# Security Policy

## Reporting Security Issues
If you discover a potential security vulnerability in the Temple Visitor Management System, please report it immediately to security@temple-vms.example.com. Do NOT open a public issue.

## Supported Versions
| Version | Supported |
| :-: | :-: |
| v2.0.x | Yes |
| < v2.0 | No |

## Security Controls Implemented
- **JWT & JTI Revocation**: HS256 tokens with server-side revocation blacklist.
- **Multi-Tenant Boundaries**: `X-Temple-ID` header validation on every protected endpoint.
- **Immutable Audit Logging**: Append-only audit entries protected against `UPDATE` and `DELETE` queries via SQLAlchemy event hooks.
- **AES-256 Backup Encryption**: Database snapshots encrypted using AES-256 Fernet keys with SHA-256 integrity verification.
- **HTTP Security Headers**: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`.
