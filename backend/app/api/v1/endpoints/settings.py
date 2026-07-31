import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.setting import Setting
from app.models.audit import AuditRecord

router = APIRouter()

DEFAULT_TEMPLE_SETTINGS = {
  "general": {
    "temple_name": "Sri Kalki Seva Alayam",
    "description": "Central Temple & Spiritual Center for Darshan and Seva Services.",
    "registration_number": "REG-SKSA-2026-0891",
    "logo_url": "/logo.png",
  },
  "contact": {
    "address": "Kalki Temple Street, Main Road, Tirupati, Andhra Pradesh - 517501",
    "phone": "+91 98765 43210",
    "email": "contact@kalkiseva.org",
    "website": "https://kalkiseva.org",
    "google_maps": "https://maps.google.com/?q=Kalki+Temple",
  },
  "operating_hours": {
    "opening_time": "06:00 AM",
    "closing_time": "09:00 PM",
    "special_festival_hours": "05:00 AM - 11:00 PM",
    "weekly_closed_days": "None",
  },
  "branding": {
    "primary_color": "#F59E0B",
    "secondary_color": "#10B981",
    "dashboard_title": "Temple Management Platform - Administrator Portal",
    "footer_text": "© 2026 Sri Kalki Seva Alayam. All Rights Reserved.",
  },
  "visitor_config": {
    "categories": ["General Visitor", "VIP Devotee", "Donor", "Volunteer"],
    "purpose_list": ["General Darshan", "Special Seva", "Annadhanam", "Donation", "Volunteer Work"],
    "max_visitors_per_day": 5000,
    "auto_checkout_minutes": 120,
  },
  "broadcast": {
    "default_whatsapp_template": "Dear {visitor_name}, welcome to Sri Kalki Seva Alayam! Your visit ID is {visit_id}.",
    "sms_template": "Welcome {visitor_name} to Sri Kalki Seva Alayam. Visit ID: {visit_id}.",
    "announcement_template": "Special Darshan timings today: {opening_time} to {closing_time}.",
  },
  "receipt_branding": {
    "temple_name": "Sri Kalki Seva Alayam",
    "address": "Kalki Temple Street, Tirupati, AP - 517501",
    "footer_text": "May Lord Kalki Bless You & Your Family.",
    "signature_placeholder": "Authorized Trustee / Executive Officer",
  }
}


@router.get("/")
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Setting).filter(Setting.key == "temple_settings")
    res = await db.execute(stmt)
    setting_row = res.scalars().first()

    if setting_row:
        try:
            return json.loads(setting_row.value_json)
        except Exception:
            return DEFAULT_TEMPLE_SETTINGS

    return DEFAULT_TEMPLE_SETTINGS


@router.put("/")
async def update_settings(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Role Security: Only Owner and Manager/Admin can update settings
    user_role = getattr(current_user, "role", "Administrator")
    if user_role not in ["Owner", "Manager", "Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Temple Owner or Manager can modify temple settings.",
        )

    stmt = select(Setting).filter(Setting.key == "temple_settings")
    res = await db.execute(stmt)
    setting_row = res.scalars().first()

    json_str = json.dumps(payload)

    if setting_row:
        setting_row.value_json = json_str
    else:
        setting_row = Setting(key="temple_settings", value_json=json_str, description="Global Temple Branding & Settings")
        db.add(setting_row)

    # Audit Logging
    audit_entry = AuditRecord(
        user_id=current_user.id,
        role=user_role,
        action="TEMPLE_SETTINGS_UPDATE",
        entity_type="Settings",
        status="SUCCESS",
        severity="INFO",
    )
    db.add(audit_entry)

    await db.commit()
    return payload


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Simulate logo file upload response
    logo_path = f"/uploads/temple_logo_{Date.now() if 'Date' in globals() else '2026'}.png"
    return {"message": "Logo uploaded successfully", "logo_url": logo_path}
