"""SQL validation and safety mechanisms."""

import re
from typing import List, Set
from sqlalchemy import text
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class SQLGuardError(Exception):
    """Exception raised when SQL validation fails."""
    pass


class SQLGuard:
    """SQL validation and safety guard."""
    
    # Allowed table names
    ALLOWED_TABLES: Set[str] = {
        "fact_measure",
        "dim_time", 
        "dim_geo",
        "dim_indicator"
    }
    
    # Forbidden SQL keywords (DDL/DML operations)
    FORBIDDEN_KEYWORDS: Set[str] = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", 
        "GRANT", "REVOKE", "TRUNCATE", "REPLACE", "MERGE"
    }
    
    # Allowed SQL keywords (DQL operations)
    ALLOWED_KEYWORDS: Set[str] = {
        "SELECT", "WITH", "FROM", "WHERE", "JOIN", "INNER", "LEFT", 
        "RIGHT", "OUTER", "ON", "AS", "AND", "OR", "NOT", "IN", 
        "EXISTS", "BETWEEN", "LIKE", "ORDER", "BY", "GROUP", "HAVING",
        "LIMIT", "OFFSET", "UNION", "INTERSECT", "EXCEPT", "CASE", 
        "WHEN", "THEN", "ELSE", "END", "DISTINCT", "ALL", "ANY", "SOME"
    }
    
    def __init__(self):
        self.max_rows = settings.max_rows_returned
        
    def validate_and_sanitize(self, query: str) -> text:
        """Validate SQL query and return sanitized version."""
        if not query or not query.strip():
            raise SQLGuardError("Query cannot be empty")
        
        # Normalize whitespace and remove comments
        query = self._normalize_query(query)
        
        # Check for forbidden keywords
        self._check_forbidden_keywords(query)
        
        # Validate table names
        self._validate_table_names(query)
        
        # Ensure query starts with SELECT or WITH
        self._validate_query_type(query)
        
        # Add LIMIT if not present
        query = self._ensure_limit(query)
        
        return text(query)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing comments and extra whitespace."""
        # Remove SQL comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        return query.strip()
    
    def _check_forbidden_keywords(self, query: str) -> None:
        """Check for forbidden SQL keywords."""
        # Extract keywords (words that are not quoted)
        keywords = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', query.upper())
        
        forbidden_found = [kw for kw in keywords if kw in self.FORBIDDEN_KEYWORDS]
        if forbidden_found:
            raise SQLGuardError(f"Forbidden SQL keywords detected: {forbidden_found}")
    
    def _validate_table_names(self, query: str) -> None:
        """Validate that only allowed tables are referenced."""
        # Extract table names after FROM and JOIN keywords
        from_pattern = r'\bFROM\s+([A-Za-z_][A-Za-z0-9_]*)'
        join_pattern = r'\bJOIN\s+([A-Za-z_][A-Za-z0-9_]*)'
        
        from_tables = re.findall(from_pattern, query, re.IGNORECASE)
        join_tables = re.findall(join_pattern, query, re.IGNORECASE)
        
        all_tables = set(from_tables + join_tables)
        
        # Convert to lowercase for comparison
        all_tables = {table.lower() for table in all_tables}
        
        disallowed_tables = all_tables - self.ALLOWED_TABLES
        if disallowed_tables:
            raise SQLGuardError(f"Access to tables not allowed: {disallowed_tables}")
    
    def _validate_query_type(self, query: str) -> None:
        """Ensure query is a valid SELECT or WITH statement."""
        query_upper = query.upper().strip()
        
        if not (query_upper.startswith('SELECT') or query_upper.startswith('WITH')):
            raise SQLGuardError("Only SELECT and WITH queries are allowed")
    
    def _ensure_limit(self, query: str) -> str:
        """Add LIMIT clause if not present."""
        query_upper = query.upper()
        
        # Check if LIMIT is already present
        if 'LIMIT' in query_upper:
            # Extract the limit value and ensure it's not too high
            limit_match = re.search(r'\bLIMIT\s+(\d+)', query_upper)
            if limit_match:
                limit_value = int(limit_match.group(1))
                if limit_value > self.max_rows:
                    # Replace with our max limit
                    query = re.sub(
                        r'\bLIMIT\s+\d+', 
                        f'LIMIT {self.max_rows}', 
                        query, 
                        flags=re.IGNORECASE
                    )
        else:
            # Add LIMIT clause
            query = f"{query} LIMIT {self.max_rows}"
        
        return query
