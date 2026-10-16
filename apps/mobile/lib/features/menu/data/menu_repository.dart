import '../../../core/network/api_client.dart';

class MenuRepository {
  final ApiClient _api;

  MenuRepository(this._api);

  Future<List<Map<String, dynamic>>> getCategories() async {
    try {
      final response = await _api.get('/menu/categories');
      final data = response.data is Map ? (response.data as Map)['data'] as List? : null;
      return data?.cast<Map<String, dynamic>>() ?? [];
    } catch (e) {
      return [];
    }
  }

  Future<bool> addItem({
    required String name,
    String? description,
    required double price,
    required int prepTime,
    required String categoryId,
  }) async {
    try {
      final payload = {
        'name': name,
        'description': description,
        'base_price': price,
        'preparation_time': prepTime,
        'category_id': categoryId,
        'is_available': true,
      };
      final response = await _api.post('/menu/items', data: payload);
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }
}
