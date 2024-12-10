from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.models.connection_orm import ConnectionModel
from src.utils.fetch_data import fetch_data_and_insert_for_organization
from src.models.activity_orm import ActivityModel, ActivityType
from src.utils.database import get_db
import uuid
from src.schemas.connection_onramp import Activity, CreateConnectionResponseOnRamp


async def create_connection_onramp_logic(
    background_tasks: BackgroundTasks, response: Activity, db: Session = Depends(get_db)
):
    try:
        # Extract connection data
        connection_data = response.data

        # Check if the connection already exists
        existing_connection = db.query(ConnectionModel).filter(
            ConnectionModel.leen_connection_id == connection_data.id,
            ConnectionModel.leen_organization_id == connection_data.organization_id
        ).first()

        if existing_connection:
            return CreateConnectionResponseOnRamp(
                connection_id=str(existing_connection.leen_connection_id),
                message="Connection already exists for the organization",
                identifier=existing_connection.identifier,
                vendor=existing_connection.vendor,
                is_active=existing_connection.is_active,
            )

        # Create a new connection entry
        new_connection = ConnectionModel(
            id=uuid.uuid4(),
            leen_connection_id=connection_data.id,
            identifier=getattr(connection_data, "identifier", ""),
            vendor=connection_data.vendor,
            refresh_interval=connection_data.refresh_interval_secs,
            timeout=connection_data.timeout_secs,
            leen_organization_id=connection_data.organization_id,
            oauth2_authorize_url=getattr(connection_data, "oauth2_authorize_url", ""),
            is_active=connection_data.is_active,
        )
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)

        activity_data = ActivityModel(
            activity_type=ActivityType.CREATE_CONNECTION,
            response=connection_data.dict(),
            httpStatus=response.httpStatus,
            url="OnRamp API",
            leen_organization_id=connection_data.organization_id,
            created_at=None,
            created_by=None,
        )

        db.add(activity_data)
        db.commit()
        db.refresh(activity_data)

        background_tasks.add_task(
            fetch_data_and_insert_for_organization, organization_id=connection_data.organization_id
        )

        return CreateConnectionResponseOnRamp(
            connection_id=str(new_connection.leen_connection_id),
            message="Connection created successfully",
            identifier=new_connection.identifier,
            vendor=new_connection.vendor,
            is_active=new_connection.is_active,
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()