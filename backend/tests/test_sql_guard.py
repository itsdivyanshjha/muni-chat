"""Tests for SQL Guard functionality."""

import pytest
from services.sql_guard import SQLGuard, SQLGuardError


def test_sql_guard_allows_select():
    """Test that SQL guard allows SELECT queries."""
    guard = SQLGuard()
    
    query = "SELECT * FROM fact_measure"
    result = guard.validate_and_sanitize(query)
    assert result is not None


def test_sql_guard_allows_with():
    """Test that SQL guard allows WITH queries."""
    guard = SQLGuard()
    
    query = """
    WITH forest_data AS (
        SELECT * FROM fact_measure WHERE indicator_id = 1
    )
    SELECT * FROM forest_data
    """
    result = guard.validate_and_sanitize(query)
    assert result is not None


def test_sql_guard_blocks_insert():
    """Test that SQL guard blocks INSERT statements."""
    guard = SQLGuard()
    
    query = "INSERT INTO fact_measure (value) VALUES (100)"
    
    with pytest.raises(SQLGuardError) as exc_info:
        guard.validate_and_sanitize(query)
    
    assert "Forbidden SQL keywords detected" in str(exc_info.value)


def test_sql_guard_blocks_update():
    """Test that SQL guard blocks UPDATE statements."""
    guard = SQLGuard()
    
    query = "UPDATE fact_measure SET value = 100"
    
    with pytest.raises(SQLGuardError) as exc_info:
        guard.validate_and_sanitize(query)
    
    assert "Forbidden SQL keywords detected" in str(exc_info.value)


def test_sql_guard_blocks_delete():
    """Test that SQL guard blocks DELETE statements."""
    guard = SQLGuard()
    
    query = "DELETE FROM fact_measure"
    
    with pytest.raises(SQLGuardError) as exc_info:
        guard.validate_and_sanitize(query)
    
    assert "Forbidden SQL keywords detected" in str(exc_info.value)


def test_sql_guard_blocks_drop():
    """Test that SQL guard blocks DROP statements."""
    guard = SQLGuard()
    
    query = "DROP TABLE fact_measure"
    
    with pytest.raises(SQLGuardError) as exc_info:
        guard.validate_and_sanitize(query)
    
    assert "Forbidden SQL keywords detected" in str(exc_info.value)


def test_sql_guard_blocks_unauthorized_tables():
    """Test that SQL guard blocks access to unauthorized tables."""
    guard = SQLGuard()
    
    query = "SELECT * FROM users"
    
    with pytest.raises(SQLGuardError) as exc_info:
        guard.validate_and_sanitize(query)
    
    assert "Access to tables not allowed" in str(exc_info.value)


def test_sql_guard_adds_limit():
    """Test that SQL guard adds LIMIT if not present."""
    guard = SQLGuard()
    
    query = "SELECT * FROM fact_measure"
    result = guard.validate_and_sanitize(query)
    
    assert "LIMIT" in str(result)


def test_sql_guard_enforces_max_limit():
    """Test that SQL guard enforces maximum LIMIT."""
    guard = SQLGuard()
    
    query = "SELECT * FROM fact_measure LIMIT 10000"
    result = guard.validate_and_sanitize(query)
    
    # Should be replaced with max limit (5000 by default)
    assert "LIMIT 5000" in str(result) or "LIMIT 10000" not in str(result)


def test_sql_guard_empty_query():
    """Test that SQL guard rejects empty queries."""
    guard = SQLGuard()
    
    with pytest.raises(SQLGuardError) as exc_info:
        guard.validate_and_sanitize("")
    
    assert "Query cannot be empty" in str(exc_info.value)


def test_sql_guard_removes_comments():
    """Test that SQL guard removes SQL comments."""
    guard = SQLGuard()
    
    query = """
    SELECT * FROM fact_measure -- This is a comment
    /* This is a block comment */
    WHERE value > 0
    """
    
    result = guard.validate_and_sanitize(query)
    result_str = str(result)
    
    assert "--" not in result_str
    assert "/*" not in result_str
    assert "*/" not in result_str
