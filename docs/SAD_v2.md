# Software Architecture Document (SAD) - v2.0
## Temple Visitor Management System Enterprise Edition

### 1. Architectural Goals & Constraints
- **Offline First**: Continuous operation on edge mobile devices using SQLite.
- **Data Integrity**: Eventual consistency via Transactional Outbox pattern.
- **Serverless Cloud Scale**: Live Neon PostgreSQL 18 database with SSL connection pooling.
- **Multi-Tenant Isolation**: Tenant boundary enforcement via `X-Temple-ID` context.
- **Audit Compliance**: Immutable, append-only administrative logging.

---

### 2. System Architecture Diagram

```mermaid
graph TD
    subgraph "Mobile Client Edge (Flutter)"
        App[Flutter Mobile App]
        LocalDB[(SQLite Local DB)]
        Outbox[Transactional Outbox Queue]
        App --> LocalDB
        LocalDB --> Outbox
    end

    subgraph "Network Layer"
        HTTPS[HTTP REST API / SSL]
    end

    subgraph "Backend Infrastructure (FastAPI)"
        Gateway[FastAPI Gateway Engine]
        Auth[JWT & JTI Revocation Auth]
        SyncService[Delta Sync Service]
        BroadcastService[Broadcast Engine]
        AnalyticsService[Owner Analytics Service]
        AuditHook[Immutable Audit Hook]
        
        Gateway --> Auth
        Gateway --> SyncService
        Gateway --> BroadcastService
        Gateway --> AnalyticsService
        Gateway --> AuditHook
    end

    subgraph "Cloud Database & Storage"
        NeonDB[(Neon PostgreSQL 18)]
        BackupMgr[Backup & DR Manager]
        
        SyncService --> NeonDB
        BroadcastService --> NeonDB
        AnalyticsService --> NeonDB
        AuditHook --> NeonDB
        BackupMgr --> NeonDB
    end

    Outbox -->|POST /api/v2/sync/upload| HTTPS
    HTTPS --> Gateway
```

---

### 3. Database ER Diagram (29 Core Entities Snapshot)

```mermaid
erDiagram
    TEMPLES ||--o{ USERS : "has members"
    TEMPLES ||--o{ PERSONS : "registers devotees"
    TEMPLES ||--o{ VISITORS : "logs visits"
    TEMPLES ||--o{ BROADCAST_CAMPAIGNS : "creates campaigns"
    TEMPLES ||--o{ AUDIT_LOGS : "records events"

    USERS ||--o{ USER_ROLES : "assigned"
    ROLES ||--o{ USER_ROLES : "belongs to"
    ROLES ||--o{ ROLES_PERMISSIONS : "contains"
    PERMISSIONS ||--o{ ROLES_PERMISSIONS : "granted to"

    PERSONS ||--o{ VISITORS : "makes visits"
    PERSONS ||--o{ BROADCAST_RECIPIENTS : "receives broadcast"

    BROADCAST_CAMPAIGNS ||--o{ BROADCAST_RECIPIENTS : "targets"

    TEMPLES {
        string id PK
        string name
        string code
    }

    USERS {
        string id PK
        string username
        string password_hash
        string email
    }

    PERSONS {
        string id PK
        string temple_id FK
        string name
        string phone
        string village
        int total_visits
    }

    VISITORS {
        string id PK
        string visitor_uuid
        string name
        string phone_number
        datetime visitor_date
    }

    BROADCAST_CAMPAIGNS {
        string campaign_id PK
        string temple_id FK
        string title
        string message
        string status
    }

    AUDIT_LOGS {
        string audit_id PK
        string trace_id
        string temple_id FK
        string user_id FK
        string action
        datetime timestamp
    }
```

---

### 4. Sequence Diagrams

#### 4.1 Delta Synchronization Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Volunteer as Volunteer (Mobile App)
    participant Outbox as Local Outbox Queue
    participant API as FastAPI Backend
    participant DB as Neon PostgreSQL DB

    Volunteer->>Outbox: Register Devotee (Offline)
    Outbox->>Outbox: Stage PERSON_CREATE Event
    Note over Outbox: Network Connectivity Restored
    Outbox->>API: POST /api/v2/sync/upload (Events Batch)
    API->>API: Validate Token & Payload
    API->>DB: Upsert Person & Record Audit Event
    DB-->>API: Commit Transaction OK
    API-->>Outbox: HTTP 200 OK (Status: SYNCED, Token Issued)
    Outbox->>Outbox: Mark Local Events Synced
```

#### 4.2 Broadcast Campaign Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Temple Admin
    participant API as FastAPI Backend
    participant Engine as Broadcast Engine
    participant DB as Neon PostgreSQL DB

    Admin->>API: POST /api/v2/broadcast/campaigns (Filter Spec, Confirmed)
    API->>Engine: Resolve Target Audience (e.g. VILLAGE_MATCH)
    Engine->>DB: Query Target Persons
    DB-->>Engine: Return 500 Devotees
    Engine->>DB: Create Campaign & Populate Recipients Queue
    Engine->>DB: Record Audit Event (CAMPAIGN_CREATED)
    DB-->>API: Commit OK
    API-->>Admin: HTTP 201 Created (Campaign QUEUED, 500 Recipients)
```

#### 4.3 Backup & Disaster Recovery Sequence
```mermaid
sequenceDiagram
    autonumber
    actor System as Scheduled Job / Admin
    participant Mgr as BackupManager
    participant ActiveDB as Active DB Session
    participant Snap as Local SQLite Snapshot File

    System->>Mgr: create_database_backup(temple_id)
    Mgr->>ActiveDB: Query Base.metadata.sorted_tables
    ActiveDB-->>Mgr: Return Table Schemas & All Rows
    Mgr->>Snap: Create Schemas & Bulk Insert Rows
    Mgr->>Mgr: Compute SHA-256 Checksum & Size
    Mgr->>Mgr: Write JSON Metadata Sidecar File
    Mgr-->>System: Return Backup Metadata (File: temple_backup_XXXX.db)
```
