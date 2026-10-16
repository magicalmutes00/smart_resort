import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/providers.dart';

// Placeholder: OrdersScreen uses ordersRepositoryProvider from providers.dart
class OrdersScreen extends ConsumerStatefulWidget {
  const OrdersScreen({super.key});

  @override
  ConsumerState<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends ConsumerState<OrdersScreen> {
  @override
  Widget build(BuildContext context) {
    final ordersAsyncValue = ref.watch(ordersProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Orders')),
      body: ordersAsyncValue.when(
        data: (orders) => orders.isEmpty
            ? const Center(child: Text('No orders found'))
            : ListView.builder(
                itemCount: orders.length,
                itemBuilder: (context, index) {
                  final order = orders[index];
                  return OrderListItem(order: order);
                },
              ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('Failed to load orders: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(ordersProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class OrderListItem extends StatelessWidget {
  final Map<String, dynamic> order;

  const OrderListItem({super.key, required this.order});

  @override
  Widget build(BuildContext context) {
    final id = order['id'] ?? 'Unknown';
    final status = order['status'] ?? 'unknown';
    final orderType = order['order_type'] ?? 'DINE_IN';
    final createdAt = order['created_at'] ?? '';
    final customerName = order['customer_name'] ?? 'Walk-in Customer';

    Color statusColor;
    switch (status.toLowerCase()) {
      case 'pending':
        statusColor = Colors.orange;
        break;
      case 'confirmed':
        statusColor = Colors.blue;
        break;
      case 'preparing':
        statusColor = Colors.purple;
        break;
      case 'ready':
        statusColor = Colors.green;
        break;
      case 'completed':
        statusColor = Colors.grey;
        break;
      case 'cancelled':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ListTile(
        title: Row(
          children: [
            Expanded(child: Text('Order #$id')),
            Chip(
              label: Text('Table ${order['table_number'] ?? 'N/A'}'),
              backgroundColor: Colors.blue.shade100,
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Customer: $customerName'),
            Text('Type: $orderType'),
            Text('Status: $status', style: TextStyle(color: statusColor)),
            Text('Created: $createdAt'),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => _showOrderDetails(context, order),
      ),
    );
  }

  void _showOrderDetails(BuildContext context, Map<String, dynamic> order) {
    showModalBottomSheet(
      context: context,
      builder: (context) => OrderDetailsSheet(order: order),
    );
  }
}

class OrderDetailsSheet extends ConsumerStatefulWidget {
  final Map<String, dynamic> order;
  const OrderDetailsSheet({super.key, required this.order});

  @override
  ConsumerState<OrderDetailsSheet> createState() => _OrderDetailsSheetState();
}

class _OrderDetailsSheetState extends ConsumerState<OrderDetailsSheet> {
  bool _isUpdating = false;

  Future<void> _changeStatus(String newStatus) async {
    final id = widget.order['id']?.toString();
    if (id == null) return;

    setState(() => _isUpdating = true);
    try {
      final repo = ref.read(ordersRepositoryProvider);
      final success = await repo.updateOrderStatus(id: id, status: newStatus);
      if (success && mounted) {
        // Update local state to reflect the new status
        setState(() {
          widget.order['status'] = newStatus;
        });
        // Refresh the orders list
        ref.invalidate(ordersProvider);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Order updated to $newStatus')),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to update order status')),
          );
        }
      }
    } finally {
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final order = widget.order;
    final status = order['status']?.toString().toUpperCase() ?? 'UNKNOWN';

    return Container(
      padding: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text('Order #${order['order_number'] ?? order['id'] ?? 'Unknown'}',
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                ),
                if (order['table_number'] != null)
                  Chip(
                    label: Text('Table ${order['table_number']}'),
                    backgroundColor: Colors.blue.shade100,
                  ),
              ],
            ),
            const SizedBox(height: 16),
            _buildDetailRow('Type:', order['order_type'] ?? 'DINE_IN'),
            _buildDetailRow('Status:', status),
            _buildDetailRow('Created:', order['created_at'] ?? ''),
            _buildDetailRow('Room:', order['room_number'] ?? 'N/A'),
            const SizedBox(height: 16),
            const Text('Items:', style: TextStyle(fontWeight: FontWeight.bold)),
            ...((order['items'] as List?)?.map((item) {
              final itemData = item as Map<String, dynamic>;
              return _buildDetailRow(
                '- ${itemData['menu_item_name'] ?? 'Item'} x${itemData['quantity'] ?? 1}',
                '',
              );
            }).toList() ?? []),
            const SizedBox(height: 16),
            const Text('Kitchen Actions:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            _buildKitchenActions(status),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKitchenActions(String currentStatus) {
    // Define the order workflow for kitchen staff
    final workflow = [
      {'from': 'CREATED', 'to': 'CONFIRMED', 'label': 'Order Taken', 'color': Colors.blue},
      {'from': 'CONFIRMED', 'to': 'ACCEPTED', 'label': 'Cooking', 'color': Colors.deepPurple},
      {'from': 'ACCEPTED', 'to': 'PREPARING', 'label': 'Processing', 'color': Colors.orange},
      {'from': 'PREPARING', 'to': 'READY', 'label': 'Ready to Deliver', 'color': Colors.green},
    ];

    final availableActions = workflow.where((a) => a['from'] == currentStatus).toList();

    if (availableActions.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Text(
          currentStatus == 'READY'
              ? '✓ Order is ready to deliver'
              : currentStatus == 'COMPLETED'
                  ? '✓ Order completed'
                  : 'No actions available for status: $currentStatus',
          style: const TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: availableActions.map((action) {
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: ElevatedButton.icon(
            onPressed: _isUpdating ? null : () => _changeStatus(action['to'] as String),
            icon: _isUpdating
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.restaurant),
            label: Text(action['label'] as String),
            style: ElevatedButton.styleFrom(
              backgroundColor: action['color'] as Color,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
