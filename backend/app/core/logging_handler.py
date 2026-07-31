import logging
from collections import deque
from datetime import datetime
from typing import List, Dict, Any, Optional

# In-memory ring buffer holding recent 500 log records
MAX_LOG_ENTRIES = 500
log_ring_buffer: deque = deque(maxlen=MAX_LOG_ENTRIES)


class OperationalLogHandler(logging.Handler):
    """
    Custom logging handler that intercepts all application logs
    and stores them in a memory ring buffer for live Operations Center inspection.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_entry = {
                "id": f"log-{record.created:.3f}",
                "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
                "severity": record.levelname,
                "component": record.name.replace("app.", "").replace("endpoints.", "").title(),
                "message": self.format(record),
            }
            log_ring_buffer.appendleft(log_entry)
        except Exception:
            self.handleError(record)


# Initialize global handler instance
ops_log_handler = OperationalLogHandler()
ops_log_handler.setFormatter(logging.Formatter("%(message)s"))
ops_log_handler.setLevel(logging.INFO)

# Attach to root logger
logging.getLogger("app").addHandler(ops_log_handler)
logging.getLogger("app").setLevel(logging.INFO)


def get_live_logs(
    severity: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Retrieve filtered log entries from the live ring buffer."""
    entries = list(log_ring_buffer)

    if severity:
        sev_upper = severity.upper()
        entries = [e for e in entries if e["severity"] == sev_upper]

    if component:
        comp_lower = component.lower()
        entries = [e for e in entries if comp_lower in e["component"].lower()]

    return entries[:limit]
