from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ConnectorModel(Base):
    __tablename__ = "connectors"

    id = Column(Integer, Sequence("connector_id_seq"), primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Connector name (e.g., "qualys")
    base_url = Column(String)  # Base URL for the connector
    model_name = Column(String)  # Name of the model (e.g., "VulnerabilityModel")
    description = Column(String)
