class AppConfig {
  static const String appName = 'Sri Kalki Seva Alayam';
  
  // Dynamic Environment Configuration via compile-time --dart-define flag
  // Production default: https://coreops-platform.onrender.com/api/v1
  static const String apiBaseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'https://coreops-platform.onrender.com/api/v1',
  );
  
  static const String fallbackApiBaseUrl = 'https://coreops-platform.onrender.com/api/v1';
  static const int connectTimeoutMs = 30000;
  static const int receiveTimeoutMs = 30000;
}
