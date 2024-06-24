from pydantic import BaseModel, Field


class Authentication(BaseModel):
    pass


class OAuthAuthentication(Authentication):
    client_key: str = Field(..., description="The client ID for OAuth")
    secret_key: str = Field(..., description="The client secret for OAuth")
    token_url: str = Field(..., description="The token URL for OAuth")


class BasicAuthentication(Authentication):
    username: str = Field(..., description="The username for basic authentication")
    password: str = Field(..., description="The password for basic authentication")
    url: str = Field(..., description="The URL for basic authentication")


class ApiKeyAuthentication(Authentication):
    api_key: str = Field(..., description="The API key for API key authentication")


class BearerTokenAuthentication(Authentication):
    bearer_token: str = Field(
        ..., description="The bearer token for bearer token authentication"
    )
