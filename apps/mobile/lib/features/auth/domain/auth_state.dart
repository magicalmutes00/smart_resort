import 'package:flutter/foundation.dart';

@immutable
class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final String? error;
  final User? user;

  const AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.error,
    this.user,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    bool? isLoading,
    String? error,
    User? user,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      user: user ?? this.user,
    );
  }
}

class User {
  final String id;
  final String email;
  final String username;
  final String? firstName;
  final String? lastName;
  final String role;
  final List<String> permissions;

  User({
    required this.id,
    required this.email,
    required this.username,
    this.firstName,
    this.lastName,
    required this.role,
    required this.permissions,
  });

  User.fromJson(Map<String, dynamic> json)
      : id = (json['id']?.toString()) ?? '',
        email = (json['email'] as String?) ?? '',
        username = (json['username'] as String?) ?? json['email'] as String? ?? '',
        firstName = json['first_name'] as String?,
        lastName = json['last_name'] as String?,
        role = (json['role'] as String?) ?? 'user',
        permissions = List<String>.from((json['permissions'] as List?) ?? []);

  String get displayName => [firstName, lastName].whereType<String>().join(' ').isEmpty
      ? username
      : [firstName, lastName].whereType<String>().join(' ');
}
