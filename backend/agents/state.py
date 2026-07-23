"""
Shared state object passed between LangGraph nodes.
"""
from typing import TypedDict, Optional, List


class ComplaintState(TypedDict, total=False):
    session_id: str
    raw_input_text: str          # latest user message / uploaded doc text
    extraction: dict             # accumulated ComplaintExtraction fields
    missing_fields: List[str]
    is_complete: bool
    ai_message: str              # message to show the user this turn
    processing_stage: str        # "extracting" | "awaiting_info" | "reasoning" | "done"
    severity: Optional[str]
    priority: Optional[str]
    risk_assessment: Optional[str]
    suggested_action: Optional[str]
    corrective_action: Optional[str]
    preventive_action: Optional[str]
    investigation_scope: Optional[str]
    capa_priority: Optional[str]
    ai_summary: Optional[str]
