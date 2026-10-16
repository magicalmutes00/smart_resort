import '../../../core/network/api_client.dart';

class TasksRepository {
  final ApiClient _api;

  TasksRepository(this._api);

  Future<List<Map<String, dynamic>>> getTasks() async {
    try {
      final response = await _api.get('/tasks');
      if (response.statusCode == 200 && response.data is Map) {
        final data = (response.data as Map)['data'] as List?;
        return data?.cast<Map<String, dynamic>>() ?? [];
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<Map<String, dynamic>?> getTask(String id) async {
    try {
      final response = await _api.get('/tasks/$id');
      if (response.statusCode == 200 && response.data is Map) {
        return (response.data as Map).cast<String, dynamic>();
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
