# app/models/email_models.py

import uuid
from typing import Optional
from sqlalchemy import String, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
import enum


class EmailStatus(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    QUEUED = "queued"


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # relationship
    email_logs: Mapped[Optional[list["EmailLog"]]] = relationship("EmailLog", back_populates="template")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_template_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("email_templates.id"))
    recipient_email: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[EmailStatus] = mapped_column(Enum(EmailStatus), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sent_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    failed_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    retries: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # relationship
    template: Mapped[EmailTemplate] = relationship("EmailTemplate", back_populates="email_logs")
