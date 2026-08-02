from datetime import date, datetime, timezone
import re
from typing import Dict, Any


def _parse_date(val) -> date:
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return datetime.strptime(val[:10], "%Y-%m-%d").date()
        except Exception:
            pass
    return date.today()


def eval_visitor_lifecycle(visitor, current_date: date = None) -> Dict[str, Any]:
    """
    Unified Single Source of Truth for Visitor Session Lifecycle and Status Calculation.
    
    Status Logic:
    1. CHECKED_OUT: Explicit status == "CHECKED_OUT" OR checkout recorded in notes.
    2. AUTO_CLOSED: Explicit status == "AUTO_CLOSED" OR notes contain [AUTO_CLOSED] OR visit_date < current_date.
    3. INSIDE: visit_date == current_date AND status not checked out or auto-closed.
    """
    if current_date is None:
        current_date = date.today()

    if isinstance(visitor, dict):
        notes = visitor.get("notes") or ""
        raw_date = visitor.get("visit_date") or visitor.get("visitor_date") or visitor.get("date")
        raw_time = visitor.get("check_in_time") or visitor.get("visitor_time") or visitor.get("time") or "00:00:00"
        obj_status = visitor.get("status")
    else:
        notes = getattr(visitor, "notes", "") or ""
        raw_date = getattr(visitor, "visit_date", None) or getattr(visitor, "visitor_date", None)
        raw_time = getattr(visitor, "check_in_time", None) or getattr(visitor, "visitor_time", "00:00:00")
        obj_status = getattr(visitor, "status", None)

    v_date = _parse_date(raw_date)

    is_explicit_checkout = (
        obj_status == "CHECKED_OUT" or
        "[CHECKED_OUT]" in notes or
        "CHECKED_OUT" in notes or
        "Visitor Left" in notes or
        "Exit Time" in notes
    )

    is_explicit_autoclose = obj_status == "AUTO_CLOSED" or "[AUTO_CLOSED]" in notes or "AUTO_CLOSED" in notes
    is_past_day = v_date < current_date

    checkout_time = None
    duration = None

    if "Out: " in notes:
        try:
            match = re.search(r"Out:\s*([0-9:]+)\s*\(([^)]+)\)", notes)
            if match:
                checkout_time = match.group(1)
                duration = match.group(2)
        except Exception:
            pass

    if is_explicit_checkout:
        status = "CHECKED_OUT"
        is_auto_closed = False
        if not checkout_time:
            c_out = getattr(visitor, "check_out_time", None)
            checkout_time = str(c_out) if c_out else "Recorded"
        if not duration:
            duration = getattr(visitor, "duration", "Completed")
    elif is_explicit_autoclose or is_past_day:
        status = "AUTO_CLOSED"
        is_auto_closed = True
        if not checkout_time:
            c_out = getattr(visitor, "check_out_time", None)
            checkout_time = str(c_out) if c_out else "23:59:59 (Auto)"
        if not duration:
            duration = getattr(visitor, "duration", "Day-End Auto-Close")
    else:
        status = "INSIDE"
        is_auto_closed = False
        checkout_time = "N/A"
        duration = getattr(visitor, "duration", "Ongoing")

    check_in_time = str(raw_time)

    return {
        "status": status,
        "is_inside": status == "INSIDE",
        "is_checked_out": status in ("CHECKED_OUT", "AUTO_CLOSED"),
        "is_auto_closed": is_auto_closed,
        "check_in_time": check_in_time,
        "check_out_time": checkout_time,
        "duration": duration
    }
