# API Documentation - v2.0
## Temple Visitor Management System Enterprise Edition

### Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://api.temple-vms.example.com`

---

### Authentication & Authorization
All API endpoints (except `/api/v2/health` and `/api/v2/auth/login`) require HTTP Bearer JWT Authentication and mandatory multi-tenant header context:

```http
Authorization: Bearer <access_token>
X-Temple-ID: SKSA_MAIN
```

---

### 1. Health Endpoints

#### `GET /api/v2/health`
Returns system health status and environment details.
- **Response `200 OK`**:
```json
{
  "status": "HEALTHY",
  "version": "v2.0",
  "system": "Sri Kalki Seva Alayam - Visitor Management System",
  "multi_tenant": true
}
```

#### `GET /api/v2/health/database`
Returns database connectivity and latency details.
- **Response `200 OK`**:
```json
{
  "status": "UP",
  "latency_ms": 18.42,
  "database_type": "PostgreSQL (Neon serverless)"
}
```

---

### 2. Authentication Endpoint

#### `POST /api/v2/auth/login`
Authenticates administrative users and returns a JWT access token.
- **Request Body**:
```json
{
  "username": "admin",
  "password": "Admin@12345"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### 3. Delta Synchronization Endpoint

#### `POST /api/v2/sync/upload`
Processes a batch of offline outbox events from edge client terminals.
- **Request Body**:
```json
{
  "client_id": "device_terminal_01",
  "temple_id": "SKSA_MAIN",
  "events": [
    {
      "event_id": "evt_99881122",
      "entity_type": "PERSON",
      "entity_id": "p_100200300",
      "action": "CREATE",
      "payload": {
        "id": "p_100200300",
        "temple_id": "SKSA_MAIN",
        "name": "Ramesh Kumar",
        "phone": "9876543210",
        "village": "Vijayawada",
        "total_visits": 1
      },
      "client_timestamp": "2026-07-30T12:00:00Z"
    }
  ]
}
```
- **Response `200 OK`**:
```json
{
  "client_id": "device_terminal_01",
  "next_sync_token": "token_1785414361_val_devi",
  "results": [
    {
      "event_id": "evt_99881122",
      "entity_id": "p_100200300",
      "status": "SYNCED",
      "retryable": false,
      "error_message": null
    }
  ]
}
```

---

### 4. Owner Dashboard Endpoints

#### `GET /api/v2/dashboard/overview`
Retrieves aggregated live visitor, communication, and synchronization metrics.
- **Response `200 OK`**:
```json
{
  "visitor_metrics": {
    "live_visitors": 12,
    "today_visitors": 12,
    "weekly_visitors": 84,
    "monthly_visitors": 340,
    "yearly_visitors": 4200,
    "repeat_visitors": 15,
    "first_time_visitors": 69
  },
  "communication": { "messages_sent": 120, "delivery_rate": 98.5 },
  "synchronization": { "last_sync_timestamp": "2026-07-30T12:25:58Z", "success_rate": 100.0 },
  "system_health_status": "HEALTHY"
}
```

---

### 5. Enterprise Broadcast Endpoints

#### `POST /api/v2/broadcast/campaigns`
Creates and queues a targeted broadcast campaign.
- **Request Body**:
```json
{
  "temple_id": "SKSA_MAIN",
  "title": "Sri Rama Navami Special Festival",
  "message": "Special Darshan and Annadanam invitation at Sri Kalki Seva Alayam",
  "audience_filter": { "filter_type": "ALL_DEVOTEES" },
  "confirmed": true
}
```
- **Response `201 Created`**:
```json
{
  "campaign_id": "786935a5-c1dd-4f0d-9ac2-f1f74f030a0c",
  "status": "QUEUED",
  "total_recipients": 500,
  "created_at": "2026-07-30T12:26:31Z"
}
```

---

### 6. Visitor Directory Endpoint

#### `GET /api/v1/visitors/?search=Ramesh&page=1&limit=20`
Searches master devotee directory records by name, mobile number, or village.
- **Response `200 OK`**:
```json
{
  "items": [
    {
      "id": "p_100200300",
      "name": "Ramesh Kumar",
      "phone": "9876543210",
      "village": "Vijayawada",
      "total_visits": 3
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```
