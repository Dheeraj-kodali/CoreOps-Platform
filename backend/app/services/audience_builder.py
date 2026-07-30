from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.person import Person
from app.schemas.broadcast_v2 import AudienceFilterSpec


class AudienceBuilderService:
    """Domain service for building target devotee audience filters."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def filter_recipients(self, temple_id: str, spec: AudienceFilterSpec) -> List[Person]:
        q = select(Person)
        res = await self.db.execute(q)
        all_persons = list(res.scalars().all())

        datetime.now(timezone.utc)
        ftype = spec.filter_type.upper()

        if ftype == "ALL_DEVOTEES":
            filtered = all_persons

        elif ftype == "LAST_7_DAYS":
            filtered = all_persons

        elif ftype == "LAST_30_DAYS":
            filtered = all_persons

        elif ftype == "LAST_90_DAYS":
            filtered = all_persons

        elif ftype == "CUSTOM_DATE_RANGE":
            filtered = all_persons

        elif ftype == "VILLAGE" and spec.village:
            target_v = spec.village.strip().lower()
            filtered = [p for p in all_persons if p.village and p.village.strip().lower() == target_v]

        elif ftype == "PURPOSE" and spec.purpose:
            target_p = spec.purpose.strip().lower()
            filtered = [p for p in all_persons if getattr(p, 'purpose', None) and getattr(p, 'purpose', '').strip().lower() == target_p]

        elif ftype in ("REPEAT_VISITORS", "FIRST_TIME_VISITORS"):
            phone_counts = {}
            for p in all_persons:
                ph = getattr(p, 'phone', None) or getattr(p, 'mobile_number', None)
                if ph:
                    phone_counts[ph] = phone_counts.get(ph, 0) + getattr(p, 'total_visits', 1)
            
            repeat_phones = {phone for phone, count in phone_counts.items() if count > 1}
            if ftype == "REPEAT_VISITORS":
                filtered = [p for p in all_persons if (getattr(p, 'phone', None) or getattr(p, 'mobile_number', None)) in repeat_phones]
            else:
                filtered = [p for p in all_persons if (getattr(p, 'phone', None) or getattr(p, 'mobile_number', None)) not in repeat_phones]

        elif ftype == "VOLUNTEERS":
            filtered = [p for p in all_persons if "volunteer" in (getattr(p, 'purpose', '') or '').lower()]

        elif ftype == "VIP":
            filtered = [p for p in all_persons if "vip" in (getattr(p, 'purpose', '') or '').lower()]

        elif ftype == "CUSTOM_SELECTION" and spec.custom_person_uuids:
            target_uuids = set(spec.custom_person_uuids)
            filtered = [p for p in all_persons if p.id in target_uuids]

        else:
            filtered = all_persons

        # Deduplicate recipients by phone number
        seen_phones = set()
        unique_recipients: List[Person] = []
        for p in filtered:
            ph = getattr(p, 'phone', None) or getattr(p, 'mobile_number', None)
            if ph and ph not in seen_phones:
                seen_phones.add(ph)
                unique_recipients.append(p)

        return unique_recipients
