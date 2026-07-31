import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.core.exceptions import AppException, app_exception_handler
from app.api.v1.router import api_router
from app.api.v2.router import api_v2_router
import app.models
from app.models.user import User, Role, UserRole
from app.models.temple import Temple
from app.models.purpose import Purpose
from app.models.village import Village
from app.models.communication import CommunicationSetting, MessageTemplate
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.middleware import TenantIsolationMiddleware, SecurityHeadersMiddleware, AuditTracingMiddleware
from app.core.logging_handler import ops_log_handler
from app.services.scheduler import global_scheduler

SERVER_START_TIME = time.time()


async def seed_initial_data():
    async with AsyncSessionLocal() as session:
        t_res = await session.execute(select(Temple).filter(Temple.is_deleted.is_(False)))
        temple = t_res.scalars().first()
        if not temple:
            temple = Temple(
                id="SKSA_MAIN",
                name="Sri Kalki Seva Alayam",
                code="SKSA_MAIN",
                address="Temple Complex, Chittoor, AP",
                contact_phone="+919876543210",
                contact_email="admin@kalkiseva.org",
                is_active=True,
            )
            session.add(temple)
            await session.commit()
            await session.refresh(temple)

        res = await session.execute(select(Role).filter(Role.is_deleted.is_(False)))
        roles = res.scalars().all()
        if not roles:
            admin_role = Role(name="SUPER_ADMIN", description="Full system administrator")
            volunteer_role = Role(name="VOLUNTEER", description="Visitor registration & sync volunteer")
            session.add_all([admin_role, volunteer_role])
            await session.commit()
            await session.refresh(admin_role)
            await session.refresh(volunteer_role)
        else:
            admin_role = next((r for r in roles if r.name == "SUPER_ADMIN"), roles[0])

        user_res = await session.execute(
            select(User).options(selectinload(User.roles)).filter(User.username == "admin", User.is_deleted.is_(False))
        )
        admin_user = user_res.scalars().first()
        if not admin_user:
            super_user = User(
                username="admin",
                email="admin@kalkiseva.org",
                password_hash=get_password_hash("Admin@12345"),
                full_name="Temple Super Administrator",
                phone_number="+919876543210",
                is_active=True,
            )
            session.add(super_user)
            await session.commit()
            await session.refresh(super_user)

            user_role = UserRole(user_id=super_user.id, role_id=admin_role.id)
            session.add(user_role)
            await session.commit()

        p_res = await session.execute(select(Purpose).filter(Purpose.is_deleted.is_(False)))
        if not p_res.scalars().all():
            purposes = [
                Purpose(temple_id=temple.id, name_en="General Darshan", name_te="సాధారణ దర్శనం", code="DARSHAN_GENERAL"),
                Purpose(temple_id=temple.id, name_en="Special Seva / Archana", name_te="ప్రత్యేక సేవ / అర్చన", code="SEVA_SPECIAL"),
                Purpose(temple_id=temple.id, name_en="Voluntary Service", name_te="స్వచ్ఛంద సేవ", code="VOLUNTEER_SERVICE"),
                Purpose(temple_id=temple.id, name_en="Donation / Annadanam", name_te="విరాళం / అన్నదానం", code="DONATION_ANNADANAM"),
            ]
            session.add_all(purposes)
            await session.commit()

        v_res = await session.execute(select(Village).filter(Village.is_deleted.is_(False)))
        if not v_res.scalars().all():
            villages = [
                Village(name_en="Kalki Nagaram", name_te="కల్కి నగరం", district="Chittoor", state="Andhra Pradesh"),
                Village(name_en="Tirupati Rural", name_te="తిరుపతి రూరల్", district="Tirupati", state="Andhra Pradesh"),
                Village(name_en="Madanapalle", name_te="మదనపల్లె", district="Annamayya", state="Andhra Pradesh"),
            ]
            session.add_all(villages)
            await session.commit()


async def seed_communication_defaults():
    async with AsyncSessionLocal() as session:
        cs_res = await session.execute(
            select(CommunicationSetting).filter(CommunicationSetting.is_deleted.is_(False))
        )
        if not cs_res.scalars().first():
            default_settings = CommunicationSetting(
                mode="DISABLED",
                access_token=None,
                phone_number_id=None,
                business_account_id=None,
                verify_token=None,
                auto_send=False,
                allow_edit=False,
                save_history=True,
                retry_failed=False,
            )
            session.add(default_settings)
            await session.commit()

        mt_res = await session.execute(
            select(MessageTemplate).filter(MessageTemplate.is_deleted.is_(False))
        )
        if not mt_res.scalars().all():
            entry_template = MessageTemplate(
                template_type="ENTRY",
                title="Visitor Entry Message",
                message=(
                    "\U0001f64f Welcome {name}\n"
                    "\n"
                    "You have successfully entered\n"
                    "{temple}\n"
                    "\n"
                    "Entry Time:\n"
                    "{time}\n"
                    "\n"
                    "Have a blessed day."
                ),
            )
            exit_template = MessageTemplate(
                template_type="EXIT",
                title="Visitor Exit Message",
                message=(
                    "\U0001f64f Thank you {name}\n"
                    "\n"
                    "Exit Time:\n"
                    "{time}\n"
                    "\n"
                    "Visit Duration:\n"
                    "{duration}\n"
                    "\n"
                    "Thank you for visiting\n"
                    "{temple}"
                ),
            )
            session.add_all([entry_template, exit_template])
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    await seed_communication_defaults()
    
    # Start production background scheduler
    global_scheduler.start()
    yield
    global_scheduler.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuditTracingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TenantIsolationMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_v2_router, prefix=settings.API_V2_STR)


@app.get("/health")
async def health_check():
    uptime_sec = int(time.time() - SERVER_START_TIME)
    return {
        "status": "HEALTHY",
        "system": settings.PROJECT_NAME,
        "uptime_seconds": uptime_sec,
        "scheduler_status": global_scheduler.get_status()["status"],
    }
