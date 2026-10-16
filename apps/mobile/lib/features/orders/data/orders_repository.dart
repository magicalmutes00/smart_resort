import 'package:flutter/foundation.dart';
import '../../../core/network/api_client.dart';

class OrdersRepository {
  final ApiClient _api;

  OrdersRepository(this._api);

  Future<List<Map<String, dynamic>>> getOrders() async {
    try {
      final response = await _api.get('/orders/');
      if (response.statusCode == 200 && response.data is Map) {
        final data = (response.data as Map)['data'] as List?;
        return data?.cast<Map<String, dynamic>>() ?? [];
      }
      debugPrint('OrdersRepository.getOrders: unexpected status ${response.statusCode}');
      return [];
    } catch (e) {
      debugPrint('OrdersRepository.getOrders error: $e');
      return [];
    }
  }

  Future<bool> updateOrderStatus({required String id, required String status}) async {
    try {
      final response = await _api.patch('/orders/$id/status', data: {'status': status});
      if (response.statusCode != 200) {
        debugPrint('OrdersRepository.updateOrderStatus: ${response.statusCode}');
      }
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('OrdersRepository.updateOrderStatus error: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>?> getOrder(String id) async {
    try {
      final response = await _api.get('/orders/$id/');
      if (response.statusCode == 200 && response.data is Map) {
        return (response.data as Map).cast<String, dynamic>();
      }
      return null;
    } catch (e) {
      debugPrint('OrdersRepository.getOrder error: $e');
      return null;
    }
  }
}
