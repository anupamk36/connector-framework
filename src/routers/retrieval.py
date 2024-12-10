from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.endpoints.retrieval.list_organization import list_organizations_logic
from src.endpoints.retrieval.list_connection import list_connection_logic
from src.endpoints.retrieval.connection_status import list_connection_status_logic
from src.endpoints.retrieval.list_insights import list_insights_logic
from src.utils.database import get_db

get_router = APIRouter()


@get_router.get("/connector/list_organizations", tags=["Retrieval"])
async def list_organization():
    try:
        return await list_organizations_logic()
    except Exception as e:
        raise e


@get_router.get("/connector/list_connections", tags=["Retrieval"])
async def list_connections(organization_id: str):
    try:
        return await list_connection_logic(organization_id)
    except Exception as e:
        raise e
    
@get_router.get("/connector/list_connections_status", tags=["Retrieval"])
async def list_connection_status(organization_id: str,  db: Session = Depends(get_db)):
    try:
        return await list_connection_status_logic(organization_id, db)
    except Exception as e:
        raise e
    
@get_router.get("/connector/list_insights", tags=["Retrieval"])
async def list_insights(organization_id: str, page: int, page_size: int, db: Session = Depends(get_db)):
    try:
        return await list_insights_logic(organization_id, page, page_size, db)
    except Exception as e:
        raise e
