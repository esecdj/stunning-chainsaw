# app/models.py
from typing import List
import uuid
from sqlalchemy import String, Boolean, Enum, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import enum

from models.base import Base


class CustomerStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name: Mapped[str] = mapped_column(String, nullable=True)
    customer_contact: Mapped[str] = mapped_column(String, nullable=True)
    customer_address: Mapped[str] = mapped_column(String, nullable=True)
    customer_city: Mapped[str] = mapped_column(String, nullable=True)
    customer_state: Mapped[str] = mapped_column(String, nullable=True)
    customer_email: Mapped[str] = mapped_column(String, nullable=False)
    customer_company_name: Mapped[str] = mapped_column(String, nullable=True)
    customer_country: Mapped[str] = mapped_column(String, nullable=True)
    customer_plan_id: Mapped[str] = mapped_column(String, nullable=True)
    customer_expiry_date: Mapped[int] = mapped_column(Integer, nullable=True)
    customer_logo: Mapped[str] = mapped_column(String, nullable=True)
    customer_rejection_reason: Mapped[str] = mapped_column(String, nullable=True)
    customer_status: Mapped[CustomerStatus] = mapped_column(Enum(CustomerStatus), default=CustomerStatus.UNVERIFIED)
    role: Mapped[str] = mapped_column(String, nullable=True)
    customer_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    assigned_consultant_ids: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    customer_verification_token: Mapped[str] = mapped_column(String, nullable=True)
    customer_verification_token_expiry: Mapped[int] = mapped_column(Integer, nullable=True)
    customer_configuration_id: Mapped[str] = mapped_column(String, nullable=True)
    customer_created_at: Mapped[int] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=True)
    cloud_infrastructure: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    cnap_platforms: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    remediation_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    selected_plan: Mapped[str] = mapped_column(String, nullable=True)
    selected_plan_id: Mapped[str] = mapped_column(String, nullable=True)
    selected_plan_expiry: Mapped[int] = mapped_column(Integer, nullable=True)
    selected_plan_start_date: Mapped[int] = mapped_column(Integer, nullable=True)
    selected_plan_end_date: Mapped[int] = mapped_column(Integer, nullable=True)
    selected_plan_status: Mapped[str] = mapped_column(String, nullable=True)
    is_mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str] = mapped_column(String, nullable=True)
    otp: Mapped[str] = mapped_column(String, nullable=True)
    otp_expires_at: Mapped[int] = mapped_column(Integer, nullable=True)
