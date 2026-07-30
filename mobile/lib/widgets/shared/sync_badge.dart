import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class SyncBadge extends StatelessWidget {
  final String status;

  const SyncBadge({Key? key, required this.status}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isSynced = status == 'SYNCED';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: isSynced ? Colors.green[100] : Colors.amber[100],
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isSynced ? Colors.green : const Color(0xFFD4AF37),
        ),
      ),
      child: Text(
        isSynced ? 'SYNCED' : 'PENDING',
        style: GoogleFonts.inter(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: isSynced ? Colors.green[900] : const Color(0xFF3E2723),
        ),
      ),
    );
  }
}
