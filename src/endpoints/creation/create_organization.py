from fastapi import Depends, HTTPException
import httpx
import uuid
from src.models.organization_orm import OrganizationModel
from src.models.activity_orm import ActivityModel, ActivityType
from src.schemas.organization import Organization
from src.utils.database import get_db
from sqlalchemy.orm import Session
import configparser
import hashlib
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")

x_api_key = config["DEFAULT"]["x_api_key"]


async def create_organization_logic(org: Organization, db: Session = Depends(get_db)):
    # Check if the organization already exists by identifier
    existing_org = (
        db.query(OrganizationModel)
        .filter(OrganizationModel.identifier == org.identifier)
        .first()
    )

    if existing_org:
        if org.name != existing_org.name:
            # Update the existing organization's name
            encrypted_name = hashlib.sha256(org.name.encode()).hexdigest()
            existing_org.name = org.name
            existing_org.encrypted_name = encrypted_name
            existing_org.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_org)

            # Log activity for updating organization
            activity = ActivityModel(
                activity_type=ActivityType.UPDATE_ORGANIZATION,
                response={"message": "Organization name updated successfully"},
                httpStatus="200",
                url="",
                leen_organization_id=str(existing_org.leen_organization_id),
                created_at=datetime.utcnow(),
                created_by="platform",
            )
            db.add(activity)
            db.commit()

        return {
            "identifier": existing_org.identifier,
            "name": existing_org.name,
            "leen_organization_id": str(existing_org.leen_organization_id),
            "message": f"Organization for {org.identifier} already exists",
        }

    try:
        encrypted_name = hashlib.sha256(org.name.encode()).hexdigest()
        url = "https://api.leen.dev/v1/provisioning/organizations"
        payload = {"name": encrypted_name, "identifier": org.identifier}
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            leen_organization_id = response.json()["id"]
            new_org = OrganizationModel(
                id=uuid.uuid4(),
                identifier=org.identifier,
                leen_organization_id=leen_organization_id,
                name=org.name,
                encrypted_name=encrypted_name,
                is_active=True,
            )
            db.add(new_org)
            db.commit()
            db.refresh(new_org)

            # Set activity details for success case
            activity_type = ActivityType.CREATE_ORGANIZATION
            activity_response = response.json()
            activity_http_status = response.status_code
            activity_leen_organization_id = leen_organization_id

            return {
                "identifier": new_org.identifier,
                "name": new_org.name,
                "leen_organization_id": leen_organization_id,
                "message": "Organization created successfully",
            }
        else:
            # Set activity details for failure case
            activity_type = ActivityType.CREATE_ORGANIZATION_FAILED
            activity_response = {
                "response": f"{response.json()}",
                "identifier": org.identifier,
                "name": org.name,
            }
            activity_http_status = response.status_code
            activity_leen_organization_id = "N/A"

            raise HTTPException(status_code=response.status_code, detail=response.text)
    finally:
        # Log activity for both success and failure cases
        activity = ActivityModel(
            activity_type=activity_type,
            response=activity_response,
            httpStatus=activity_http_status,
            url=url,
            leen_organization_id=activity_leen_organization_id,
            created_at=datetime.utcnow(),
            created_by="platform",
        )
        db.add(activity)
        db.commit()
        db.close()
