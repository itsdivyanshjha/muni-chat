"""Database session management with read-only and owner connections."""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Owner engine for migrations and ETL
owner_engine: Engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

# Read-only engine for runtime queries
readonly_engine: Engine = create_engine(
    settings.runtime_db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

# Session makers
OwnerSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=owner_engine)
ReadonlySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=readonly_engine)


def get_owner_session() -> Generator[Session, None, None]:
    """Get a database session with owner privileges for migrations/ETL."""
    session = OwnerSessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_readonly_session() -> Generator[Session, None, None]:
    """Get a read-only database session for runtime queries."""
    session = ReadonlySessionLocal()
    try:
        yield session
    finally:
        session.close()


def execute_safe_query(query: str, timeout_seconds: int = None) -> dict:
    """Execute a read-only query with safety checks and timeout."""
    from services.sql_guard import SQLGuard
    
    # Validate and sanitize the query
    guard = SQLGuard()
    safe_query = guard.validate_and_sanitize(query)
    
    # Use configured timeout if not specified
    if timeout_seconds is None:
        timeout_seconds = settings.query_timeout_seconds
    
    session = ReadonlySessionLocal()
    try:
        # Set query timeout
        session.execute(f"SET statement_timeout = '{timeout_seconds}s'")
        
        # Execute the query
        result = session.execute(safe_query)
        
        # Fetch results
        columns = list(result.keys()) if result.keys() else []
        rows = result.fetchall()
        
        # Apply row limit
        if len(rows) > settings.max_rows_returned:
            logger.warning(f"Query returned {len(rows)} rows, limiting to {settings.max_rows_returned}")
            rows = rows[:settings.max_rows_returned]
        
        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows)
        }
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        session.close()
