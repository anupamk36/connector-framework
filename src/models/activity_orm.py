from enum import Enum
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from uuid import uuid4
from sqlalchemy_utils import ChoiceType

Base = declarative_base()


# Step 1 & 2: Define the enum class for activity types
class ActivityType(Enum):
    CREATE_ORGANIZATION = "CREATE_ORGANIZATION"
    CREATE_ORGANIZATION_FAILED = "CREATE_ORGANIZATION_FAILED"
    UPDATE_ORGANIZATION = "UPDATE_ORGANIZATION"
    CREATE_CONNECTION = "CREATE_CONNECTION"
    CREATE_CONNECTION_TOKEN = "CREATE_CONNECTION_TOKEN"
    UPDATE_CONNECTION = "UPDATE_CONNECTION"
    DELETE_CONNECTION = "DELETE_CONNECTION"


class ActivityModel(Base):
    __tablename__ = "activity"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    activity_type = Column(ChoiceType(ActivityType, impl=String()))
    response = Column(JSON)
    httpStatus = Column(String)
    url = Column(String, default="")
    leen_organization_id = Column(String)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(String, default="platform")
