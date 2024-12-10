"""
This module contains the logic for creating connection invite tokens.
It is used to create a connection invite token for creating connections.
"""

import configparser
from datetime import datetime
from typing import Optional
import httpx
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.models.activity_orm import ActivityModel, ActivityType

from src.utils.database import get_db

config = configparser.ConfigParser()
config.read("config.ini")

x_api_key = config["DEFAULT"]["x_api_key"]


async def create_connection_invite_token_logic(
    organization_id: str, vendor: str, identifier: str, db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Create a connection invite token for a given organization.

    Args:
        organization_id (str): The ID of the organization.
        vendor (str): The vendor name.
        identifier (str): The identifier for the connection.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict or None: The response JSON if the request is successful, None otherwise.

    Raises:
        HTTPException: If the request fails with a non-200 status code.
    """
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connection-invite-tokens"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        payload = {"vendor": vendor, "identifier": identifier}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        activity_data = ActivityModel(
            activity_type=ActivityType.CREATE_CONNECTION_TOKEN,
            response=response.json(),
            httpStatus=str(response.status_code),
            url=url,
            leen_organization_id=organization_id,
            created_at=datetime.now(),
            created_by="platform",
        )

        db.add(activity_data)
        db.commit()

        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()
