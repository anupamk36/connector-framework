from pydantic import BaseModel


# Define models for request bodies
class Organization(BaseModel):
    identifier: str
    name: str
