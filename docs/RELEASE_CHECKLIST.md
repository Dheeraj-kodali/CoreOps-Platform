# Release & Upgrade Checklist — Temple Visitor Management System Enterprise Edition v2.0

## Pre-Release Quality Gates
- [x] All 43 backend Pytest tests passing 100%.
- [x] All 4 stress benchmark tests passing 100%.
- [x] Zero Ruff linter warnings or compilation errors (`python -m ruff check app`).
- [x] Zero TypeScript compilation errors (`npx tsc --noEmit`).
- [x] All 12 Flutter mobile tests passing (`flutter test`).
- [x] Mobile Release APK compiled successfully (`flutter build apk --release`).
- [x] Database SHA-256 backup created & verified.

## Upgrade Procedure
1. Create pre-upgrade SQLite database backup snapshot.
2. Pull latest release code.
3. Verify environment variables in `config/production.env`.
4. Start server & execute `/health` verification.
