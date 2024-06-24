from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from src.config.connector_config import CONNECTOR_MAPPING
from src.utils.database import SessionLocal
from sqlalchemy import text
import configparser
import httpx
import asyncio
from typing import List
import pytz
from datetime import datetime, timedelta


timezone = pytz.timezone("US/Eastern")
now = datetime.now()
localized_time = timezone.localize(now)
one_week_back = localized_time - timedelta(weeks=1)
datetime_string = one_week_back.strftime("%Y-%m-%d %H:%M:%S.%f%z")
# Replace the last two characters with a colon
datetime_string = datetime_string[:-2] + ":" + datetime_string[-2:]

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
            print("Hitting the API endpoint: ", url)
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data["items"])

            total = data["total"]
            offset += limit
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    for item in all_data:
        item["organization_id"] = organization_id
        item["connection_id"] = x_connection_id

    return all_data, vendor


# Function to insert vulnerability data into PostgreSQL
async def insert_data_to_postgres(all_data: List[dict], vendor: str):
    db = SessionLocal()
    try:
        new_records = []
        config = CONNECTOR_MAPPING.get(vendor.lower())
        if config is None:
            raise ValueError(f"No ORM configuration found for {vendor} vendor")
        ORMModel = config["model"]
        for record_data in all_data:
            db.execute(text("LOCK TABLE % s IN EXCLUSIVE MODE" % ORMModel.__tablename__))
            # Check if the record already exists
            record = db.query(ORMModel).filter(ORMModel.id == record_data["id"]).first()

            if record:
                # Update the existing record
                for key, value in record_data.items():
                    setattr(record, key, value)
            else:
                # Create a new record
                new_records.append(ORMModel(**record_data))

        if new_records:
            db.bulk_save_objects(new_records)

        db.commit()
    except Exception as e:
        db.rollback()
        print(e)  # Print the exception to the console
    finally:
        db.close()


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


async def fetch_and_insert_data(
    x_connection_id: str, organization_id: str, vendor: str
):
    vulnerabilities = await fetch_connector_data(
        x_connection_id, organization_id, vendor
    )
    for vuln in vulnerabilities:
        await insert_data_to_postgres(vuln, vendor=vendor)


@fetch_router.get(
    "/fetch_data_for_connection",
    tags=["Fetch Data"],
    description="Fetch data from the API and insert into the database for a specific connection",
)
async def fetch_data_for_connection(
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

