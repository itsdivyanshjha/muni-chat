"""Logging configuration for the Municipal AI Insights backend."""

import logging
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


def hash_prompt(prompt: str) -> str:
    """Create a hash of the prompt for logging purposes."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:8]


def log_request_response(
    logger: logging.Logger,
    prompt: str,
    filters: Dict[str, Any],
    sql_used: str,
    duration_ms: int,
    row_count: int,
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """Log request and response details for observability."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt_hash": hash_prompt(prompt),
        "filters": filters,
        "sql_used": sql_used,
        "duration_ms": duration_ms,
        "row_count": row_count,
        "success": success,
    }
    
    if error:
        log_data["error"] = error
    
    if success:
        logger.info(f"Request completed: {json.dumps(log_data)}")
    else:
        logger.error(f"Request failed: {json.dumps(log_data)}")
