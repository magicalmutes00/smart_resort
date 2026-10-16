class Environment {
  Environment._();

  // Production default is the live Render backend. Override for local
  // development at build/run time; Android emulator reaches the host via
  // 10.0.2.2, e.g.:
  //   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1 --dart-define=WS_BASE_URL=ws://10.0.2.2:8000/ws
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://smartresort-backend-8rac.onrender.com/api/v1',
  );

  static const String wsBaseUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: 'wss://smartresort-backend-8rac.onrender.com/ws',
  );

  static const bool isDebug = bool.fromEnvironment('DEBUG', defaultValue: true);
}
