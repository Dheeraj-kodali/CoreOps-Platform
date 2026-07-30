import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """Production JSON Structured Log Formatter for Observability & ELK/Datadog integration."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_fields"):
            log_obj.update(getattr(record, "extra_fields"))

        return json.dumps(log_obj)


def setup_structured_logging(log_level: str = "INFO"):
    """Configures structured JSON logging across the application."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(stream_handler)


def log_structured(logger_name: str, level: str, message: str, **kwargs):
    """Helper to emit structured log with context metadata."""
    logger = logging.getLogger(logger_name)
    lvl = getattr(logging, level.upper(), logging.INFO)
    extra = {"extra_fields": kwargs} if kwargs else {}
    logger.log(lvl, message, extra=extra)
