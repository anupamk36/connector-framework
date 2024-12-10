from pydantic import BaseModel
from typing import Optional


class ConnectionData(BaseModel):
    id: str
    identifier: Optional[str]
    vendor: str
    refresh_interval_secs: int
    timeout_secs: int
    organization_id: str
    oauth2_authorize_url: Optional[str]
    is_active: bool


class Activity(BaseModel):
    data: ConnectionData
    httpStatus: int
    message: str


class CreateConnectionResponseOnRamp(BaseModel):
    connection_id: str
    message: str
    identifier: Optional[str]
    vendor: str
    is_active: bool
