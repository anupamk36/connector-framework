from fastapi import Depends, HTTPException, BackgroundTasks
from src.schemas.connection import Connection, CreateConnectionResponse
from src.models.connection_orm import ConnectionModel
from src.utils.database import get_db
from src.utils.fetch_data import fetch_data_for_organization
from sqlalchemy.orm import Session
import httpx
import uuid
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]


async def create_connection_logic(
    background_tasks: BackgroundTasks,
    conn: Connection,
    organization_id: str,
    db: Session = Depends(get_db),
):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections"
        payload = {
            "vendor": conn.vendor.value,
            "credentials": conn.credentials.dict(),
            "identifier": conn.identifier,
        }
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            connection_id = response.json()["id"]
            new_conn = ConnectionModel(
                id=uuid.uuid4(),
                identifier=conn.identifier,
                vendor=conn.vendor.value,
                leen_connection_id=connection_id,
                leen_organization_id=organization_id,
                is_active=True,
                created_at=None,
                updated_at=None,
                created_by=None,
                updated_by=None,
            )
            db.add(new_conn)
            db.commit()
            db.refresh(new_conn)
            detail = f"Connection created successfully for the connection_id: {connection_id} and organization_id: {organization_id}"

            # Add fetch_data_for_organization to background tasks
            background_tasks.add_task(
                fetch_data_for_organization, organization_id=organization_id
            )

            return CreateConnectionResponse(
                connection_id=str(new_conn.leen_connection_id),
                message=detail,
                identifier=conn.identifier,
                vendor=new_conn.vendor,
                is_active=new_conn.is_active,
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise e
