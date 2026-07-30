# 📦 Installation & Deployment Guide — Temple Visitor App v1.0.0

This guide provides step-by-step instructions for deploying the Temple Visitor Management System on an Android reception device.

---

## 📋 System Requirements

- **Device**: Android Phone or Tablet
- **OS Version**: Android 7.0 (API level 24) or higher
- **RAM**: 2 GB Minimum (4 GB Recommended)
- **Storage**: 100 MB free internal storage

---

## 🔧 Installation Steps

### Option A: Direct APK Installation (Recommended)
1. Copy `app-release.apk` to the Android phone storage via USB cable or Bluetooth.
2. Open **File Manager** on the phone and tap `app-release.apk`.
3. If prompted, enable **"Install from Unknown Sources"** in Android Settings.
4. Tap **Install** and launch **Sri Kalki Seva Alayam**.

### Option B: Building from Source
```bash
cd mobile
flutter pub get
flutter build apk --release
```
The compiled APK will be generated at `build/app/outputs/flutter-apk/app-release.apk`.

---

## ⚙️ Initial Configuration
1. Launch app on reception device.
2. Default login credentials / direct entry to reception shell.
3. Access Admin Settings via ⚙️ icon (Default PIN: `1234`).
4. Update **Temple Information** and **Admin PIN**.
