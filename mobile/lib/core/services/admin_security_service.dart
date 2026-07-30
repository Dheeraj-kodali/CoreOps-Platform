import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AdminSecurityService {
  static const String _pinHashKey = 'admin_pin_hash_v1';
  static const String _failedAttemptsKey = 'admin_failed_attempts_v1';
  static const String _lockoutTimestampKey = 'admin_lockout_ts_v1';

  static const String _defaultPin = '1234';

  /// Hash PIN using SHA-256 for secure local storage
  static String _hashPin(String pin) {
    final bytes = utf8.encode('temple_salt_$pin');
    return sha256.convert(bytes).toString();
  }

  /// Verify entered PIN against stored SHA-256 hash with lockout handling
  static Future<Map<String, dynamic>> verifyPin(String enteredPin) async {
    final prefs = await SharedPreferences.getInstance();

    // Check Lockout Status (5 failed attempts locks for 5 mins)
    final lockoutTs = prefs.getInt(_lockoutTimestampKey) ?? 0;
    final nowMs = DateTime.now().millisecondsSinceEpoch;
    final remainingLockMs = (lockoutTs + 5 * 60 * 1000) - nowMs;

    if (remainingLockMs > 0) {
      final remainingMins = (remainingLockMs / (60 * 1000)).ceil();
      return {
        'success': false,
        'isLocked': true,
        'message': 'Account locked due to 5 failed attempts. Try again in $remainingMins minute(s).',
      };
    }

    final storedHash = prefs.getString(_pinHashKey) ?? _hashPin(_defaultPin);
    final enteredHash = _hashPin(enteredPin);

    if (enteredHash == storedHash) {
      // Reset failed attempts on success
      await prefs.setInt(_failedAttemptsKey, 0);
      await prefs.remove(_lockoutTimestampKey);
      return {'success': true, 'isLocked': false};
    } else {
      final failedCount = (prefs.getInt(_failedAttemptsKey) ?? 0) + 1;
      await prefs.setInt(_failedAttemptsKey, failedCount);

      if (failedCount >= 5) {
        await prefs.setInt(_lockoutTimestampKey, nowMs);
        return {
          'success': false,
          'isLocked': true,
          'message': '5 incorrect PIN attempts. Locked out for 5 minutes.',
        };
      }

      final remainingAttempts = 5 - failedCount;
      return {
        'success': false,
        'isLocked': false,
        'message': 'Incorrect PIN. $remainingAttempts attempt(s) remaining before lockout.',
      };
    }
  }

  /// Update Admin PIN with SHA-256 hashing
  static Future<bool> changePin(String currentPin, String newPin) async {
    final verifyResult = await verifyPin(currentPin);
    if (verifyResult['success'] != true) return false;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_pinHashKey, _hashPin(newPin));
    return true;
  }
}
