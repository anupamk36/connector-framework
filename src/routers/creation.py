from fastapi import APIRouter, Depends, BackgroundTasks
from src.endpoints.creation.create_organization import create_organization_logic
from src.endpoints.creation.create_connection import create_connection_logic
from src.endpoints.creation.connection_invite_token import (
    create_connection_invite_token_logic,
)
from src.endpoints.creation.create_connection_onramp import (
    create_connection_onramp_logic,
)
from src.schemas.organization import Organization, OrganizationResponseModel
from src.schemas.connection import Connection, CreateConnectionResponse
from src.schemas.connection_onramp import CreateConnectionResponseOnRamp, Activity
from src.utils.database import get_db
from sqlalchemy.orm import Session
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]

post_router = APIRouter()


# Route to create a connection
@post_router.post(
    "/connector/create_connection",
    response_model=CreateConnectionResponse,
    tags=["Connector"],
)
async def create_connection(
    background_tasks: BackgroundTasks,
    conn: Connection,
    organization_id: str,
    db: Session = Depends(get_db),
):
    try:
        return await create_connection_logic(
            background_tasks, conn, organization_id, db
        )
    except Exception as e:
        raise e


@post_router.post(
    "/connector/create_connection_onramp",
    tags=["Connector"],
    response_model=CreateConnectionResponseOnRamp,
)
async def create_connection_onramp(
    background_tasks: BackgroundTasks, response: Activity, db: Session = Depends(get_db)
):
    try:
        return await create_connection_onramp_logic(background_tasks, response, db)
    except Exception as e:
        raise e


@post_router.post(
    "/connector/create_organization",
    response_model=OrganizationResponseModel,
    tags=["Provisioning"],
)
async def create_organization(org: Organization, db: Session = Depends(get_db)):
    try:
        return await create_organization_logic(org, db)
    except Exception as e:
        raise


# Route to create invite token for a connection
@post_router.post("/connector/create_connection_invite_token", tags=["Provisioning"])
async def create_connection_invite_token(
    organization_id: str, vendor: str, identifier: str, db: Session = Depends(get_db)
):
    try:
        return await create_connection_invite_token_logic(
            organization_id, vendor, identifier, db
        )
    except Exception as e:
        raise e
