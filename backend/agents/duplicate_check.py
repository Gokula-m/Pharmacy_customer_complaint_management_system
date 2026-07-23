"""
Bonus feature: Duplicate Complaint Detection.

Simple, explainable heuristic (no extra LLM call needed) — flags complaints against the same
batch number with an overlapping/similar complaint type raised recently, so QA can spot a
trending batch issue instead of treating every report as isolated.
"""
from datetime import timedelta
from sqlalchemy.orm import Session

from ..database.models import Complaint


def find_potential_duplicates(db: Session, batch_number: str, complaint_type: str,
                               complaint_date, window_days: int = 30, limit: int = 5):
    if not batch_number:
        return []

    window_start = complaint_date - timedelta(days=window_days)
    query = (
        db.query(Complaint)
        .filter(Complaint.batch_number == batch_number)
        .filter(Complaint.complaint_date >= window_start)
        .order_by(Complaint.complaint_date.desc())
        .limit(limit)
    )
    candidates = query.all()

    results = []
    for c in candidates:
        same_type = (complaint_type or "").strip().lower() == (c.complaint_type or "").strip().lower()
        results.append({
            "complaint_id": c.id,
            "complaint_date": str(c.complaint_date),
            "complaint_type": c.complaint_type,
            "same_type": same_type,
        })
    return results
