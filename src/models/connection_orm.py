from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ConnectionModel(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    identifier = Column(String, index=True)  # Consider if this should be indexed
    vendor = Column(String, index=True)  # Consider if this should be indexed
    leen_connection_id = Column(UUID(as_uuid=True), index=True)
    leen_organization_id = Column(UUID(as_uuid=True), index=True)
    is_active = Column(Boolean, default=True)  # Assuming default active status
    refresh_interval = Column(Integer)
    timeout = Column(Integer)
    oauth2_authorize_url = Column(String)
    created_at = Column(DateTime, default=func.now())  # Use func.now() for the default
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now()
    )  # Automatically update on modification
    created_by = Column(String, default="platform")
    updated_by = Column(String, default="platform")
