# src/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.models.vulnerability_orm import VulnerabilityModel
from src.models.organization_orm import OrganizationModel
from src.models.connection_orm import ConnectionModel
from src.models.alerts_orm import AlertsModel
from src.models.issue_orm import IssuesModel
from src.models.activity_orm import ActivityModel
from src.models.connectors_orm import ConnectorModel

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres:5432/<database>"

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=0)
metadata = MetaData()

metadata.reflect(bind=engine)

VulnerabilityModel.metadata.create_all(bind=engine)
OrganizationModel.metadata.create_all(bind=engine)
ConnectionModel.metadata.create_all(bind=engine)
AlertsModel.metadata.create_all(bind=engine)
IssuesModel.metadata.create_all(bind=engine)
ActivityModel.metadata.create_all(bind=engine)
ConnectorModel.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
