"""
Diagnostic Endpoints Template
Essential endpoints for debugging production issues
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from datetime import datetime
import os

from database.connection import get_db, engine

router = APIRouter()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if service is running.

    Use for:
    - Load balancer health checks
    - Uptime monitoring
    - Quick service status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "your-app-name"
    }

# ============================================================================
# DATABASE CHECK
# ============================================================================

@router.get("/db-check")
async def database_check(db: Session = Depends(get_db)):
    """
    Check database connectivity and list tables.

    Returns:
    - connected: bool
    - tables: list of table names
    - table_count: number of tables

    Use for:
    - Verifying database migrations
    - Checking database connectivity
    - Debugging missing tables
    """
    try:
        # Test connection
        db.execute(text("SELECT 1"))

        # Get table names
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        return {
            "connected": True,
            "database_url_set": bool(os.getenv('DATABASE_URL')),
            "table_count": len(tables),
            "tables": sorted(tables),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "database_url_set": bool(os.getenv('DATABASE_URL')),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================================================
# ENVIRONMENT CHECK
# ============================================================================

@router.get("/env-check")
async def environment_check():
    """
    Check which environment variables are set.

    ⚠️ IMPORTANT: Never expose actual values, only check if they're set!

    Returns:
    - environment: development/production
    - variables: dict of which variables are set (not their values!)

    Use for:
    - Debugging missing environment variables
    - Verifying deployment configuration
    - Checking which services are configured
    """
    return {
        "environment": os.getenv('ENVIRONMENT', 'unknown'),
        "variables": {
            # Core
            "database_url_set": bool(os.getenv('DATABASE_URL')),
            "environment_set": bool(os.getenv('ENVIRONMENT')),
            "log_level_set": bool(os.getenv('LOG_LEVEL')),

            # API Keys (check without exposing!)
            "finnhub_api_key_set": bool(os.getenv('FINNHUB_API_KEY')),
            "alpha_vantage_api_key_set": bool(os.getenv('ALPHA_VANTAGE_API_KEY')),

            # Optional services
            "redis_url_set": bool(os.getenv('REDIS_URL')),
            "sentry_dsn_set": bool(os.getenv('SENTRY_DSN')),
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# TABLE INFO
# ============================================================================

@router.get("/table-info/{table_name}")
async def table_info(table_name: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific table.

    Args:
        table_name: Name of the table

    Returns:
    - columns: list of column details
    - row_count: number of rows
    - indexes: list of indexes

    Use for:
    - Verifying table schema
    - Debugging column mismatches
    - Checking data population
    """
    try:
        inspector = inspect(engine)

        # Check if table exists
        tables = inspector.get_table_names()
        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

        # Get column information
        columns = inspector.get_columns(table_name)

        # Get row count
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = result.scalar()

        # Get indexes
        indexes = inspector.get_indexes(table_name)

        return {
            "table_name": table_name,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col["default"]) if col["default"] else None
                }
                for col in columns
            ],
            "indexes": [
                {
                    "name": idx["name"],
                    "columns": idx["column_names"],
                    "unique": idx["unique"]
                }
                for idx in indexes
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting table info: {str(e)}")

# ============================================================================
# SEQUENCE CHECK (PostgreSQL only)
# ============================================================================

@router.get("/sequence-check/{table_name}")
async def sequence_check(table_name: str, db: Session = Depends(get_db)):
    """
    Check PostgreSQL sequence status for a table.

    Args:
        table_name: Name of the table

    Returns:
    - max_id: Maximum ID in table
    - next_sequence_value: Next value from sequence
    - in_sync: Whether sequence is ahead of max_id

    Use for:
    - Debugging duplicate key violations
    - Verifying data imports
    - Checking sequence health after manual operations
    """
    database_url = os.getenv('DATABASE_URL', '')

    if not database_url.startswith('postgresql'):
        return {
            "error": "Sequence check only applicable to PostgreSQL",
            "database_type": "sqlite" if database_url.startswith('sqlite') else "unknown"
        }

    try:
        # Get max ID from table
        max_id_result = db.execute(text(f"SELECT MAX(id) FROM {table_name}"))
        max_id = max_id_result.scalar() or 0

        # Get next sequence value
        sequence_name = f"{table_name}_id_seq"
        next_val_result = db.execute(text(f"SELECT last_value FROM {sequence_name}"))
        next_val = next_val_result.scalar()

        # Check if in sync
        in_sync = next_val > max_id

        return {
            "table_name": table_name,
            "max_id": max_id,
            "next_sequence_value": next_val,
            "in_sync": in_sync,
            "needs_fix": not in_sync,
            "fix_command": f"ALTER SEQUENCE {sequence_name} RESTART WITH {max_id + 1};" if not in_sync else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking sequence: {str(e)}")

# ============================================================================
# VERSION INFO
# ============================================================================

@router.get("/version")
async def version_info():
    """
    Return version information about the application.

    Returns:
    - version: Application version
    - python_version: Python version
    - database_type: Type of database being used

    Use for:
    - Verifying correct deployment version
    - Debugging version-specific issues
    - Checking infrastructure details
    """
    import sys

    database_url = os.getenv('DATABASE_URL', '')

    if database_url.startswith('postgresql'):
        db_type = "PostgreSQL"
    elif database_url.startswith('sqlite'):
        db_type = "SQLite"
    else:
        db_type = "Unknown"

    return {
        "app_version": "1.0.0",  # Update this with each release
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "database_type": db_type,
        "environment": os.getenv('ENVIRONMENT', 'unknown'),
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# USAGE IN MAIN APP
# ============================================================================

"""
Add to your main FastAPI app:

from fastapi import FastAPI
from diagnostic_endpoints import router as diagnostic_router

app = FastAPI()

# Include diagnostic endpoints
app.include_router(diagnostic_router, tags=["diagnostics"])

# Now you can access:
# GET /health
# GET /db-check
# GET /env-check
# GET /table-info/{table_name}
# GET /sequence-check/{table_name}
# GET /version
"""
