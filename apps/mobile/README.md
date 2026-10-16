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

Configure API base URL:

```bash
flutter run --dart-define=API_BASE_URL=http://your-server:8000/api/v1
flutter run --dart-define=WS_BASE_URL=ws://your-server:8000/ws
```

Default Android emulator URL is `10.0.2.2` (host machine).

## Build

```bash
flutter build apk --release
flutter build ios --release
```
