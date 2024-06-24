from fastapi import APIRouter, HTTPException, Depends
import httpx
from src.utils.fetch_data import fetch_data_for_connection
from src.schemas.connection import Connection, DeleteConnectionResponse
from src.models.connection import ConnectionModel
from src.utils.database import get_db
from sqlalchemy.orm import Session
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]

connector_router = APIRouter()


# Route to create a connection
@connector_router.post(
    "/connector/create_connection", response_model=Connection, tags=["Connector"]
)
async def create_connection(
    conn: Connection, organization_id: str, db: Session = Depends(get_db)
):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections"
        payload = {
            "vendor": conn.vendor.value,
            "credentials": conn.credentials.dict(),  # Convert ConnectionType to dict
            "identifier": conn.identifier,
        }
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            connection_id = response.json()["id"]
            new_conn = ConnectionModel(
                id=connection_id,
                organization_id=organization_id,
                vendor=conn.vendor.value,
                credentials=conn.credentials.dict(),
                identifier=conn.identifier,
            )
            db.add(new_conn)
            await fetch_data_for_connection(
                x_connection_id=connection_id,
                organization_id=organization_id,
                vendor=conn.vendor.value,
            )
            db.commit()
            db.refresh(new_conn)
            detail = f"Connection created successfully for the connection_id: {connection_id} and organization_id: {organization_id}"
            return Connection(
                id=str(new_conn.id),
                vendor=new_conn.vendor,
                credentials=new_conn.credentials,
                identifier=new_conn.identifier,
                detail=detail,
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    finally:
        db.close()


@connector_router.delete(
    "/connector/delete_connection",
    response_model=DeleteConnectionResponse,
    tags=["Connector"],
)
async def delete_connection(
    connection_id: str, organization_id: str, db: Session = Depends(get_db)
):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections/{connection_id}"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
        if response.status_code == 200:
            db_conn = (
                db.query(ConnectionModel)
                .filter(ConnectionModel.id == connection_id)
                .first()
            )
            if db_conn:
                db.delete(db_conn)
                db.commit()
            return {
                "detail": f"Connection deleted successfully for the connection_id: {connection_id} and organization_id: {organization_id}"
            }
        else:
            print(response.text)
            raise HTTPException(status_code=response.status_code, detail=response.text)
    finally:
        db.close()


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
