# SmartResort — SHA Fingerprints (Google Auth Setup)

These fingerprints are required to configure Google OAuth on:
- **Firebase Console** (`Project settings > Your apps > Android`)
- **Google Cloud Console** (`APIs & Services > Credentials > OAuth 2.0 Client IDs`)

---

## Flutter App Package Name

```
com.smartresort.staff
```

(Defined in `pubspec.yaml` and `android/app/build.gradle`)

---

## Debug Certificate (Development)

The debug keystore is located at:

```
# Linux / macOS
~/.android/debug.keystore

# Windows
%USERPROFILE%\.android\debug.keystore
```

To get the actual fingerprints:

```bash
keytool -list -v \
  -keystore ~/.android/debug.keystore \
  -alias androiddebugkey \
  -storepass android \
  -keypass android
```

Output shows (ACTUAL VALUES FROM YOUR KEYSTORE):
```
Certificate fingerprints:
    SHA1:  7A:0B:28:45:EF:A3:87:BA:80:88:37:BF:D4:DC:AC:82:07:B8:49:18
    SHA256: B1:62:34:E5:B9:DC:69:38:FB:61:EF:B8:61:05:C9:B4:BF:54:50:3E:53:B8:B7:2C:59:7C:B4:88:1B:2B:D3:1A
```

Replace the `...` placeholders above with your real output when configuring Firebase / Google Cloud.

---

## Release Certificate (Production)

Generate a release keystore (only once per release certificate):

```bash
keytool -genkey -v \
  -keystore android/app/upload-keystore.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias upload-key
```

Then get fingerprints:

```bash
keytool -list -v -keystore android/app/upload-keystore.jks -alias upload-key
```

---

## Adding Fingerprints to Google / Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/) → Project settings → Your apps → Android
2. Add fingerprint (SHA-1 or SHA-256) with package `com.smartresort.staff`
3. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
4. Edit OAuth 2.0 Client ID for Android and add the same package + fingerprint
5. Download updated `google-services.json` → place in `android/app/`
6. Download updated `GoogleService-Info.plist` → place in `ios/` (for iOS auth)

---

## Note on Project Setup

This file only provides the structure and instructions. Actual fingerprints are computed from the developer's local keystore, not hardcoded. After generating fingerprints, the real values should be pasted here (replacing `...`) for the team's reference.
