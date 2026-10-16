# SmartResort Mobile (Flutter)

Production-grade Flutter staff application for SmartResort.

## Setup

```bash
flutter pub get
flutter run
```

## Architecture

Feature-first organization with data/domain/presentation layers per feature. State management with Riverpod, navigation with GoRouter, networking with Dio, and secure storage for tokens.

```
lib/
├── main.dart
├── app/
│   ├── app.dart
│   ├── router.dart
│   ├── theme/
│   └── config/
├── core/
│   ├── network/
│   ├── providers/
│   └── websocket/
└── features/
    ├── auth/
    ├── dashboard/
    ├── tasks/
    ├── orders/
    └── profile/
```

## Environment

Configure API base URL (defaults to the live Render backend):

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1 --dart-define=WS_BASE_URL=ws://10.0.2.2:8000/ws
```

Use the override above for local development. `10.0.2.2` is the Android emulator's host-machine address. Changing the default requires a full rebuild, not hot reload.

## Build

```bash
flutter build apk --release
flutter build ios --release
```
