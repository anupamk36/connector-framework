from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from src.config.connector_config import CONNECTOR_MAPPING
from src.utils.database import SessionLocal
from sqlalchemy import text
from sqlalchemy.future import select
import configparser
import httpx
import asyncio
from typing import List
import logging

log = logging.getLogger(__name__)


fetch_router = APIRouter()

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

x_api_key = config["DEFAULT"]["x_api_key"]

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]


async def list_organization():
    try:
        url = "https://api.leen.dev/v1/provisioning/organizations"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise e


async def list_connection(organization_id: str):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise e

import logging

async def fetch_connector_data(x_connection_id: str, organization_id: str, vendor: str):
    limit = 500
    offset = 0
    total = None
    all_data = []
    base_url = ""
    config = CONNECTOR_MAPPING.get(vendor.lower())
    if config is None:
        raise ValueError(f"No base_url configuration found for {vendor} vendor")
    base_url = config["base_url"]

    while total is None or offset < total:
        url = f"{base_url}?limit={limit}&offset={offset}" 
        headers = {"X-API-KEY": x_api_key, "X-CONNECTION-ID": x_connection_id}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
            # print(f"Hitting the API endpoint: {url}")
        if response.status_code == 200:
            try:
                data = response.json()
                logging.info(f"API Response: {data}")
            except ValueError as e:
                raise ValueError(f"Failed to parse JSON response: {response.text}") from e

            if not isinstance(data, dict):
                raise ValueError(f"Invalid response data: {data}")
            
            items = data.get("items")
            if not isinstance(items, list):
                raise ValueError(f"Expected 'items' to be a list, got {type(items)}: {items}")
            
            all_data.extend(items)

            total = data.get("total")
            if total is None:
                raise ValueError(f"Missing 'total' in response data: {data}")
            
            offset += limit
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    for item in all_data:
        item["organization_id"] = organization_id
        item["connection_id"] = x_connection_id
    return all_data, vendor


async def insert_data_to_postgres(all_data: List[dict], vendor: str):
    records = []
    log.debug(
        f"Inserting data into the database, total records: {len(all_data)}, by {vendor} vendor"
    )
    db = SessionLocal()
    try:
        new_records = []
        config = CONNECTOR_MAPPING.get(vendor.lower())
        if config is None:
            raise ValueError(f"No ORM configuration found for {vendor} vendor")
        ORMModel = config["model"]
        log.debug(f"Using ORM model: {ORMModel.__name__} for vendor: {vendor}")

        for record_data in all_data:
            log.debug(f"Processing record data: {record_data}")
            db.execute(text("LOCK TABLE %s IN EXCLUSIVE MODE" % ORMModel.__tablename__))
            log.debug(f"Locked table: {ORMModel.__tablename__}")

            # Check if the record already exists
            record = db.query(ORMModel).filter(ORMModel.id == record_data["id"]).first()
            if record:
                log.debug(f"Record found: {record}, updating existing record.")
                for key, value in record_data.items():
                    log.debug(f"Updating field: {key} with value: {value}")
                    setattr(record, key, value)
            else:
                log.debug(f"No existing record found, adding new record: {record_data}")
                new_records.append(ORMModel(**record_data))
                records.append(record_data)

        if new_records:
            db.add_all(new_records)

        db.commit()
        log.debug("Database commit successful")

    except Exception as exc:
        db.rollback()
        log.error(f"Exception occurred: {exc}")
        raise HTTPException(
            status_code=500, detail=str(exc)
        )  # Raising HTTPException to propagate error

    finally:
        db.close()
        log.debug("Database connection closed")


# @fetch_router.get(
#     "/fetch_data_for_connection",
#     tags=["Fetch Data"],
#     description="Fetch data from the API and insert into the database for a specific connection",
# )
# async def fetch_data_for_connection(
#     x_connection_id: str, organization_id: str, vendor: str
# ):
#     vulnerabilities = await fetch_connector_data(
#         x_connection_id, organization_id, vendor
#     )
#     for vuln in vulnerabilities:
#         await insert_data_to_postgres(vuln, vendor=vendor)


@fetch_router.get(
    "/fetch_data",
    tags=["Fetch Data"],
    description="Fetch data from the API and insert into the database",
)
async def fetch_data():
    organizations = await list_organization()
    tasks = []
    for org in organizations["items"]:
        connections = await list_connection(org["id"])
        for conn in connections["items"]:
            tasks.append(fetch_connector_data(conn["id"], org["id"], conn["vendor"]))
    vulnerabilities = await asyncio.gather(*tasks)
    for vuln, vendor in vulnerabilities:
        await insert_data_to_postgres(vuln, vendor=vendor)

async def fetch_data_and_insert_for_organization(organization_id: str, is_refresh: bool = False):
    if not is_refresh:
        await asyncio.sleep(30)
    tasks = []
    connections = await list_connection(organization_id)
    for conn in connections["items"]:
        tasks.append(fetch_connector_data(conn["id"], organization_id, conn["vendor"]))
    vulnerabilities = await asyncio.gather(*tasks)
    for vuln, vendor in vulnerabilities:
        await insert_data_to_postgres(vuln, vendor=vendor)



@fetch_router.get(
    "/fetch_data_for_organization",
    tags=["Fetch Data"],
    description="Fetch data from the API and insert into the database for specific organization",
)
async def fetch_data_for_organization(organization_id: str, background_tasks: BackgroundTasks, is_refresh: bool = False):

    background_tasks.add_task(fetch_data_and_insert_for_organization, organization_id, is_refresh)
    if is_refresh:
        return {"message": "Data fetching started in the background, refreshing the data"}
    return {"message": "Data fetching started in the background"}

async def fetch_and_insert_data(
    x_connection_id: str, organization_id: str, vendor: str
):
    vulnerabilities = await fetch_connector_data(
        x_connection_id, organization_id, vendor
    )
    for vuln in vulnerabilities:
        await insert_data_to_postgres(vuln, vendor=vendor)


# @fetch_router.get(
#     "/fetch_data",
#     tags=["Fetch Data"],
#     description="Fetch data from the API and insert into the database in background",
# )
# async def fetch_data(background_tasks: BackgroundTasks):
#     organizations = await list_organization()
#     for org in organizations["items"]:
#         connections = await list_connection(org["id"])
#         for conn in connections["items"]:
#             background_tasks.add_task(
#                 fetch_and_insert_data, conn["id"], org["id"], conn["vendor"]
#             )
#     return {"message": "Data fetching and insertion started"}
