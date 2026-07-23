"""
FastAPI backend for the AI-Powered Customer Complaint Management System.

Run with:
    uvicorn backend.main:app --reload --port 8000
(run from the project root, one level above `backend/`)
"""
import os
import uuid
from datetime import date, datetime
from typing import Dict

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database.db import Base, engine, get_db
from .database import models
from .schemas import ChatRequest, ChatResponse, ComplaintExtraction, ComplaintCreate, ComplaintUpdate, ComplaintOut
from .parsers import extract_text
from .agents.graph import complaint_graph
from .agents.duplicate_check import find_potential_duplicates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharma Complaint Management System API")

# CORS_ORIGINS env var: comma-separated list of allowed origins.
# Defaults to local dev servers. In production (Render), set this to your
# deployed frontend's URL, e.g. https://pharma-complaint-frontend.onrender.com
_cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory session store: session_id -> LangGraph state dict.
# For production, persist this in the `conversations` table instead.
SESSIONS: Dict[str, dict] = {}


def _run_turn(session_id: str, raw_text: str) -> ChatResponse:
    prior_state = SESSIONS.get(session_id, {"session_id": session_id, "extraction": {}})
    input_state = {**prior_state, "session_id": session_id, "raw_input_text": raw_text}

    result_state = complaint_graph.invoke(input_state)
    SESSIONS[session_id] = result_state

    return ChatResponse(
        session_id=session_id,
        ai_message=result_state.get("ai_message", ""),
        extraction=ComplaintExtraction(**result_state.get("extraction", {})),
        missing_fields=result_state.get("missing_fields", []),
        is_complete=result_state.get("is_complete", False),
        processing_stage=result_state.get("processing_stage", "idle"),
    )


@app.get("/")
def root():
    return {"status": "ok", "service": "pharma-complaint-management-api"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    return _run_turn(payload.session_id, payload.message)


@app.post("/upload", response_model=ChatResponse)
async def upload(session_id: str, file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit")

    try:
        text = extract_text(file.filename, contents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    saved_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(saved_path, "wb") as f:
        f.write(contents)

    return _run_turn(session_id, text)


@app.post("/complaints", response_model=ComplaintOut)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    customer = models.Customer(name=payload.customer_name, source_type=payload.complaint_source)
    product = models.Product(name=payload.product_name, strength_grade=payload.product_strength)
    db.add(customer)
    db.add(product)
    db.flush()  # get generated IDs before creating the complaint

    complaint = models.Complaint(
        customer_id=customer.id,
        product_id=product.id,
        complaint_source=payload.complaint_source,
        batch_number=payload.batch_number,
        manufacturing_date=payload.manufacturing_date,
        expiry_date=payload.expiry_date,
        quantity_affected=payload.quantity_affected,
        complaint_type=payload.complaint_type,
        complaint_date=payload.complaint_date,
        detailed_description=payload.detailed_description,
        severity=payload.severity,
        priority=payload.priority,
        risk_assessment=payload.risk_assessment,
        suggested_action=payload.suggested_action,
        corrective_action=payload.corrective_action,
        preventive_action=payload.preventive_action,
        investigation_scope=payload.investigation_scope,
        capa_priority=payload.capa_priority,
        ai_summary=payload.ai_summary,
        status=models.ComplaintStatus.PENDING,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    out = ComplaintOut(
        id=complaint.id,
        complaint_source=complaint.complaint_source,
        customer_name=customer.name,
        product_name=product.name,
        product_strength=product.strength_grade,
        batch_number=complaint.batch_number,
        manufacturing_date=complaint.manufacturing_date,
        expiry_date=complaint.expiry_date,
        quantity_affected=complaint.quantity_affected,
        complaint_type=complaint.complaint_type,
        complaint_date=complaint.complaint_date,
        detailed_description=complaint.detailed_description,
        severity=complaint.severity.value if complaint.severity else None,
        priority=complaint.priority.value if complaint.priority else None,
        risk_assessment=complaint.risk_assessment,
        suggested_action=complaint.suggested_action,
        corrective_action=complaint.corrective_action,
        preventive_action=complaint.preventive_action,
        investigation_scope=complaint.investigation_scope,
        capa_priority=complaint.capa_priority,
        ai_summary=complaint.ai_summary,
        status=complaint.status.value,
    )
    return out


@app.get("/complaints")
def list_complaints(db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "customer_name": c.customer.name if c.customer else None,
            "product_name": c.product.name if c.product else None,
            "batch_number": c.batch_number,
            "complaint_type": c.complaint_type,
            "severity": c.severity.value if c.severity else None,
            "priority": c.priority.value if c.priority else None,
            "capa_priority": c.capa_priority,
            "status": c.status.value if c.status else None,
            "ai_summary": c.ai_summary,
            "created_at": c.created_at,
        }
        for c in complaints
    ]


@app.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    c = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    duplicates = find_potential_duplicates(db, c.batch_number, c.complaint_type, c.complaint_date)

    return {
        "id": c.id,
        "customer_name": c.customer.name if c.customer else None,
        "complaint_source": c.complaint_source,
        "product_name": c.product.name if c.product else None,
        "product_strength": c.product.strength_grade if c.product else None,
        "batch_number": c.batch_number,
        "manufacturing_date": c.manufacturing_date,
        "expiry_date": c.expiry_date,
        "quantity_affected": c.quantity_affected,
        "complaint_type": c.complaint_type,
        "complaint_date": c.complaint_date,
        "detailed_description": c.detailed_description,
        "severity": c.severity.value if c.severity else None,
        "priority": c.priority.value if c.priority else None,
        "risk_assessment": c.risk_assessment,
        "suggested_action": c.suggested_action,
        "corrective_action": c.corrective_action,
        "preventive_action": c.preventive_action,
        "investigation_scope": c.investigation_scope,
        "capa_priority": c.capa_priority,
        "ai_summary": c.ai_summary,
        "status": c.status.value if c.status else None,
        "potential_duplicates": duplicates,
    }


@app.put("/complaints/{complaint_id}")
def update_complaint(complaint_id: str, payload: ComplaintUpdate, db: Session = Depends(get_db)):
    c = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if payload.status:
        c.status = payload.status
    if payload.severity:
        c.severity = payload.severity
    if payload.priority:
        c.priority = payload.priority
    if payload.detailed_description:
        c.detailed_description = payload.detailed_description
    if payload.corrective_action:
        c.corrective_action = payload.corrective_action
    if payload.preventive_action:
        c.preventive_action = payload.preventive_action
    if payload.investigation_scope:
        c.investigation_scope = payload.investigation_scope
    if payload.capa_priority:
        c.capa_priority = payload.capa_priority

    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)
    return {"id": c.id, "status": c.status.value if c.status else None}
