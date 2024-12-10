from sqlalchemy import Column, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True)
    identifier = Column(String)
    leen_organization_id = Column(UUID(as_uuid=True))
    name = Column(String)
    encrypted_name = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    created_by = Column(String, default="platform")
    updated_by = Column(String, default="platform")
