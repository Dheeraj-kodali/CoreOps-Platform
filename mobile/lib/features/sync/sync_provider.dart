import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:temple_visitor_app/core/repositories/sync_repository.dart';

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

  SyncNotifier(this._repo) : super(SyncState(pendingCount: 0, isSyncing: false)) {
    refreshQueueCount();
  }

  Future<void> refreshQueueCount() async {
    final count = await _repo.getPendingCount();
    state = state.copyWith(pendingCount: count);
  }

  Future<bool> triggerManualSync() async {
    state = state.copyWith(isSyncing: true, lastMessage: null);
    final success = await _repo.processSyncQueue();
    await refreshQueueCount();
    state = state.copyWith(
      isSyncing: false,
      lastMessage: success ? 'Synchronization complete!' : 'Sync failed. Will retry automatically when online.',
    );
    return success;
  }
}
