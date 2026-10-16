import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/google_auth_service.dart';
import '../../../core/network/api_client.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  Map<String, dynamic>? _user;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    setState(() => _loading = true);
    try {
      final api = ApiClient();
      final resp = await api.get('/users/me');
      if (resp.statusCode == 200 && resp.data is Map) {
        setState(() => _user = resp.data as Map<String, dynamic>);
      }
    } catch (e) {
      // stay empty
    }
    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const CircleAvatar(radius: 48, child: Icon(Icons.person, size: 48)),
                  const SizedBox(height: 16),
                  Text(_user?['email']?.toString() ?? 'User', style: Theme.of(context).textTheme.titleLarge),
                  Text(_user?['username']?.toString() ?? '-', style: Theme.of(context).textTheme.bodyMedium),
                  Text(_user?['role']?.toString() ?? '-', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey)),
                  const Divider(height: 32),
                  ListTile(
                    leading: const Icon(Icons.email),
                    title: const Text('Email'),
                    subtitle: Text(_user?['email']?.toString() ?? '—'),
                  ),
                  ListTile(
                    leading: const Icon(Icons.badge),
                    title: const Text('Username'),
                    subtitle: Text(_user?['username']?.toString() ?? '—'),
                  ),
                  ListTile(
                    leading: const Icon(Icons.people),
                    title: const Text('First / Last'),
                    subtitle: Text('${_user?['first_name'] ?? '—'} ${_user?['last_name'] ?? ''}'),
                  ),
                  ListTile(
                    leading: const Icon(Icons.phone),
                    title: const Text('Phone'),
                    subtitle: Text(_user?['phone']?.toString() ?? '—'),
                  ),
                  ListTile(
                    leading: const Icon(Icons.security),
                    title: const Text('Role'),
                    subtitle: Text(_user?['role']?.toString() ?? '—'),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: () async {
                      try {
                        final s = GoogleAuthService(ApiClient());
                        await s.signOut();
                      } catch (_) {
                        // Google/Firebase not configured — ignore
                      }
                      final api = ApiClient();
                      await api.clearTokens();
                      if (mounted) context.go('/login');
                    },
                    icon: const Icon(Icons.logout),
                    label: const Text('Sign Out'),
                  ),
                ],
              ),
            ),
    );
  }
}
