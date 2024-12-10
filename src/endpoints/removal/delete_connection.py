from fastapi import Depends, HTTPException
import httpx
from sqlalchemy import text
from src.utils.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]


async def delete_connection_logic(
    connection_id: str, organization_id: str, db: Session = Depends(get_db)
):
    url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections/{connection_id}"
    headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}

    query = text(
        "UPDATE connections SET is_active = False, updated_at = :updated_at WHERE "
        "leen_connection_id = :leen_connection_id AND leen_organization_id = :leen_organization_id"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
        response.raise_for_status()
        db.execute(
            query,
            {
                "updated_at": datetime.now(),
                "leen_connection_id": str(connection_id),
                "leen_organization_id": str(organization_id),
            },
        )
        db.commit()
        return {
            "detail": f"Connection deleted successfully for the connection_id: {connection_id} and organization_id: {organization_id}"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
