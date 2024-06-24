from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AlertsModel(Base):
    __tablename__ = "alerts"
    connection_id = Column(UUID(as_uuid=True))
    organization_id = Column(UUID(as_uuid=True))
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    vendor_id = Column(String)
    title = Column(String)
    description = Column(String)
    assigned_user = Column(String)
    severity = Column(String)
    vendor_severity = Column(String)
    status = Column(String)
    vendor_status = Column(String)
    first_event_time = Column(DateTime)
    last_event_time = Column(DateTime)
    resolved_time = Column(DateTime)
    vendor = Column(String)
    pid = Column(String)
    process_created_at = Column(DateTime)
    process_filename = Column(String)
    process_command_line = Column(String)
    process_filepath = Column(String)
    process_sha1 = Column(String)
    process_sha256 = Column(String)
    process_md5 = Column(String)
    parent_pid = Column(String)
    user_name = Column(String)
    windows_sid = Column(String)
    active_directory_user_id = Column(String)
    active_directory_domain = Column(String)
    device = Column(JSON)
    mitre = Column(JSON)
