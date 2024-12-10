from pydantic import BaseModel, Field
from typing import Union
from enum import Enum
from src.schemas.authentication import (
    OAuthAuthentication,
    BasicAuthentication,
    ApiKeyAuthentication,
    BearerTokenAuthentication,
)


class ConnectionType(Enum):
    TENABLE = "TENABLE"
    QUALYS = "QUALYS"
    SNYK = "SNYK"
    CROWDSTRIKE = "CROWDSTRIKE"
    MS_DEFENDER_ENDPOINT = "MS_DEFENDER_ENDPOINT"
    TYPSENTINELONEE = "SENTINELONE"
    SEMGREP = "SEMGREP"
    INSIGHTVM = "INSIGHTVM"


class Connection(BaseModel):
    connection_id: str = Field(None, alias="id")
    vendor: ConnectionType
    credentials: Union[
        OAuthAuthentication,
        BasicAuthentication,
        ApiKeyAuthentication,
        BearerTokenAuthentication,
    ]
    identifier: str
    detail: str = Field(None)

    class Config:
        from_attributes = True


class DeleteConnectionResponse(BaseModel):
    detail: str


class CreateConnectionResponse(BaseModel):
    connection_id: str
    message: str
    identifier: str
    vendor: str
    is_active: bool
