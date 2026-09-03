<!-- Web Customer App — Google Sign-In -->

This file provides the web-side Google authentication component for the SmartResort customer web application.

---

## Setup Requirements

1. **Google OAuth 2.0 Client ID**

Create an OAuth 2.0 Client ID in [Google Cloud Console](https://console.cloud.google.com/):
- Application type: **Web application**
- Authorized redirect URIs:
  - Development: `http://localhost:5173/auth/callback`
  - Production: `https://smartresort.local/auth/callback`

2. **Add Client ID to `.env`**

```
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

3. **Enable Google Sign-In in Customer App**

In `apps/web/customer/src/pages/Home.tsx` or a dedicated auth component, add:

```tsx
// Example component: GoogleSignInButton
<button
  onClick={() => {
    // Initialize Google Identity Services
    window.google.accounts.oauth2.initTokenClient({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      scope: 'email profile openid',
      callback: (tokenResponse: any) => {
        // Send tokenResponse.access_token or id_token to backend /auth/google
        // The backend verifies and returns app JWT tokens
        fetch('/api/v1/auth/google', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id_token: tokenResponse.id_token }),
        })
          .then(r => r.json())
          .then(data => {
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/';
          });
      },
    }).requestAccessToken();
  }}
  className="w-full bg-white border border-gray-300 rounded-lg py-3 px-4 flex items-center justify-center gap-3 hover:shadow-md transition shadow-sm text-sm font-medium text-gray-700"
>
  <svg width="20" height="20" viewBox="0 0 48 48">
    <path fill="#4285F4" d="M45 24c0-11.5-9.5-21-21-21s-21 9.5-21 21c0 5.6 2 10.5 5 13.5l-5 5-4.5-4.5c-3 4-4.5 8.5-4.5 13.5 0 7 3.5 13.5 8.5 13.5l5-5 5 5c5 0 8.5-6.5 8.5-13.5z"/>
  </svg>
  Continue with Google
</button>
```

---

## Production Configuration

After deploying with a production domain, update:
- Firebase Console → Authentication → Sign-in method → Google
- Google Cloud Console → OAuth 2.0 Client IDs
- `VITE_GOOGLE_CLIENT_ID` environment variable

---

## Integration Point in Backend

The backend endpoint `/api/v1/auth/google` accepts `{ id_token: ... }` and:
- Verifies the token with Google's OAuth service
- Creates or updates the user (email + Google sub)
- Returns `{ access_token, refresh_token, user }`

The web client does not store Google tokens — only the app's own JWT tokens.
