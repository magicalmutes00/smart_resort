import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../network/api_client.dart';
import '../../features/auth/data/auth_repository.dart';
import '../../features/auth/presentation/auth_state_notifier.dart';
import '../../features/auth/domain/auth_state.dart';
import '../../features/tasks/data/tasks_repository.dart';
import '../../features/orders/data/orders_repository.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(apiClientProvider));
});

final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  return AuthStateNotifier(ref.watch(authRepositoryProvider));
});

final tasksRepositoryProvider = Provider<TasksRepository>((ref) {
  return TasksRepository(ref.watch(apiClientProvider));
});

final ordersRepositoryProvider = Provider<OrdersRepository>((ref) {
  return OrdersRepository(ref.watch(apiClientProvider));
});

final ordersProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final repository = ref.watch(ordersRepositoryProvider);
  final orders = await repository.getOrders();
  return orders;
});
