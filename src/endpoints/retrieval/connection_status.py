from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.utils.database import get_db


async def list_connection_status_logic(
    organization_id: str, db: Session = Depends(get_db)
):
    # Define the raw SQL query with placeholders for parameters
    raw_sql = text(
        """
    SELECT
        c.id,
        c.name AS connector_name,
        c.description AS connector_description,
        co.leen_connection_id,
        CASE 
            WHEN co.is_active IS NULL THEN 'Available'
            ELSE 'Connected'
        END AS status
    FROM
        connectors c
    LEFT JOIN
        connections co ON lower(c.name) = lower(co.vendor)
        AND co.leen_organization_id = :org_id
        AND co.is_active = true
    """
    )

    # Execute the query with the organization_id parameter
    result_set = db.execute(raw_sql, {"org_id": organization_id}).fetchall()

    # Convert result set rows to dictionaries
    result_set_dicts = [row._asdict() for row in result_set]

    # Map the result set to the desired output format
    result = [
        {
            "id": row['id'], 
            "name": row['connector_name'], 
            "description": row['connector_description'], 
            "status": row['status'],
            "leen_connection_id": row['leen_connection_id']
        }
        for row in result_set_dicts
    ]
    return result