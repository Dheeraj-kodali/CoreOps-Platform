import sys
import logging
import time
from functools import wraps


class StructuredLogFormatter(logging.Formatter):
    """Custom Formatter outputting structured log metadata."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "temple_id"):
            log_entry["temple_id"] = record.temple_id
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return str(log_entry)


def setup_logging():
    """Initialize structured logging configuration for the backend service."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredLogFormatter())

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)


def log_performance(threshold_ms: float = 500.0):
    """Decorator to log slow domain service function executions exceeding a given threshold."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            if duration_ms > threshold_ms:
                logging.warning(
                    f"[PERFORMANCE ALERT] Slow function execution: '{func.__qualname__}' took {duration_ms:.2f}ms (Threshold: {threshold_ms}ms)"
                )
            return result

        return wrapper

    return decorator
