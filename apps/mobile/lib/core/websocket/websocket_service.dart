import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final String _url;
  final void Function(String event, Map<String, dynamic> data) onEvent;

  WebSocketService({
    required String url,
    required this.onEvent,
  }) : _url = url;

  void connect({String? token}) {
    try {
      final authUrl = token != null ? '$_url?token=$token' : _url;
      _channel = WebSocketChannel.connect(Uri.parse(authUrl));
      _channel!.stream.listen(
        (message) {
          final decoded = jsonDecode(message as String);
          if (decoded['event'] != null && decoded['data'] != null) {
            onEvent(decoded['event'] as String, decoded['data'] as Map<String, dynamic>);
          }
        },
        onError: (_) {},
        onDone: () {},
      );
    } catch (_) {}
  }

  void subscribe(String channel) {
    if (_channel == null) return;
    _channel!.sink.add(jsonEncode({
      'action': 'subscribe',
      'channel': channel,
    }));
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}
