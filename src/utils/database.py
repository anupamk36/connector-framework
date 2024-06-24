# src/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.models.vulnerability import VulnerabilityModel
from src.models.organization import OrganizationModel
from src.models.connection import ConnectionModel
from src.models.alerts import AlertsModel
from src.models.issue import IssuesModel

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=0)
metadata = MetaData()

metadata.reflect(bind=engine)

VulnerabilityModel.metadata.create_all(bind=engine)
OrganizationModel.metadata.create_all(bind=engine)
ConnectionModel.metadata.create_all(bind=engine)
AlertsModel.metadata.create_all(bind=engine)
IssuesModel.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
