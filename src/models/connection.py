from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ConnectionModel(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    identifier = Column(String)
    organization_id = Column(String)
    vendor = Column(String)
    credentials = Column(JSON)
