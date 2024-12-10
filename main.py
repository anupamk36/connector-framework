from fastapi import FastAPI
import configparser
import asyncio
from src.routers.creation import post_router
from src.utils.fetch_data import fetch_router
from src.routers.retrieval import get_router
from src.routers.removal import removal_router
from src.utils.sync_connectors import sync_connectors

from sqlalchemy.ext.declarative import declarative_base
from fastapi.middleware.cors import CORSMiddleware

Base = declarative_base()

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]

# # Create FastAPI instance
app = FastAPI()

allowed_origins = [
    "*",  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be included in cross-origin HTTP requests
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(post_router)
app.include_router(fetch_router)
app.include_router(get_router)
app.include_router(removal_router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to Cowbell Connector API"}


@app.on_event("startup")
async def startup_event():
    print("Starting up")
    await asyncio.get_event_loop().run_in_executor(None, sync_connectors)
