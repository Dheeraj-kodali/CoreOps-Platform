# Contributing Guidelines

Thank you for your interest in contributing to the Temple Visitor Management System Enterprise Edition v2.0.

## 1. Development Principles
- **Offline First**: All mobile edge features must work without an active internet connection.
- **Data Integrity**: Edge mutations must be logged to local SQLite outbox tables before sync.
- **Code Quality**: All Python code must pass `ruff` linter and maintain 100% test pass rate on `pytest`.
- **Tenant Context**: All API routes must enforce tenant scoping (`X-Temple-ID`).

## 2. Setting Up Development Environment
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m pytest
```

## 3. Pull Request Guidelines
1. Create a feature branch (`feature/your-feature-name`).
2. Write unit tests in `backend/tests/` covering your changes.
3. Ensure `python -m pytest` passes with 100% green status.
4. Submit a Pull Request with descriptive documentation.
