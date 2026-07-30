import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/features/sync/sync_provider.dart';
import 'package:temple_visitor_app/widgets/shared/temple_app_bar.dart';

class SyncScreen extends ConsumerWidget {
  const SyncScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final loc = AppLocalizations.of(context);
    final syncState = ref.watch(syncStateProvider);

    return Scaffold(
      appBar: TempleAppBar(title: loc.offlineSync),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFFD4AF37).withOpacity(0.15),
              ),
              child: const Icon(
                Icons.cloud_sync,
                size: 64,
                color: Color(0xFFD4AF37),
              ),
            ),
            const SizedBox(height: 24),

            Text(
              'Pending Sync Queue',
              style: GoogleFonts.cinzel(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF2C1A11),
              ),
            ),
            const SizedBox(height: 8),

            Text(
              '${syncState.pendingCount} visitor records waiting to be synced to the central server',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(fontSize: 14, color: Colors.grey[700]),
            ),
            const SizedBox(height: 32),

            if (syncState.lastMessage != null) ...[
              Text(
                syncState.lastMessage!,
                style: GoogleFonts.inter(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF3E2723),
                ),
              ),
              const SizedBox(height: 16),
            ],

            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: syncState.pendingCount == 0 || syncState.isSyncing
                    ? null
                    : () async {
                        await ref.read(syncStateProvider.notifier).triggerManualSync();
                      },
                icon: syncState.isSyncing
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF2C1A11)),
                      )
                    : const Icon(Icons.cloud_upload),
                label: Text(syncState.isSyncing ? 'Syncing...' : loc.manualSync),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
