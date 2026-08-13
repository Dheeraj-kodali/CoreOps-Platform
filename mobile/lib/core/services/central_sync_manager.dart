import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:temple_visitor_app/core/repositories/sync_repository.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';
import 'package:temple_visitor_app/core/services/connectivity_service.dart';
import 'package:temple_visitor_app/core/services/websocket_service.dart';

import 'package:temple_visitor_app/core/database/sqlite_database.dart';

enum SyncEventType {
  registration,
  checkout,
  profileUpdate,
  deletion,
  backgroundSync,
  offlineQueue,
  webSocket,
  appResume,
  pullToRefresh,
  connectivityOnline,
}

class SyncEvent {
  final SyncEventType type;
  final String reason;
  final DateTime timestamp;
  final bool success;
  final Map<String, dynamic>? extraData;

  SyncEvent({
    required this.type,
    required this.reason,
    required this.timestamp,
    required this.success,
    this.extraData,
  });
}

class CentralSyncState {
  final int pendingCount;
  final bool isSyncing;
  final String? lastMessage;
  final DateTime? lastSyncTime;
  final Map<String, dynamic> todayStats;

  CentralSyncState({
    required this.pendingCount,
    required this.isSyncing,
    this.lastMessage,
    this.lastSyncTime,
    this.todayStats = const {
      'total_visitors': 0,
      'visitors_inside': 0,
      'total_records': 0,
      'visitors_left': 0,
    },
  });

  CentralSyncState copyWith({
    int? pendingCount,
    bool? isSyncing,
    String? lastMessage,
    DateTime? lastSyncTime,
    Map<String, dynamic>? todayStats,
  }) {
    return CentralSyncState(
      pendingCount: pendingCount ?? this.pendingCount,
      isSyncing: isSyncing ?? this.isSyncing,
      lastMessage: lastMessage ?? this.lastMessage,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      todayStats: todayStats ?? this.todayStats,
    );
  }
}

class CentralSyncManager extends StateNotifier<CentralSyncState> with WidgetsBindingObserver {
  static final CentralSyncManager instance = CentralSyncManager._internal();

  final SyncRepository _syncRepo = SyncRepository();
  final VisitorRepository _visitorRepo = VisitorRepository();
  final ConnectivityService _connectivity = ConnectivityService();

  final StreamController<SyncEvent> _syncEventController = StreamController<SyncEvent>.broadcast();
  Stream<SyncEvent> get onSyncCompleted => _syncEventController.stream;

  StreamSubscription<bool>? _connectivitySub;
  StreamSubscription<dynamic>? _wsSub;
  Timer? _periodicTimer;

  bool _initialized = false;

  bool _hasPendingSyncRequest = false;

  CentralSyncManager._internal() : super(CentralSyncState(pendingCount: 0, isSyncing: false)) {
    _init();
  }

  factory CentralSyncManager() => instance;

  void _init() {
    if (_initialized) return;
    _initialized = true;

    WidgetsBinding.instance.addObserver(this);
    WebSocketService().connect();

    // 1. Listen to WebSocket events
    _wsSub = WebSocketService().onEvent.listen((eventData) {
      AppLogger.info('[CentralSyncManager] Incoming WebSocket event received. Triggering full sync...');
      triggerSync(type: SyncEventType.webSocket, reason: 'Incoming WebSocket Event');
    });

    // 2. Listen to network connectivity restoration
    _connectivitySub = _connectivity.onConnectivityChanged.listen((isOnline) {
      if (isOnline) {
        AppLogger.info('[CentralSyncManager] Device came online. Triggering outbox and ledger sync...');
        triggerSync(type: SyncEventType.connectivityOnline, reason: 'Connectivity Online Restoration');
      }
    });

    // 3. Fast Periodic background sync timer (every 3s if pending items exist)
    _periodicTimer = Timer.periodic(const Duration(seconds: 3), (_) async {
      final count = await _syncRepo.getPendingCount();
      state = state.copyWith(pendingCount: count);
      if (count > 0 && !state.isSyncing) {
        final online = await _connectivity.isOnline();
        if (online) {
          triggerSync(type: SyncEventType.backgroundSync, reason: 'Periodic Background Sync');
        }
      }
    });

    // Initial sync check
    refreshQueueCount();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState appState) {
    if (appState == AppLifecycleState.resumed) {
      AppLogger.info('[CentralSyncManager] App resumed. Triggering full sync refresh...');
      triggerSync(type: SyncEventType.appResume, reason: 'Application Resumed');
    }
  }

  Future<void> refreshQueueCount() async {
    final count = await _syncRepo.getPendingCount();
    state = state.copyWith(pendingCount: count);
  }

  /// Single Entry Point for All Synchronization & Refresh Operations
  Future<bool> triggerSync({
    SyncEventType type = SyncEventType.pullToRefresh,
    String reason = 'Manual Refresh',
  }) async {
    if (state.isSyncing) {
      _hasPendingSyncRequest = true;
      AppLogger.info('[CentralSyncManager] Sync already in progress. Queued follow-up sync ($reason).');
      return false;
    }

    state = state.copyWith(isSyncing: true, lastMessage: null);
    AppLogger.info('[CentralSyncManager] Starting full synchronization cycle (Reason: $reason)...');

    bool overallSuccess = true;
    try {
      // Step 1: Process offline outbox queue to backend
      final queueSuccess = await _syncRepo.processSyncQueue();
      await refreshQueueCount();

      // Step 2: Download remote today's Daily Ledger and update local SQLite
      await _visitorRepo.syncRemoteLedgerSessions();

      // Step 3: Fetch live production dashboard statistics
      final localStats = await _visitorRepo.getTodayStatistics();
      final clearedAtStr = await SQLiteDatabase.getDataClearedAt();
      final liveStats = (clearedAtStr != null && (localStats['total_visitors'] ?? 0) == 0)
          ? null
          : await _visitorRepo.fetchLiveDashboardStats();

      final combinedStats = Map<String, dynamic>.from(localStats);
      if (liveStats != null) {
        combinedStats['total_visitors'] = liveStats['todays_visitors'] ?? localStats['total_visitors'];
        combinedStats['visitors_inside'] = liveStats['visitors_inside'] ?? localStats['visitors_inside'];
        combinedStats['total_records'] = liveStats['todays_check_ins'] ?? localStats['total_records'];
        combinedStats['visitors_left'] = liveStats['todays_check_outs'] ?? localStats['visitors_left'];
      }

      final now = DateTime.now();
      state = state.copyWith(
        isSyncing: false,
        lastSyncTime: now,
        todayStats: combinedStats,
        lastMessage: 'Synchronization complete!',
      );

      final event = SyncEvent(
        type: type,
        reason: reason,
        timestamp: now,
        success: queueSuccess,
        extraData: combinedStats,
      );

      _syncEventController.add(event);
      AppLogger.info('[CentralSyncManager] Full synchronization completed successfully. Notified all subscribed UI listeners.');

      // Process any queued sync request immediately
      if (_hasPendingSyncRequest) {
        _hasPendingSyncRequest = false;
        Future.microtask(() => triggerSync(type: type, reason: 'Queued follow-up sync execution'));
      }

      return queueSuccess;
    } catch (e) {
      AppLogger.error('[CentralSyncManager] Error during full synchronization ($reason): $e');
      state = state.copyWith(
        isSyncing: false,
        lastMessage: 'Sync error: $e',
      );
      if (_hasPendingSyncRequest) {
        _hasPendingSyncRequest = false;
        Future.microtask(() => triggerSync(type: type, reason: 'Queued follow-up sync execution after error'));
      }
      return false;
    }
  }

  /// Reset statistics to 0 and notify all UI listeners after clearing data
  void resetStatsToZero() {
    final now = DateTime.now();
    final zeroStats = {
      'total_visitors': 0,
      'visitors_inside': 0,
      'visitors_left': 0,
      'total_records': 0,
      'average_duration_mins': 0,
      'average_duration_formatted': '0 min',
    };
    state = state.copyWith(
      isSyncing: false,
      lastSyncTime: now,
      todayStats: zeroStats,
      lastMessage: 'All visitor data cleared and reset to 0.',
    );
    _syncEventController.add(SyncEvent(
      type: SyncEventType.pullToRefresh,
      reason: 'All visitor data cleared',
      timestamp: now,
      success: true,
      extraData: zeroStats,
    ));
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _connectivitySub?.cancel();
    _wsSub?.cancel();
    _periodicTimer?.cancel();
    _syncEventController.close();
    super.dispose();
  }
}

final centralSyncManagerProvider = StateNotifierProvider<CentralSyncManager, CentralSyncState>((ref) {
  return CentralSyncManager.instance;
});
