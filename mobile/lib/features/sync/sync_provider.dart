import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:temple_visitor_app/core/repositories/sync_repository.dart';
import 'package:temple_visitor_app/core/services/connectivity_service.dart';
import 'package:temple_visitor_app/core/services/websocket_service.dart';

final syncRepositoryProvider = Provider((ref) => SyncRepository());

final syncStateProvider = StateNotifierProvider<SyncNotifier, SyncState>((ref) {
  return SyncNotifier(ref.watch(syncRepositoryProvider));
});

class SyncState {
  final int pendingCount;
  final bool isSyncing;
  final String? lastMessage;

  SyncState({
    required this.pendingCount,
    required this.isSyncing,
    this.lastMessage,
  });

  SyncState copyWith({
    int? pendingCount,
    bool? isSyncing,
    String? lastMessage,
  }) {
    return SyncState(
      pendingCount: pendingCount ?? this.pendingCount,
      isSyncing: isSyncing ?? this.isSyncing,
      lastMessage: lastMessage ?? this.lastMessage,
    );
  }
}

class SyncNotifier extends StateNotifier<SyncState> {
  final SyncRepository _repo;
  final ConnectivityService _connectivity = ConnectivityService();
  StreamSubscription<bool>? _connectivitySub;
  Timer? _autoSyncTimer;

  SyncNotifier(this._repo) : super(SyncState(pendingCount: 0, isSyncing: false)) {
    refreshQueueCount();
    _initAutoSync();
  }

  void _initAutoSync() {
    // 1. Connect Real-Time WebSocket Service
    WebSocketService().connect();

    // 2. Listen to connectivity changes: when coming back online, auto-sync outbox queue
    _connectivitySub = _connectivity.onConnectivityChanged.listen((isOnline) {
      if (isOnline) {
        triggerManualSync();
      }
    });

    // 3. Periodic 5-second auto-sync timer when pending items exist
    _autoSyncTimer = Timer.periodic(const Duration(seconds: 5), (_) async {
      final count = await _repo.getPendingCount();
      state = state.copyWith(pendingCount: count);
      if (count > 0 && !state.isSyncing) {
        final online = await _connectivity.isOnline();
        if (online) {
          triggerManualSync();
        }
      }
    });
  }

  Future<void> refreshQueueCount() async {
    final count = await _repo.getPendingCount();
    state = state.copyWith(pendingCount: count);
  }

  Future<bool> triggerManualSync() async {
    if (state.isSyncing) return false;
    state = state.copyWith(isSyncing: true, lastMessage: null);
    final success = await _repo.processSyncQueue();
    await refreshQueueCount();
    state = state.copyWith(
      isSyncing: false,
      lastMessage: success ? 'Synchronization complete!' : 'Sync failed. Will retry automatically when online.',
    );
    return success;
  }

  @override
  void dispose() {
    _connectivitySub?.cancel();
    _autoSyncTimer?.cancel();
    super.dispose();
  }
}
