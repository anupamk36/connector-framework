from src.utils.database import get_db
from src.config.connector_config import CONNECTOR_MAPPING
from src.models.connectors_orm import ConnectorModel


def sync_connectors():
    # Use get_db to manage the session lifecycle
    db_gen = get_db()
    db = next(db_gen)
    try:
        for name, details in CONNECTOR_MAPPING.items():
            # Check if the connector already exists in the database
            connector = db.query(ConnectorModel).filter_by(name=name).first()

            if connector:
                # Update existing connector
                connector.base_url = details["base_url"]
                connector.description = details["description"]
                connector.model_name = details[
                    "model"
                ].__name__  # Store the model class name as a string
            else:
                # Create a new connector
                new_connector = ConnectorModel(
                    name=name,
                    base_url=details["base_url"],
                    description=details["description"],
                    model_name=details[
                        "model"
                    ].__name__,  # Store the model class name as a string
                )
                db.add(new_connector)

        # Commit the changes to the database
        db.commit()
    finally:
        # Ensure the db session is closed properly
        next(db_gen, None)
