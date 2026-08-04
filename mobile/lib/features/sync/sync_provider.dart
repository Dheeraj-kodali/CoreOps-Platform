import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:temple_visitor_app/core/repositories/sync_repository.dart';
import 'package:temple_visitor_app/core/services/central_sync_manager.dart';

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
  StreamSubscription<CentralSyncState>? _centralSub;

  SyncNotifier(this._repo) : super(SyncState(pendingCount: 0, isSyncing: false)) {
    refreshQueueCount();
    _subscribeCentral();
  }

  void _subscribeCentral() {
    _centralSub = CentralSyncManager.instance.stream.listen((centralState) {
      state = state.copyWith(
        pendingCount: centralState.pendingCount,
        isSyncing: centralState.isSyncing,
        lastMessage: centralState.lastMessage,
      );
    });
  }

  Future<void> refreshQueueCount() async {
    final count = await _repo.getPendingCount();
    state = state.copyWith(pendingCount: count);
  }

  Future<bool> triggerManualSync() async {
    return await CentralSyncManager.instance.triggerSync(
      type: SyncEventType.pullToRefresh,
      reason: 'User Manual Sync Trigger',
    );
  }

  @override
  void dispose() {
    _centralSub?.cancel();
    super.dispose();
  }
}
