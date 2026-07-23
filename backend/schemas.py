"""
Pydantic schemas shared by the FastAPI endpoints and the LangGraph agent state.
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, field_validator


class ComplaintExtraction(BaseModel):
    """Structured output the Information Extraction Agent must produce."""
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None  # kept as str until validated/parsed
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    detailed_description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    risk_assessment: Optional[str] = None
    suggested_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    investigation_scope: Optional[str] = None
    capa_priority: Optional[str] = None


MANDATORY_FIELDS = [
    "customer_name",
    "product_name",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "quantity_affected",
    "complaint_type",
    "detailed_description",
]


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    ai_message: str
    extraction: ComplaintExtraction
    missing_fields: List[str] = []
    is_complete: bool = False
    processing_stage: str = "idle"


class ComplaintCreate(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: str
    product_name: str
    product_strength: Optional[str] = None
    batch_number: str
    manufacturing_date: date
    expiry_date: date
    quantity_affected: int
    complaint_type: Optional[str] = None
    complaint_date: date
    detailed_description: str
    severity: Optional[str] = None
    priority: Optional[str] = None
    risk_assessment: Optional[str] = None
    suggested_action: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    investigation_scope: Optional[str] = None
    capa_priority: Optional[str] = None
    ai_summary: Optional[str] = None

    @field_validator("expiry_date")
    @classmethod
    def expiry_after_mfg(cls, v, info):
        mfg = info.data.get("manufacturing_date")
        if mfg and v <= mfg:
            raise ValueError("Expiry Date must be later than Manufacturing Date")
        return v

    @field_validator("complaint_date")
    @classmethod
    def complaint_not_future(cls, v):
        if v > date.today():
            raise ValueError("Complaint Date cannot be in the future")
        return v

    @field_validator("quantity_affected")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity Affected must be a positive integer")
        return v


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    detailed_description: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    investigation_scope: Optional[str] = None
    capa_priority: Optional[str] = None


class ComplaintOut(ComplaintCreate):
    id: str
    status: str

    class Config:
        from_attributes = True
