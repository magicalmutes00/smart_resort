# SmartResort — Package Identifier Reference

Used for Google OAuth / Firebase / FCM configuration.

---

## Mobile (Flutter)

```
Package Name: com.smartresort.staff
```

Location: `apps/mobile/pubspec.yaml`
Location (Android manifest): `apps/mobile/android/app/src/main/AndroidManifest.xml`
Location (build config): `apps/mobile/android/app/build.gradle`

---

## Web Customer App (React / Vite)

No native package identifier required for web. The web uses OAuth 2.0 redirect flow via the backend.

Base URL for OAuth redirect:
```
http://localhost:5173/auth/callback  (development)
https://smartresort.local/auth/callback  (production)
```

---

## Backend (FastAPI)

Not applicable — the backend is stateless and handles OAuth token exchange, not package identity.
