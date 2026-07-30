# Database Schema Reference - Sri Kalki Seva Alayam (Phase 2)

Database Engine: **PostgreSQL 15+** (with SQLite v3 dual-compatibility)  
Primary Key Strategy: **UUID v4 (String 36)**  
Soft Delete Strategy: **`is_deleted` (Boolean default `False`) + `deleted_at` (Timestamp)**  
Audit Metadata Strategy: **`created_at`, `updated_at`, `created_by`, `updated_by`**

---

## 🗂️ 19 PostgreSQL Entity Tables

### 1. `users`
- `id`: UUID (PK)
- `username`: String(50), UNIQUE, NOT NULL, INDEX
- `email`: String(100), UNIQUE, NULLABLE, INDEX
- `password_hash`: String(255), NOT NULL
- `full_name`: String(100), NOT NULL
- `phone_number`: String(20), NULLABLE, INDEX
- `is_active`: Boolean, DEFAULT True
- Audit & Soft Delete Mixin

### 2. `roles`
- `id`: UUID (PK)
- `name`: String(50), UNIQUE, NOT NULL, INDEX
- `description`: Text, NULLABLE
- Audit & Soft Delete Mixin

### 3. `permissions`
- `id`: UUID (PK)
- `code`: String(100), UNIQUE, NOT NULL, INDEX
- `module`: String(50), NOT NULL
- `description`: Text, NULLABLE
- Audit & Soft Delete Mixin

### 4. `user_roles`
- `user_id`: UUID (FK `users.id`), PK
- `role_id`: UUID (FK `roles.id`), PK
- `assigned_at`: DateTime(tz)

### 5. `roles_permissions`
- `role_id`: UUID (FK `roles.id`), PK
- `permission_id`: UUID (FK `permissions.id`), PK

### 6. `temples`
- `id`: UUID (PK)
- `name`: String(200), NOT NULL, INDEX
- `code`: String(50), UNIQUE, NOT NULL, INDEX
- `address`: Text, NULLABLE
- `contact_phone`: String(20), NULLABLE
- `contact_email`: String(100), NULLABLE
- `is_active`: Boolean, DEFAULT True
- Audit & Soft Delete Mixin

### 7. `volunteers`
- `id`: UUID (PK)
- `user_id`: UUID (FK `users.id`), NOT NULL, INDEX
- `temple_id`: UUID (FK `temples.id`), NOT NULL, INDEX
- `badge_number`: String(50), NULLABLE, INDEX
- `status`: String(20), DEFAULT 'ACTIVE'
- Audit & Soft Delete Mixin

### 8. `visitors`
- `id`: UUID (PK)
- `visitor_uuid`: String(36), UNIQUE, NOT NULL, INDEX
- `name`: String(150), NOT NULL, INDEX
- `phone_number`: String(20), NOT NULL, INDEX
- `gender`: String(10), NOT NULL (`MALE`, `FEMALE`, `OTHER`)
- `age`: Integer, NOT NULL
- `persons_count`: Integer, DEFAULT 1
- `temple_id`: UUID (FK `temples.id`), NULLABLE
- `village_id`: UUID (FK `villages.id`), NULLABLE
- `village_name_custom`: String(150), NULLABLE
- `purpose_id`: UUID (FK `purposes.id`), NOT NULL
- `temple_service`: String(150), NULLABLE
- `visitor_date`: Date, NOT NULL, INDEX
- `visitor_time`: Time, NOT NULL
- `volunteer_id`: UUID (FK `users.id`), NOT NULL
- `notes`: Text, NULLABLE
- `photo_url`: String(500), NULLABLE
- `id_proof_url`: String(500), NULLABLE
- `sync_status`: String(20), DEFAULT 'SYNCED'
- Audit & Soft Delete Mixin

### 9. `purposes` (`visit_purposes`)
- `id`: UUID (PK)
- `temple_id`: UUID (FK `temples.id`), NULLABLE
- `name_en`: String(100), NOT NULL
- `name_te`: String(100), NOT NULL
- `code`: String(50), UNIQUE, NOT NULL, INDEX
- `is_active`: Boolean, DEFAULT True
- Audit & Soft Delete Mixin

### 10. `villages`
- `id`: UUID (PK)
- `name_en`: String(100), NOT NULL, INDEX
- `name_te`: String(100), NOT NULL, INDEX
- `district`: String(100), NULLABLE
- `state`: String(100), DEFAULT 'Andhra Pradesh'
- `pin_code`: String(10), NULLABLE
- Audit & Soft Delete Mixin

### 11. `notifications`
- `id`: UUID (PK)
- `visitor_id`: UUID (FK `visitors.id`), NULLABLE
- `template_id`: UUID (FK `notification_templates.id`), NULLABLE
- `channel`: String(20), NOT NULL (`SMS`, `WHATSAPP`)
- `content`: Text, NOT NULL
- `status`: String(20), DEFAULT 'PENDING'
- Audit & Soft Delete Mixin

### 12. `sms_logs`
- `id`: UUID (PK)
- `phone_number`: String(20), NOT NULL, INDEX
- `message_content`: Text, NOT NULL
- `provider_response`: Text, NULLABLE
- `status`: String(20), DEFAULT 'PENDING', INDEX
- `retry_count`: Integer, DEFAULT 0
- `last_retry_at`: DateTime(tz), NULLABLE
- Audit & Soft Delete Mixin

### 13. `whatsapp_logs`
- `id`: UUID (PK)
- `phone_number`: String(20), NOT NULL, INDEX
- `message_content`: Text, NOT NULL
- `provider_response`: Text, NULLABLE
- `status`: String(20), DEFAULT 'PENDING', INDEX
- `retry_count`: Integer, DEFAULT 0
- `last_retry_at`: DateTime(tz), NULLABLE
- Audit & Soft Delete Mixin

### 14. `reports`
- `id`: UUID (PK)
- `report_type`: String(50), NOT NULL, INDEX
- `title`: String(200), NOT NULL
- `generated_by`: UUID (FK `users.id`), NOT NULL
- `file_url`: String(500), NULLABLE
- `format`: String(10), NOT NULL (`pdf`, `excel`, `csv`)
- `parameters_json`: Text, NULLABLE
- Audit & Soft Delete Mixin

### 15. `audit_logs`
- `id`: UUID (PK)
- `user_id`: UUID (FK `users.id`), NULLABLE
- `action`: String(100), NOT NULL
- `resource`: String(100), NOT NULL
- `details_json`: Text, NULLABLE
- `ip_address`: String(45), NULLABLE
- Audit & Soft Delete Mixin

### 16. `sync_queue`
- `id`: UUID (PK)
- `visitor_uuid`: String(36), NOT NULL, INDEX
- `client_id`: String(100), NOT NULL
- `action_type`: String(20), NOT NULL (`CREATE`, `UPDATE`, `DELETE`)
- `payload_json`: Text, NOT NULL
- `status`: String(20), DEFAULT 'PENDING', INDEX
- `error_message`: Text, NULLABLE
- `client_timestamp`: DateTime(tz), NOT NULL
- `server_synced_at`: DateTime(tz), NULLABLE
- Audit & Soft Delete Mixin

### 17. `settings`
- `id`: UUID (PK)
- `temple_id`: UUID (FK `temples.id`), NULLABLE
- `key`: String(100), UNIQUE, NOT NULL, INDEX
- `value_json`: Text, NOT NULL
- `description`: Text, NULLABLE
- Audit & Soft Delete Mixin

### 18. `devices`
- `id`: UUID (PK)
- `device_id`: String(100), UNIQUE, NOT NULL, INDEX
- `user_id`: UUID (FK `users.id`), NOT NULL, INDEX
- `device_name`: String(100), NULLABLE
- `fcm_token`: String(500), NULLABLE
- `last_active_at`: DateTime(tz), NULLABLE
- `is_active`: Boolean, DEFAULT True
- Audit & Soft Delete Mixin

### 19. `sessions`
- `id`: UUID (PK)
- `user_id`: UUID (FK `users.id`), NOT NULL, INDEX
- `token_jti`: String(36), UNIQUE, NOT NULL, INDEX
- `refresh_token`: Text, NULLABLE
- `ip_address`: String(45), NULLABLE
- `user_agent`: String(255), NULLABLE
- `is_revoked`: Boolean, DEFAULT False, INDEX
- `expires_at`: DateTime(tz), NOT NULL
- Audit & Soft Delete Mixin
