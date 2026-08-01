import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:temple_visitor_app/core/config/app_config.dart';
import 'package:temple_visitor_app/core/repositories/sync_repository.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  WebSocket? _webSocket;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  bool _isConnecting = false;

  final StreamController<Map<String, dynamic>> _eventController =
      StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get onEvent => _eventController.stream;

  /// Connect to Backend Real-Time WebSocket Event Stream
  Future<void> connect({String? customUrl}) async {
    if (_webSocket != null || _isConnecting) return;
    _isConnecting = true;

    // Production WebSocket URL derived from AppConfig.apiBaseUrl
    final defaultWsUrl = AppConfig.apiBaseUrl
        .replaceFirst('https://', 'wss://')
        .replaceFirst('http://', 'ws://') + '/ws';
    final wsUrl = customUrl ?? defaultWsUrl;

    try {
      AppLogger.info('[WebSocket] Connecting to $wsUrl...');
      _webSocket = await WebSocket.connect(wsUrl).timeout(const Duration(seconds: 5));
      _isConnecting = false;
      AppLogger.info('[WebSocket] Connected successfully to Real-Time Event Hub.');

      // Start ping heartbeat timer every 15 seconds
      _startPingTimer();

      _webSocket!.listen(
        (data) {
          try {
            if (data is String) {
              if (data == 'pong') return;
              final map = jsonDecode(data) as Map<String, dynamic>;
              _eventController.add(map);

              final event = map['event'] as String?;
              if (event != null && event != 'CONNECTED') {
                AppLogger.info('[WebSocket Event Received] $event: Auto-syncing local DB...');
                // Trigger background outbox queue sync on incoming event
                SyncRepository().processSyncQueue().catchError((_) => false);
              }
            }
          } catch (e) {
            AppLogger.error('[WebSocket] Message parsing error: $e');
          }
        },
        onDone: () {
          AppLogger.warning('[WebSocket] Connection closed. Scheduling reconnect...');
          _cleanup();
          _scheduleReconnect(wsUrl);
        },
        onError: (error) {
          AppLogger.error('[WebSocket] Connection error: $error');
          _cleanup();
          _scheduleReconnect(wsUrl);
        },
      );
    } catch (e) {
      _isConnecting = false;
      AppLogger.error('[WebSocket] Connection failed: $e. Scheduling reconnect...');
      _cleanup();
      _scheduleReconnect(wsUrl);
    }
  }

  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      if (_webSocket != null && _webSocket!.readyState == WebSocket.open) {
        _webSocket!.add('ping');
      }
    });
  }

  void _scheduleReconnect(String wsUrl) {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      connect(customUrl: wsUrl);
    });
  }

  void _cleanup() {
    _webSocket = null;
    _isConnecting = false;
    _pingTimer?.cancel();
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _webSocket?.close();
    _webSocket = null;
    _isConnecting = false;
  }
}
