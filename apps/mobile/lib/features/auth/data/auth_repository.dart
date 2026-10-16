import '../../../core/network/api_client.dart';
import '../../../app/config/environment.dart';
import '../domain/auth_state.dart';

class AuthRepository {
  final ApiClient _api;

  AuthRepository(this._api);

  Future<({bool success, User? user, String? error})> login({
    required String email,
    required String password,
  }) async {
    print('LOGIN REQUEST URL: POST ${Environment.apiBaseUrl}/auth/login');
    print('EMAIL: $email');
    try {
      final response = await _api.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;

        // Save tokens
        final accessToken = data['access_token'] as String?;
        final refreshToken = data['refresh_token'] as String?;
        if (accessToken != null && refreshToken != null) {
          await _api.saveTokens(
            accessToken: accessToken,
            refreshToken: refreshToken,
          );
        }

        final userData = data['user'] as Map<String, dynamic>?;
        return (
          success: true,
          user: userData != null ? User.fromJson(userData) : null,
          error: null,
        );
      }
      return (success: false, user: null, error: 'Login failed');
    } catch (e) {
      return (success: false, user: null, error: e.toString());
    }
  }

  Future<User?> getCurrentUser() async {
    try {
      final response = await _api.get('/auth/me');
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        return User.fromJson(data);
      }
    } catch (_) {}
    return null;
  }

  Future<void> logout() async {
    await _api.clearTokens();
  }
}
