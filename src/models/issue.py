from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class IssuesModel(Base):
    __tablename__ = "issues"
    connection_id = Column(UUID(as_uuid=True))
    organization_id = Column(UUID(as_uuid=True))
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    code_repo = Column(String)
    project_file_path = Column(String)
    vendor = Column(String)
    vendor_id = Column(String)
    name = Column(String)
    package_name = Column(String)
    package_version = Column(String)
    severity = Column(String)
    platform = Column(String)
    package_manager = Column(String)
    publication_time = Column(DateTime)
    is_patchable = Column(Boolean)
    type = Column(String)
    description = Column(String)
    vulnerability_identifiers = Column(JSON)
    cvss_score = Column(Integer)
    state = Column(String)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    kb_url = Column(String)
