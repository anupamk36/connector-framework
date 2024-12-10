from fastapi import HTTPException
import httpx
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# Fetch the x_api_key
x_api_key = config["DEFAULT"]["x_api_key"]


async def list_connection_logic(organization_id: str):
    try:
        url = f"https://api.leen.dev/v1/provisioning/organizations/{organization_id}/connections"
        headers = {"X-API-KEY": x_api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise e
