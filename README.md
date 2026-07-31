# Temple Visitor Management System Enterprise Edition v2.0

An enterprise-grade, offline-first mobile and cloud web application built for seamless devotee registration, visitor management, broadcast communications, owner analytics, operations monitoring, security hardening, and disaster recovery.

---

## Project Overview

The **Temple Visitor Management System Enterprise Edition v2.0** is designed to handle high-volume visitor flow at temple premises with uninterrupted offline edge operation and browser-based management via a Next.js 15 Admin Portal. Client devices operate using a local SQLite offline database and sync outbox events seamlessly with a central serverless **Neon PostgreSQL** cloud database via a delta synchronization engine.

### Key Objectives
- **Zero-Downtime Offline Operation**: Allow temple volunteers and staff to register visitors and record visits without internet connectivity.
- **Reliable Data Sync**: Guarantee eventual consistency between edge SQLite databases and cloud PostgreSQL via a transactional outbox queue.
- **Broadcast Communication**: Enable temple administrators to send targeted festival notifications and event broadcasts to devotees via SMS/WhatsApp.
- **Comprehensive Owner Visibility**: Provide real-time operational metrics, visitor analytics, system health status, and immutable audit logs.
- **Browser-Based Admin Portal**: Enterprise Next.js 15 Web Application (`admin-web`) with RBAC, live reports, physical SQL backups, and security session management.

---

## Enterprise Features

- **Offline-First Architecture**: Fully functional edge nodes operating on SQLite with local Transactional Outbox pattern.
- **Delta Synchronization Protocol**: Efficient batch upload & sync token mechanism resolving conflicts and preventing duplicate records.
- **Live Cloud Database**: Serverless **Neon PostgreSQL 18** cloud database with SSL encryption and multi-tenant scoping (`X-Temple-ID`).
- **Next.js 15 Admin Portal (`admin-web`)**: Modern dark glassmorphic web dashboard built with Next.js 15, TypeScript, Tailwind CSS, and TanStack Query.
- **Targeted Broadcast Engine**: Audience filtering (`ALL_DEVOTEES`, `VILLAGE_MATCH`, `DATE_RANGE`, `REPEAT_VISITORS`), template library, and Meta WhatsApp Cloud API v23.0 integration.
- **Immutable Audit System**: 20-field append-only audit trail capturing administrative events with UUID trace IDs and ORM event hooks blocking deletion/tampering.
- **Physical SQL Backup & Disaster Recovery**: Automated 24-hour snapshot engine generating verified `.sql` backup files with SHA-256 checksum verification, 30-day retention purge, and browser downloads.
- **Enterprise Security Center**: Role-Based Access Control (RBAC), password complexity policies, JTI token revocation ("Logout From All Devices"), and TOTP MFA readiness.

---

## Client Requirement Compliance

| # | Client Requirement | System Implementation | Compliance |
| :-: | :--- | :--- | :-: |
| **1** | *"The owner must be able to access every visitor who has ever visited the temple."* | **Master Devotee Directory**: Multi-parameter search & filtering across master `persons` and granular `visitors` records with pagination. | **100%** |
| **2** | *"During important events, the owner must be able to send a custom/default message to all historical visitors or a selected group."* | **Enterprise Broadcast Engine**: Targeted filtering by village, date range, or visit frequency with pre-defined templates & queue tracking. | **100%** |
| **3** | *"The owner must have complete visibility into the entire system at any time."* | **Owner Dashboard & Audit Trail**: Real-time operational metrics, visitor analytics, sync status, health checks, operations monitoring, and 20-field append-only audit logs. | **100%** |

---

## Technology Stack

- **Mobile Client**: Flutter (Dart) — Cross-platform Android/iOS edge application with offline SQLite persistence.
- **Admin Web Portal**: Next.js 15 (TypeScript / React 19) — Turbopack-powered Web Portal (`admin-web/`) styled with Tailwind CSS & Lucide Icons.
- **Backend Framework**: FastAPI (Python 3.11 / 3.14) — Asynchronous RESTful API engine with Pydantic v2 schemas.
- **Edge Storage**: SQLite (`sqflite` on Flutter / `sqlite3` in Python) — Local offline transactional database.
- **Cloud Database**: Neon PostgreSQL 18 — Serverless PostgreSQL cloud database with SSL (`sslmode=require`).
- **ORM & Data Layer**: SQLAlchemy 2.0 (AsyncIO / `asyncpg` & `aiosqlite`).
- **Authentication & Security**: PyJWT (HS256) with JTI revocation check, Passlib (Bcrypt/PBKDF2) password hashing, custom CORS middleware, and HTTP security headers.
- **Testing Suites**: Pytest (AsyncIO / HTTPX ASGITransport), Flutter Test framework, Next.js Turbopack build suite.

---

## Folder Structure

```
temple/
├── admin-web/                  # Next.js 15 Web Admin / Owner Dashboard Interface
│   ├── src/app/
│   │   ├── dashboard/          # Visitors, Reports, Users, Security, Operations, Settings
│   │   └── login/              # Authentication & Protected Route Guard
│   ├── public/                 # Static Assets & Logos
│   └── package.json            # Web Portal Dependencies
├── backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                # API Endpoints (v1 and v2)
│   │   ├── core/               # Database, Security, Logging, Config
│   │   ├── models/             # SQLAlchemy Models (29 registered tables)
│   │   ├── schemas/            # Pydantic v2 Request/Response Schemas
│   │   └── services/           # Backup Engine, Scheduler, Meta WhatsApp
│   ├── alembic/                # Database Migrations
│   ├── tests/                  # Pytest Backend Test Suite
│   └── requirements.txt        # Production Dependencies
├── backups/                    # Physical Database Snapshot Exports (.sql)
├── mobile/                     # Flutter Mobile Client Application
├── scripts/                    # Acceptance & Validation Test Runners
└── README.md                   # Project Documentation
```

---

## Installation & Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Admin Web Portal Setup
```bash
cd admin-web
npm install
npm run dev
# Access http://localhost:3000
```

### 3. Mobile App Setup
```bash
cd mobile
flutter pub get
flutter run
```

---

## Production Build & Deployment Commands

### Backend Production Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Admin Web Production Build
```bash
cd admin-web
npm run build
npm run start
```

### Mobile Android Release APK
```bash
cd mobile
flutter build apk --release
```

---

## License

This project is proprietary software developed for Sri Kalki Seva Alayam. All rights reserved.
