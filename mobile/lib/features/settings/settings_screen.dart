import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:share_plus/share_plus.dart';
import 'package:file_picker/file_picker.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/core/services/storage_service.dart';
import 'package:temple_visitor_app/features/authentication/auth_provider.dart';
import 'package:temple_visitor_app/main.dart';
import 'package:temple_visitor_app/widgets/shared/temple_app_bar.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final loc = AppLocalizations.of(context);
    final currentLocale = ref.watch(localeProvider);

    return Scaffold(
      appBar: TempleAppBar(title: loc.settings),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Language Selector Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: const Color(0xFFD4AF37).withOpacity(0.3)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.language, color: Color(0xFFD4AF37)),
                      const SizedBox(width: 10),
                      Text(
                        loc.selectLanguage,
                        style: GoogleFonts.cinzel(fontSize: 16, fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () async {
                            ref.read(localeProvider.notifier).state = const Locale('en');
                            await StorageService.saveLanguage('en');
                          },
                          style: OutlinedButton.styleFrom(
                            side: BorderSide(
                              color: currentLocale.languageCode == 'en' ? const Color(0xFFD4AF37) : Colors.grey,
                              width: currentLocale.languageCode == 'en' ? 2 : 1,
                            ),
                            backgroundColor: currentLocale.languageCode == 'en' ? const Color(0xFFFAF8F5) : Colors.white,
                          ),
                          child: Text(loc.english, style: GoogleFonts.inter(fontWeight: FontWeight.bold)),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () async {
                            ref.read(localeProvider.notifier).state = const Locale('te');
                            await StorageService.saveLanguage('te');
                          },
                          style: OutlinedButton.styleFrom(
                            side: BorderSide(
                              color: currentLocale.languageCode == 'te' ? const Color(0xFFD4AF37) : Colors.grey,
                              width: currentLocale.languageCode == 'te' ? 2 : 1,
                            ),
                            backgroundColor: currentLocale.languageCode == 'te' ? const Color(0xFFFAF8F5) : Colors.white,
                          ),
                          child: Text(loc.telugu, style: GoogleFonts.inter(fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Database Backup & Restore Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: const Color(0xFFD4AF37).withOpacity(0.3)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.backup, color: Color(0xFFD4AF37)),
                      const SizedBox(width: 10),
                      Text(
                        'Database Backup & Restore',
                        style: GoogleFonts.cinzel(fontSize: 16, fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            try {
                              final dbPath = await SQLiteDatabase.getDatabaseFilePath();
                              final file = File(dbPath);
                              if (await file.exists()) {
                                final xFile = XFile(dbPath);
                                await Share.shareXFiles([xFile], text: 'Temple Visitors Database Backup (.db)');
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Database Backup Exported Successfully'), backgroundColor: Colors.green),
                                  );
                                }
                              }
                            } catch (e) {
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Export Failed: $e'), backgroundColor: Colors.red),
                                );
                              }
                            }
                          },
                          icon: const Icon(Icons.upload_file, size: 18),
                          label: const Text('Backup Database (.db)'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            try {
                              final result = await FilePicker.platform.pickFiles();
                              if (result != null && result.files.single.path != null) {
                                final path = result.files.single.path!;
                                await SQLiteDatabase.importDatabase(path);
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Database Restored Successfully!'), backgroundColor: Colors.green),
                                  );
                                }
                              }
                            } catch (e) {
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Restore Failed: $e'), backgroundColor: Colors.red),
                                );
                              }
                            }
                          },
                          icon: const Icon(Icons.file_download, size: 18),
                          label: const Text('Restore Database (.db)'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Application Info Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: const Color(0xFFD4AF37).withOpacity(0.3)),
            ),
            child: ListTile(
              leading: const Icon(Icons.info_outline, color: Color(0xFFD4AF37)),
              title: Text('Sri Kalki Seva Alayam', style: GoogleFonts.inter(fontWeight: FontWeight.bold)),
              subtitle: const Text('Version 1.0.0 (Enterprise Build)'),
            ),
          ),
          const SizedBox(height: 24),

          // Logout Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () async {
                await ref.read(authStateProvider.notifier).logout();
              },
              icon: const Icon(Icons.logout),
              label: Text(loc.logout),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF900C3F),
                foregroundColor: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
