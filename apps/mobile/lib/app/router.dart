import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/providers/providers.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/auth/presentation/splash_screen.dart';
import '../features/dashboard/presentation/dashboard_screen.dart';
import '../features/orders/presentation/orders_screen.dart';
import '../features/tasks/presentation/tasks_screen.dart';
import '../features/tasks/presentation/task_detail_screen.dart';
import '../features/profile/presentation/profile_screen.dart';
import '../features/menu/presentation/menu_item_form_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/app/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/app/tasks',
            builder: (context, state) => const TasksScreen(),
            routes: [
              GoRoute(
                path: ':id',
                builder: (context, state) => TaskDetailScreen(
                  taskId: state.pathParameters['id']!,
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/app/orders',
            builder: (context, state) => const OrdersScreen(),
          ),
          GoRoute(
            path: '/app/menu',
            builder: (context, state) => const MenuItemFormScreen(),
          ),
          GoRoute(
            path: '/app/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
    ],
  );
});

class MainShell extends ConsumerWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);
    final role = authState.user?.role ?? '';
    final canAddMenu = ['SUPER_ADMIN', 'OWNER', 'MANAGER'].contains(role);

    final destinations = [
      const NavigationDestination(icon: Icon(Icons.dashboard_outlined), label: 'Dashboard'),
      const NavigationDestination(icon: Icon(Icons.task_outlined), label: 'Tasks'),
      const NavigationDestination(icon: Icon(Icons.receipt_long_outlined), label: 'Orders'),
      if (canAddMenu)
        const NavigationDestination(icon: Icon(Icons.restaurant_menu_outlined), label: 'Menu'),
      const NavigationDestination(icon: Icon(Icons.person_outlined), label: 'Profile'),
    ];

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _calculateSelectedIndex(context, destinations.length, canAddMenu),
        onDestinationSelected: (index) => _onItemTapped(index, context, canAddMenu),
        destinations: destinations,
      ),
    );
  }

  int _calculateSelectedIndex(BuildContext context, int totalDestinations, bool canAddMenu) {
    final location = GoRouterState.of(context).uri.path;
    int base = 0;
    if (location.startsWith('/app/tasks')) base = 1;
    if (location.startsWith('/app/orders')) base = 2;
    if (location.startsWith('/app/menu')) base = canAddMenu ? 3 : -1;
    if (location.startsWith('/app/profile')) base = canAddMenu ? 4 : 3;
    if (location.startsWith('/app/dashboard')) base = 0;
    return base;
  }

  void _onItemTapped(int index, BuildContext context, bool canAddMenu) {
    if (!canAddMenu) {
      switch (index) {
        case 0: context.go('/app/dashboard'); break;
        case 1: context.go('/app/tasks'); break;
        case 2: context.go('/app/orders'); break;
        case 3: context.go('/app/profile'); break;
      }
      return;
    }
    switch (index) {
      case 0: context.go('/app/dashboard'); break;
      case 1: context.go('/app/tasks'); break;
      case 2: context.go('/app/orders'); break;
      case 3: context.go('/app/menu'); break;
      case 4: context.go('/app/profile'); break;
    }
  }
}
