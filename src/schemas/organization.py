from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


# Define models for request bodies
class Organization(BaseModel):
    identifier: str
    name: str


class OrganizationResponseModel(BaseModel):
    leen_organization_id: str
    identifier: str
    name: str
    message: str
