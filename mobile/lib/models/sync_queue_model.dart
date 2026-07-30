import 'dart:convert';
import 'dart:math';

/// SyncQueueModel represents an atomic outbox event pending synchronization.
class SyncQueueModel {
  final int? queueId;
  final String eventId;
  final String templeId;
  final String entityType;
  final String entityId;
  final String operation;
  final Map<String, dynamic> payload;
  final String status; // 'PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'DEAD_LETTER'
  final int retryCount;
  final int maxRetries;
  final int? nextRetryAt; // Unix timestamp in seconds
  final String? errorMessage;
  final int clientTimestamp; // Unix timestamp in milliseconds
  final int? serverSyncedAt;
  final String createdAt;
  final String updatedAt;

  SyncQueueModel({
    this.queueId,
    required this.eventId,
    this.templeId = 'TEMPLE_MAIN',
    required this.entityType,
    required this.entityId,
    required this.operation,
    required this.payload,
    this.status = 'PENDING',
    this.retryCount = 0,
    this.maxRetries = 10,
    this.nextRetryAt,
    this.errorMessage,
    required this.clientTimestamp,
    this.serverSyncedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Calculate next retry timestamp using Exponential Backoff with Full Jitter.
  /// Formula: delay = random(0, min(maxBackoff, base * 2^retryCount))
  static int calculateNextRetryTimestamp(
    int retryCount, {
    int baseDelaySeconds = 2,
    int maxBackoffSeconds = 3600,
    Random? randomOverride,
  }) {
    final rand = randomOverride ?? Random();
    final exponential = baseDelaySeconds * pow(2, retryCount).toInt();
    final cap = min(maxBackoffSeconds, exponential);
    final jitteredDelay = rand.nextInt(cap + 1);
    final currentEpochSeconds = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    return currentEpochSeconds + jitteredDelay;
  }

  Map<String, dynamic> toMap() {
    return {
      if (queueId != null) 'queue_id': queueId,
      'event_id': eventId,
      'temple_id': templeId,
      'entity_type': entityType,
      'entity_id': entityId,
      'operation': operation,
      'payload': jsonEncode(payload),
      'status': status,
      'retry_count': retryCount,
      'max_retries': maxRetries,
      'next_retry_at': nextRetryAt,
      'error_message': errorMessage,
      'client_timestamp': clientTimestamp,
      'server_synced_at': serverSyncedAt,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }

  factory SyncQueueModel.fromMap(Map<String, dynamic> map) {
    Map<String, dynamic> parsedPayload = {};
    if (map['payload'] != null) {
      if (map['payload'] is String) {
        try {
          parsedPayload = jsonDecode(map['payload'] as String) as Map<String, dynamic>;
        } catch (_) {
          parsedPayload = {'raw': map['payload']};
        }
      } else if (map['payload'] is Map) {
        parsedPayload = Map<String, dynamic>.from(map['payload'] as Map);
      }
    }

    return SyncQueueModel(
      queueId: map['queue_id'] as int?,
      eventId: map['event_id'] as String,
      templeId: (map['temple_id'] ?? 'TEMPLE_MAIN') as String,
      entityType: map['entity_type'] as String,
      entityId: map['entity_id'] as String,
      operation: map['operation'] as String,
      payload: parsedPayload,
      status: (map['status'] ?? 'PENDING') as String,
      retryCount: (map['retry_count'] as int?) ?? 0,
      maxRetries: (map['max_retries'] as int?) ?? 10,
      nextRetryAt: map['next_retry_at'] as int?,
      errorMessage: map['error_message'] as String?,
      clientTimestamp: (map['client_timestamp'] as int?) ?? DateTime.now().millisecondsSinceEpoch,
      serverSyncedAt: map['server_synced_at'] as int?,
      createdAt: (map['created_at'] ?? DateTime.now().toIso8601String()) as String,
      updatedAt: (map['updated_at'] ?? DateTime.now().toIso8601String()) as String,
    );
  }

  SyncQueueModel copyWith({
    int? queueId,
    String? eventId,
    String? templeId,
    String? entityType,
    String? entityId,
    String? operation,
    Map<String, dynamic>? payload,
    String? status,
    int? retryCount,
    int? maxRetries,
    int? nextRetryAt,
    String? errorMessage,
    int? clientTimestamp,
    int? serverSyncedAt,
    String? createdAt,
    String? updatedAt,
  }) {
    return SyncQueueModel(
      queueId: queueId ?? this.queueId,
      eventId: eventId ?? this.eventId,
      templeId: templeId ?? this.templeId,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      operation: operation ?? this.operation,
      payload: payload ?? this.payload,
      status: status ?? this.status,
      retryCount: retryCount ?? this.retryCount,
      maxRetries: maxRetries ?? this.maxRetries,
      nextRetryAt: nextRetryAt ?? this.nextRetryAt,
      errorMessage: errorMessage ?? this.errorMessage,
      clientTimestamp: clientTimestamp ?? this.clientTimestamp,
      serverSyncedAt: serverSyncedAt ?? this.serverSyncedAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
