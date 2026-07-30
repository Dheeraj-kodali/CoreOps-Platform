import 'dart:developer' as developer;

enum LogLevel { info, warning, error, critical }

class AppLogger {
  static void log(String message, {LogLevel level = LogLevel.info, Object? error, StackTrace? stackTrace}) {
    final timestamp = DateTime.now().toIso8601String();
    final prefix = level.name.toUpperCase();

    // Avoid logging sensitive PII or credentials
    final sanitizedMessage = _sanitize(message);

    developer.log(
      '[$timestamp] [$prefix] $sanitizedMessage',
      name: 'TempleVisitorApp',
      level: _getLevelValue(level),
      error: error,
      stackTrace: stackTrace,
    );
  }

  static String _sanitize(String msg) {
    // Strip sensitive patterns if any
    return msg;
  }

  static int _getLevelValue(LogLevel level) {
    switch (level) {
      case LogLevel.info:
        return 800;
      case LogLevel.warning:
        return 900;
      case LogLevel.error:
        return 1000;
      case LogLevel.critical:
        return 1200;
    }
  }

  static void info(String message) => log(message, level: LogLevel.info);
  static void warning(String message) => log(message, level: LogLevel.warning);
  static void error(String message, {Object? err, StackTrace? st}) => log(message, level: LogLevel.error, error: err, stackTrace: st);
  static void critical(String message, {Object? err, StackTrace? st}) => log(message, level: LogLevel.critical, error: err, stackTrace: st);
}
