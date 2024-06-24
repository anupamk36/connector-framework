from fastapi import APIRouter, HTTPException, Depends
import httpx
from src.models.organization import OrganizationModel
from src.schemas.organization import Organization
from src.schemas.connection import Connection
from src.models.connection import ConnectionModel
from src.utils.crypto import Crypto
from src.utils.database import get_db
from sqlalchemy.orm import Session
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

crypto = Crypto("connector_fernet_key", "us-west-2")
# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]

router = APIRouter()


@router.post(
    "/provisioning/create_organization",
    response_model=Organization,
    tags=["Provisioning"],
)
async def create_organization(org: Organization, db: Session = Depends(get_db)):
    try:
        encrypted_name = crypto.encrypt(org.name)
        url = "https://api.leen.dev/v1/provisioning/organizations"
        payload = {"name": encrypted_name, "identifier": org.identifier}
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            id = response.json()["id"]
            new_org = OrganizationModel(
                id=id,
                identifier=org.identifier,
                name=org.name,
                encrypted_name=encrypted_name,
            )
            db.add(new_org)
            db.commit()
            db.refresh(new_org)
            return new_org
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    finally:
        db.close()


@router.get("/provisioning/list_organizations", tags=["Provisioning"])
async def list_organization():
    try:
        url = "https://api.leen.dev/v1/provisioning/organizations"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise e


# @router.post("/provisioning/create_connection", tags=["Provisioning"])
async def create_connection(
    conn: Connection, organization_id: str, db: Session = Depends(get_db)
):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections"
        payload = {
            "vendor": conn.vendor.value,
            "credentials": conn.credentials.dict(),  # Convert ConnectionType to dict
        }
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            id = response.json()["id"]
            new_conn = ConnectionModel(
                id=id, vendor=conn.vendor, credentials=conn.credentials
            )
            db.add(new_conn)
            db.commit()
            db.refresh(new_conn)
            return new_conn
        else:
            print(response.text)
            raise HTTPException(status_code=response.status_code, detail=response.text)
    finally:
        db.close()
