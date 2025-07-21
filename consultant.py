import uuid
import enum
from sqlalchemy import String, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base

class ConsultantRole(str, enum.Enum):
    CONSULTANT = "CONSULTANT"
    ADMIN = "ADMIN"

class Consultant(Base):
    __tablename__ = "consultants"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    azure_id: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    mail: Mapped[str] = mapped_column(String, nullable=False)
    mobile_phone: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[ConsultantRole] = mapped_column(Enum(ConsultantRole), nullable=False)
