class Environment {
  Environment._();

  // Android emulator reaches the host machine via 10.0.2.2.
  // For a physical device, pass the host's LAN IP instead:
  //   flutter run --dart-define=API_BASE_URL=http://<host-ip>:8000/api/v1
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  static const String wsBaseUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: 'ws://10.0.2.2:8000/ws',
  );

  static const bool isDebug = bool.fromEnvironment('DEBUG', defaultValue: true);
}
