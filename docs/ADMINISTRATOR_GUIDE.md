# Administrator Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Role-Based Access Control (RBAC)
The system enforces strict RBAC permissions across all API endpoints:
- `ADMIN`: Full system access, User creation, Role assignment, System Configuration, Backup & Restore.
- `TEMPLE_OWNER`: Temple configuration, Analytics view, Report export, Broadcast Campaign creation & approval.
- `VOLUNTEER / OPERATOR`: Visitor registration, Checkout, Repeat visitor lookup.

## 2. Managing Users & Passwords
- **Create User**: `POST /api/v2/auth/register`
- **Reset Password**: `POST /api/v1/auth/reset-password`
- Password Policy: Minimum 8 characters, at least 1 uppercase letter, 1 number, and 1 special character.

## 3. Communication & WhatsApp Integration
- Configure Meta Cloud API Token under **Communication Settings** in Admin Dashboard.
- Access Token, Phone Number ID (`1290699690788322`), and Business Account ID are stored securely and masked in security log outputs.
