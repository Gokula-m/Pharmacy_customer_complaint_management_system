"""
Normalized SQLAlchemy models for the Complaint Management System.

Tables: Customers, Products, Complaints, Conversations, Attachments
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Text, Date, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from .db import Base


def gen_uuid():
    return str(uuid.uuid4())


class ComplaintStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class Severity(str, enum.Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"


class Priority(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    source_type = Column(String(100))  # Pharmacy / Hospital / Distributor / Patient etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    strength_grade = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="product")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String, primary_key=True, default=gen_uuid)

    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)

    complaint_source = Column(String(100))
    batch_number = Column(String(100), nullable=False, index=True)
    manufacturing_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    quantity_affected = Column(Integer, nullable=False)

    complaint_type = Column(String(150))
    complaint_date = Column(Date, nullable=False)
    detailed_description = Column(Text, nullable=False)

    severity = Column(SAEnum(Severity))
    priority = Column(SAEnum(Priority))
    risk_assessment = Column(Text)
    suggested_action = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    investigation_scope = Column(Text)
    capa_priority = Column(String(20))  # "Immediate" | "Standard" | "Routine"
    ai_summary = Column(Text)

    status = Column(SAEnum(ComplaintStatus), default=ComplaintStatus.PENDING)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="complaints")
    product = relationship("Product", back_populates="complaints")
    conversations = relationship("Conversation", back_populates="complaint")
    attachments = relationship("Attachment", back_populates="complaint")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_uuid)
    complaint_id = Column(String, ForeignKey("complaints.id"), nullable=True)
    session_id = Column(String, index=True, nullable=False)

    role = Column(String(20))  # 'user' or 'assistant'
    message = Column(Text)
    state_snapshot = Column(Text)  # JSON-encoded LangGraph state at this turn

    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="conversations")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String, primary_key=True, default=gen_uuid)
    complaint_id = Column(String, ForeignKey("complaints.id"), nullable=True)

    filename = Column(String(255))
    file_type = Column(String(50))
    file_path = Column(String(500))
    extracted_text = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="attachments")
