import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/auth_state.dart';
import '../data/auth_repository.dart';

class AuthStateNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;

  AuthStateNotifier(this._repository) : super(const AuthState());

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    final result = await _repository.login(email: email, password: password);

    if (result.success && result.user != null) {
      state = state.copyWith(
        isAuthenticated: true,
        isLoading: false,
        user: result.user,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error ?? 'Login failed',
      );
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AuthState();
  }

  Future<void> checkAuth() async {
    final user = await _repository.getCurrentUser();
    if (user != null) {
      state = state.copyWith(isAuthenticated: true, user: user);
    }
  }
}
