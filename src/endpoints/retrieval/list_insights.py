from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.utils.database import get_db


async def list_insights_logic(
    organization_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size
    base_query = """
    SELECT 
        combined_data.organization_id,
        combined_data.connection_id,
        combined_data.patchable,
        combined_data.description,
        combined_data.vendor,
        combined_data.severity,
        combined_data.date,
        combined_data.code_repo,
        combined_data.project_file_path,
        combined_data.package_name,
        combined_data.package_version,
        combined_data.cvss_score,
        combined_data.first_seen,
        combined_data.last_seen,
        combined_data.solution
    FROM (
        SELECT 
            i.organization_id,
            i.connection_id,
            i.is_patchable AS patchable,
            i.name AS description,
            i.vendor,
            i.severity,
            i.publication_time AS date,
            i.code_repo,
            i.project_file_path,
            i.package_name,
            i.package_version,
            i.cvss_score,
            i.first_seen,
            i.last_seen,
            NULL AS solution
        FROM 
            issues i
        JOIN 
            connections c ON i.connection_id = c.leen_connection_id 
        WHERE 
            c.is_active = TRUE

        UNION ALL

        SELECT 
            v.organization_id,
            v.connection_id,
            v.patchable AS patchable,
            v.description,
            v.vendor,
            v.severity,
            v.created_at AS date,
            NULL AS code_repo,
            NULL AS project_file_path,
            NULL AS package_name,
            NULL AS package_version,
            v.cvss_base_score AS cvss_score,
            v.first_seen,
            v.last_seen,
            CASE 
                WHEN v.patchable THEN v.solution
                ELSE NULL
            END AS solution
        FROM 
            vulnerabilities v
        JOIN 
            connections c ON v.connection_id = c.leen_connection_id  
        WHERE 
            c.is_active = TRUE

        UNION ALL

        SELECT 
            a.organization_id,
            a.connection_id,
            NULL AS patchable,
            a.description,
            a.vendor,
            a.severity,
            a.first_event_time AS date,
            NULL AS code_repo,
            NULL AS project_file_path,
            NULL AS package_name,
            NULL AS package_version,
            NULL AS cvss_score,
            a.first_event_time AS first_seen,
            a.last_event_time AS last_seen,
            NULL AS solution
        FROM 
            alerts a
        JOIN 
            connections c ON a.connection_id = c.leen_connection_id  
        WHERE 
            c.is_active = TRUE
    ) AS combined_data
    WHERE 
        combined_data.organization_id = :organization_id

    """

    # Query to get the total count
    count_query = "SELECT COUNT(*) FROM (" + base_query + ") AS count_query"
    total_count_result = db.execute(text(count_query), {"organization_id": organization_id})
    total_count = total_count_result.scalar()

    # Query to get the paginated results
    data_query = "SELECT * FROM (" + base_query + ") AS data_query ORDER BY date DESC LIMIT :page_size OFFSET :offset;"
    result = db.execute(text(data_query), {"organization_id": organization_id, "page_size": page_size, "offset": offset})
    insights = result.fetchall()

    if not insights:
        raise HTTPException(status_code=404, detail="Insights not found")
    
    # Determine if this is the last page
    is_end = len(insights) < page_size
    
    return {
        "data": [row._asdict() for row in insights],
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "is_end": is_end
    }