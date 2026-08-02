from datetime import date, datetime, timezone
import re
from typing import Dict, Any, Tuple

def eval_visitor_lifecycle(visitor, current_date: date = None) -> Dict[str, Any]:
    """
    Unified Single Source of Truth for Visitor Session Lifecycle and Status Calculation.
    
    Status Logic:
    1. CHECKED_OUT: Explicit checkout recorded in notes ([CHECKED_OUT], CHECKED_OUT, Visitor Left, Exit Time).
    2. AUTO_CLOSED: Explicit [AUTO_CLOSED] in notes OR visitor_date < current_date (unfinished session from previous day).
    3. INSIDE: visitor_date == current_date AND session not checked out or auto-closed.
    """
    if current_date is None:
        current_date = date.today()
        
    notes = visitor.notes or ""
    v_date = visitor.visitor_date if hasattr(visitor, "visitor_date") else current_date
    
    is_explicit_checkout = (
        "[CHECKED_OUT]" in notes or 
        "CHECKED_OUT" in notes or 
        "Visitor Left" in notes or 
        "Exit Time" in notes
    )
    
    is_explicit_autoclose = "[AUTO_CLOSED]" in notes or "AUTO_CLOSED" in notes
    is_past_day = v_date < current_date
    
    # Extract checkout time and duration if present in notes
    # Format: [CHECKED_OUT] Out: 12:40:45 (5 min)
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
            checkout_time = "Recorded"
        if not duration:
            duration = "Completed"
    elif is_explicit_autoclose or is_past_day:
        status = "AUTO_CLOSED"
        is_auto_closed = True
        if not checkout_time:
            checkout_time = "23:59:59 (Auto)"
        if not duration:
            duration = "Day-End Auto-Close"
    else:
        status = "INSIDE"
        is_auto_closed = False
        checkout_time = "N/A"
        duration = "Ongoing"
        
    check_in_time = str(visitor.visitor_time) if hasattr(visitor, "visitor_time") else "00:00:00"
    
    return {
        "status": status,
        "is_inside": status == "INSIDE",
        "is_checked_out": status in ("CHECKED_OUT", "AUTO_CLOSED"),
        "is_auto_closed": is_auto_closed,
        "check_in_time": check_in_time,
        "check_out_time": checkout_time,
        "duration": duration
    }
