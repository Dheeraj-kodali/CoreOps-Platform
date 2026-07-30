import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';
import 'package:temple_visitor_app/core/services/storage_service.dart';
import 'package:temple_visitor_app/models/user_model.dart';

class AuthRepository {
  /// Standalone 100% Offline SQLite Authentication
  Future<UserModel?> login({required String username, required String password}) async {
    try {
      AppLogger.info('Attempting local SQLite authentication for username: $username');

      final userMap = await SQLiteDatabase.getUserByUsername(username.trim());
      if (userMap == null) {
        AppLogger.warning('Authentication failed: User $username not found in SQLite database');
        return null;
      }

      final inputHash = SQLiteDatabase.hashPassword(password);
      final storedHash = userMap['password_hash'].toString();

      if (inputHash != storedHash) {
        AppLogger.warning('Authentication failed: Invalid password for username $username');
        return null;
      }

      final user = UserModel(
        id: userMap['id'].toString(),
        username: userMap['username'].toString(),
        fullName: userMap['username'] == 'admin' ? 'Temple Administrator' : userMap['username'].toString(),
        email: '${userMap['username']}@kalkiseva.org',
        phoneNumber: '+91 98765 43210',
      );

      // Save user session locally in SharedPreferences
      await StorageService.saveUser(user.toJson());
      AppLogger.info('Local SQLite Authentication successful for user: ${user.username}');
      return user;
    } catch (e, st) {
      AppLogger.error('SQLite Login Error', err: e, st: st);
      return null;
    }
  }

  Future<void> logout() async {
    AppLogger.info('Clearing local session during logout');
    await StorageService.clearAll();
  }

  Future<UserModel?> getCurrentUser() async {
    final userMap = await StorageService.getUser();
    if (userMap != null) {
      return UserModel.fromJson(userMap);
    }
    return null;
  }
}
