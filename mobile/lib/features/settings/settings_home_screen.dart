import 'package:flutter/material.dart';
import 'package:temple_visitor_app/features/settings/temple_info_screen.dart';
import 'package:temple_visitor_app/features/settings/communication_settings_screen.dart';
import 'package:temple_visitor_app/features/settings/communication_templates_screen.dart';
import 'package:temple_visitor_app/features/settings/today_activities_screen.dart';
import 'package:temple_visitor_app/features/settings/festival_info_screen.dart';
import 'package:temple_visitor_app/features/settings/communication_test_screen.dart';
import 'package:temple_visitor_app/features/reports/reports_dashboard_screen.dart';
import 'package:temple_visitor_app/features/reports/backup_restore_screen.dart';
import 'package:temple_visitor_app/core/services/admin_security_service.dart';

class SettingsHomeScreen extends StatefulWidget {
  const SettingsHomeScreen({super.key});

  @override
  State<SettingsHomeScreen> createState() => _SettingsHomeScreenState();
}

class _SettingsHomeScreenState extends State<SettingsHomeScreen> {
  void _changePinDialog() {
    final currentCtrl = TextEditingController();
    final newCtrl = TextEditingController();
    String error = '';

    showDialog(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          title: const Text('Change Admin Security PIN'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: currentCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Current PIN')),
              const SizedBox(height: 8),
              TextField(controller: newCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'New PIN')),
              if (error.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(error, style: const TextStyle(color: Colors.red, fontSize: 12)),
              ],
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                final success = await AdminSecurityService.changePin(currentCtrl.text.trim(), newCtrl.text.trim());
                if (success) {
                  if (context.mounted) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Admin Security PIN Changed Successfully'), backgroundColor: Colors.green),
                    );
                  }
                } else {
                  setModalState(() => error = 'Incorrect current PIN');
                }
              },
              child: const Text('Update PIN'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Temple Control & Settings', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          _menuTile(
            title: 'Reports & Analytics Dashboard',
            subtitle: 'View visitor metrics, filter records, export Excel & PDF',
            icon: Icons.bar_chart,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportsDashboardScreen())),
          ),
          _menuTile(
            title: 'Backup & Database Management',
            subtitle: 'Export and restore SQLite database snapshots',
            icon: Icons.backup,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BackupRestoreScreen())),
          ),
          _menuTile(
            title: 'Temple Organization Info',
            subtitle: 'Name, address, contact numbers, donation links',
            icon: Icons.account_balance,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TempleInfoScreen())),
          ),
          _menuTile(
            title: 'Communication Settings',
            subtitle: 'Configure WhatsApp mode, Meta API credentials & behavior options',
            icon: Icons.forum,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CommunicationSettingsScreen())),
          ),
          _menuTile(
            title: 'Communication Templates',
            subtitle: 'Entry and Exit WhatsApp message templates',
            icon: Icons.mark_chat_read,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CommunicationTemplatesScreen())),
          ),
          _menuTile(
            title: 'Today\'s Activities Manager',
            subtitle: 'Manage daily seva, prasad, and special events',
            icon: Icons.event,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TodayActivitiesScreen())),
          ),
          _menuTile(
            title: 'Festival Information',
            subtitle: 'Manage upcoming festival announcements',
            icon: Icons.festival,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FestivalInfoScreen())),
          ),
          _menuTile(
            title: 'Communication Gateway Test',
            subtitle: 'Send test messages without affecting visitor records',
            icon: Icons.send,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CommunicationTestScreen())),
          ),
          _menuTile(
            title: 'Security PIN Settings',
            subtitle: 'Change Administrator access PIN (Default: 1234)',
            icon: Icons.security,
            onTap: _changePinDialog,
          ),
        ],
      ),
    );
  }

  Widget _menuTile({required String title, required String subtitle, required IconData icon, required VoidCallback onTap}) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        leading: CircleAvatar(
          backgroundColor: const Color(0xFFD4AF37),
          child: Icon(icon, color: Colors.black),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
