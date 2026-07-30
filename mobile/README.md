# 🛕 Temple Visitor Management System — Version 1.0.0

An enterprise-grade, offline-first Android Visitor Registration & Reception Management System designed for single-device temple reception operations.

---

## 🌟 Key Features

- **2-Touch Reception Journey**: "VISITOR ENTERED" & "VISITOR LEFT" single-tap workflow.
- **Offline-First SQLite Architecture**: 100% operational reliability without internet.
- **Automated WhatsApp Notifications**: Instant welcome gate passes & checkout thank-you notes with dynamic placeholders.
- **Real-Time Reception Dashboard**: Today's visitor metrics, active visitors inside, and average duration counters.
- **Reports & Export Engine**: Filter by Date/Village/Purpose/Status; export to formatted Excel CSV (`Visitors_YYYY_MM_DD.csv`) & Printable PDF.
- **Database Backup & Restore**: Local snapshot backup and warning-protected database restoration.
- **PIN-Protected Admin Portal**: SHA-256 hashed security PIN (`1234`) with 5-minute brute-force lockout.

---

## 📱 Tech Stack

- **Framework**: Flutter 3.x (Dart Null-Safety Strict)
- **State Management**: Flutter Riverpod
- **Database**: SQLite (sqflite v2.3.3+1) with indexed queries
- **Security**: SHA-256 hashing (crypto v3.0.3) & parameterized SQL queries
- **Export Engines**: Custom CSV & HTML Printable PDF engines

---

## 🚀 Quick Setup

1. Clone repository: `git clone https://github.com/temple-management/temple-visitor-app.git`
2. Open `mobile` folder in Android Studio / VS Code.
3. Fetch dependencies: `flutter pub get`
4. Run app: `flutter run --release`

---

## 📄 License
MIT License - See [LICENSE](LICENSE) for details.
