from fastapi import APIRouter, Depends
from src.endpoints.removal.delete_connection import delete_connection_logic
from src.schemas.connection import DeleteConnectionResponse
from src.utils.database import get_db
from sqlalchemy.orm import Session

removal_router = APIRouter()


@removal_router.delete(
    "/connector/delete_connection",
    response_model=DeleteConnectionResponse,
    tags=["Removal"],
)
async def delete_connection(
    connection_id: str, organization_id: str, db: Session = Depends(get_db)
):
    try:
        return await delete_connection_logic(connection_id, organization_id, db)
    except Exception as e:
        raise e
