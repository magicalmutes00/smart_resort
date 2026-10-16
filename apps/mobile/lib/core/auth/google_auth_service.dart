import 'package:google_sign_in/google_sign_in.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb_auth;

import '../network/api_client.dart';

class GoogleAuthService {
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
    clientId: null,
  );

  final ApiClient _api;

  GoogleAuthService(this._api);

  Future<String?> signInAndGetIdToken() async {
    try {
      final account = await _googleSignIn.signIn();
      if (account == null) return null;
      final auth = await account.authentication;
      return auth.idToken ?? auth.accessToken;
    } catch (e) {
      print('Google sign-in error: $e');
      return null;
    }
  }

  Future<String?> signInWithFirebase() async {
    try {
      final account = await _googleSignIn.signIn();
      if (account == null) return null;
      final auth = await account.authentication;
      final credential = fb_auth.GoogleAuthProvider.credential(
        accessToken: auth.accessToken,
        idToken: auth.idToken,
      );
      final userCredential = await fb_auth.FirebaseAuth.instance.signInWithCredential(credential);
      return await userCredential.user?.getIdToken();
    } catch (_) {
      return null;
    }
  }

  Future<void> signOut() async {
    await _googleSignIn.signOut();
    await fb_auth.FirebaseAuth.instance.signOut();
  }

  Future<({bool success, Map<String, dynamic>? user, String? error})>
      authenticateWithBackend(String idToken) async {
    try {
      final response = await _api.post(
        '/auth/google',
        data: {'id_token': idToken},
      );
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final accessToken = data['access_token'] as String?;
        final refreshToken = data['refresh_token'] as String?;
        if (accessToken != null && refreshToken != null) {
          await _api.saveTokens(
            accessToken: accessToken,
            refreshToken: refreshToken,
          );
        }
        return (
          success: true,
          user: data['user'] as Map<String, dynamic>?,
          error: null,
        );
      }
      return (
        success: false,
        user: null,
        error: 'Authentication failed (${response.statusCode})',
      );
    } catch (e) {
      return (success: false, user: null, error: e.toString());
    }
  }
}
