"""
LangGraph node functions. Each takes the ComplaintState dict and returns the updates to merge.
"""
import json

from .llm import call_llm, call_llm_json, FAST_MODEL, REASONING_MODEL
from .state import ComplaintState
from ..prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE
from ..prompts.completeness_prompt import COMPLETENESS_SYSTEM_PROMPT, COMPLETENESS_USER_TEMPLATE
from ..prompts.qms_prompt import QMS_SYSTEM_PROMPT, QMS_USER_TEMPLATE
from ..prompts.capa_prompt import CAPA_SYSTEM_PROMPT, CAPA_USER_TEMPLATE
from ..prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_TEMPLATE
from ..schemas import MANDATORY_FIELDS

FIELD_LABELS = {
    "customer_name": "customer/reporting entity name",
    "product_name": "product name",
    "batch_number": "batch/lot number",
    "manufacturing_date": "manufacturing date",
    "expiry_date": "expiry date",
    "quantity_affected": "quantity affected",
    "complaint_type": "complaint type",
    "detailed_description": "a detailed description of the issue",
}


def extraction_node(state: ComplaintState) -> dict:
    """Information Extraction Agent — merges new text into the running extraction JSON."""
    existing = state.get("extraction", {}) or {}
    user_prompt = EXTRACTION_USER_TEMPLATE.format(
        existing_json=json.dumps(existing, indent=2),
        user_text=state.get("raw_input_text", ""),
    )
    merged = call_llm_json(EXTRACTION_SYSTEM_PROMPT, user_prompt, model=FAST_MODEL)
    # Never let the LLM silently drop a previously-known value with null
    for k, v in existing.items():
        if (v not in (None, "", "null")) and not merged.get(k):
            merged[k] = v
    return {"extraction": merged, "processing_stage": "extracting"}


def completeness_node(state: ComplaintState) -> dict:
    """Completeness Checker Agent — decides if we can proceed or must ask the user for more."""
    extraction = state.get("extraction", {}) or {}
    missing = [f for f in MANDATORY_FIELDS if not extraction.get(f)]

    if not missing:
        return {"missing_fields": [], "is_complete": True, "processing_stage": "reasoning"}

    user_prompt = COMPLETENESS_USER_TEMPLATE.format(extraction_json=json.dumps(extraction, indent=2))
    question = call_llm(COMPLETENESS_SYSTEM_PROMPT, user_prompt, model=FAST_MODEL, temperature=0.3)

    if question.strip().upper() == "COMPLETE":
        # Safety net disagreement between rule-check and LLM: trust the rule-check (missing is non-empty)
        labels = ", ".join(FIELD_LABELS.get(f, f) for f in missing)
        question = f"Could you also share the {labels}?"

    return {
        "missing_fields": missing,
        "is_complete": False,
        "ai_message": question,
        "processing_stage": "awaiting_info",
    }


def qms_reasoning_node(state: ComplaintState) -> dict:
    """QMS Reasoning Agent — determines severity, priority, risk assessment, suggested action."""
    extraction = state.get("extraction", {}) or {}
    user_prompt = QMS_USER_TEMPLATE.format(extraction_json=json.dumps(extraction, indent=2))
    result = call_llm_json(QMS_SYSTEM_PROMPT, user_prompt, model=REASONING_MODEL)

    extraction["severity"] = result.get("severity")
    extraction["priority"] = result.get("priority")
    extraction["risk_assessment"] = result.get("risk_assessment")
    extraction["suggested_action"] = result.get("suggested_action")

    return {
        "extraction": extraction,
        "severity": result.get("severity"),
        "priority": result.get("priority"),
        "risk_assessment": result.get("risk_assessment"),
        "suggested_action": result.get("suggested_action"),
    }


def capa_recommendation_node(state: ComplaintState) -> dict:
    """CAPA Recommendation Agent — proposes corrective/preventive actions and investigation scope,
    building on the severity/risk assessment the QMS reasoning agent already produced."""
    extraction = state.get("extraction", {}) or {}
    user_prompt = CAPA_USER_TEMPLATE.format(extraction_json=json.dumps(extraction, indent=2))
    result = call_llm_json(CAPA_SYSTEM_PROMPT, user_prompt, model=REASONING_MODEL)

    extraction["corrective_action"] = result.get("corrective_action")
    extraction["preventive_action"] = result.get("preventive_action")
    extraction["investigation_scope"] = result.get("investigation_scope")
    extraction["capa_priority"] = result.get("capa_priority")

    return {
        "extraction": extraction,
        "corrective_action": result.get("corrective_action"),
        "preventive_action": result.get("preventive_action"),
        "investigation_scope": result.get("investigation_scope"),
        "capa_priority": result.get("capa_priority"),
    }


def summary_node(state: ComplaintState) -> dict:
    """Complaint Summary Agent — produces a professional QA summary."""
    extraction = state.get("extraction", {}) or {}
    user_prompt = SUMMARY_USER_TEMPLATE.format(extraction_json=json.dumps(extraction, indent=2))
    summary = call_llm(SUMMARY_SYSTEM_PROMPT, user_prompt, model=REASONING_MODEL, temperature=0.3)

    ai_message = (
        "The information is parsed successfully. I extracted the necessary information to make "
        "a note and populated the complaint form — please review the Severity, Priority, and Risk "
        "Assessment suggestions before saving."
    )
    return {
        "ai_summary": summary,
        "ai_message": ai_message,
        "processing_stage": "done",
    }
