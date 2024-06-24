from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrganizationModel(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True)
    identifier = Column(String, unique=True)
    name = Column(String)
    encrypted_name = Column(String)
