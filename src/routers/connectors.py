from fastapi import APIRouter, HTTPException, Depends
import httpx
import asyncio
from sqlalchemy import text
from src.utils.fetch_data import fetch_data_for_connection
from src.endpoints.creation.create_connection import create_connection_logic
from src.schemas.connection import (
    Connection,
    DeleteConnectionResponse,
    CreateConnectionResponse,
)
from src.models.connection_orm import ConnectionModel
from src.utils.database import get_db
from src.endpoints.creation.connection_invite_token import (
    create_connection_invite_token_logic,
)
from sqlalchemy.orm import Session
from datetime import datetime
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]

connector_router = APIRouter()

# # Route to create invite token for a connection
# @connector_router.post("/connector/create_connection_invite_token", tags=["Connector"])
# async def connection_invite_token(organization_id: str, vendor: str):
#     try:
#         return await create_connection_invite_token_logic(organization_id, vendor)
#     except Exception as e:
#         raise e


@connector_router.get("/connector/list_connections", tags=["Connector"])
async def list_connection(organization_id: str):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise e


# An API endpoint to fetch the status of a connection:
# It will query the connection table and check if is_active is True or False
# @connector_router.get("/connector/connection_status", tags=["Connector"])
# async def connection_status(leen_connection_id: str, db: Session = Depends(get_db)):
#     try:
#         db_conn = db.query(ConnectionModel).filter(ConnectionModel.leen_connection_id == leen_connection_id).first()
#         if db_conn:
#             return {"is_active": db_conn.is_active}
#         else:
#             raise HTTPException(status_code=404, detail="Connection not found")
#     finally:
#         db.close()
