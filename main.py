from fastapi import FastAPI
import configparser
from src.routers.provisioning import router as provisioning_router
from src.utils.fetch_data import fetch_router
from src.routers.connectors import connector_router

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]

# Create FastAPI instance
app = FastAPI()
app.include_router(provisioning_router)
app.include_router(fetch_router)
app.include_router(connector_router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to Connector API"}