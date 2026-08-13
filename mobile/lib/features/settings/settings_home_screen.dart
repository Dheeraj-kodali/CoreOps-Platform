import 'package:flutter/material.dart';
import 'package:temple_visitor_app/features/settings/temple_info_screen.dart';
import 'package:temple_visitor_app/features/settings/communication_settings_screen.dart';
import 'package:temple_visitor_app/features/settings/communication_templates_screen.dart';
import 'package:temple_visitor_app/features/settings/today_activities_screen.dart';
import 'package:temple_visitor_app/features/settings/festival_info_screen.dart';
import 'package:temple_visitor_app/features/settings/communication_test_screen.dart';
import 'package:temple_visitor_app/features/reports/reports_dashboard_screen.dart';
import 'package:temple_visitor_app/features/reports/backup_restore_screen.dart';
import 'package:temple_visitor_app/features/broadcast/broadcast_screen.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/admin_security_service.dart';

class SettingsHomeScreen extends StatefulWidget {
  const SettingsHomeScreen({super.key});

  @override
  State<SettingsHomeScreen> createState() => _SettingsHomeScreenState();
}

class _SettingsHomeScreenState extends State<SettingsHomeScreen> {
  Future<bool> _promptAdminPin() async {
    final pinCtrl = TextEditingController();
    String err = '';
    bool authorized = false;

    await showDialog(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: const [
              Icon(Icons.security, color: Color(0xFFD4AF37)),
              SizedBox(width: 8),
              Text('Admin PIN Required', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Please enter Administrator Access PIN (Default: 1234):', style: TextStyle(fontSize: 13)),
              const SizedBox(height: 12),
              TextField(
                controller: pinCtrl,
                obscureText: true,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Admin PIN', border: OutlineInputBorder()),
              ),
              if (err.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(err, style: const TextStyle(color: Colors.red, fontSize: 12, fontWeight: FontWeight.bold)),
              ],
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFD4AF37), foregroundColor: Colors.black),
              onPressed: () async {
                final res = await AdminSecurityService.verifyPin(pinCtrl.text.trim());
                if (res['valid'] == true) {
                  authorized = true;
                  if (context.mounted) Navigator.pop(context);
                } else {
                  setModalState(() => err = res['message']?.toString() ?? 'Incorrect Admin PIN. Try 1234');
                }
              },
              child: const Text('VERIFY & ENTER'),
            ),
          ],
        ),
      ),
    );
    return authorized;
  }

  void _changePinDialog() async {
    final ok = await _promptAdminPin();
    if (!ok) return;

    final currentCtrl = TextEditingController();
    final newCtrl = TextEditingController();
    String error = '';

    if (!mounted) return;
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

  void _clearVisitorDataDialog() async {
    final ok = await _promptAdminPin();
    if (!ok) return;

    if (!mounted) return;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Row(
          children: const [
            Icon(Icons.delete_forever, color: Colors.red),
            SizedBox(width: 8),
            Text('Reset & Clear All Visitor Data', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        content: const Text(
          'This will permanently delete all visitor entries, visits, persons, outbox queue items, and history logs from SQLite database.\n\nVisitor counts will reset to 0. Are you sure you want to proceed?',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            onPressed: () async {
              Navigator.pop(context);
              await VisitorRepository().clearAllVisitorData();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('All Visitor Data Cleared & Counter Reset to 0 Successfully!'),
                    backgroundColor: Colors.green,
                  ),
                );
              }
            },
            child: const Text('CLEAR ALL DATA (0 COUNT)'),
          ),
        ],
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
            title: 'Enterprise Devotee Broadcast',
            subtitle: 'Send custom WhatsApp messages to all historical visitors in ledger via n8n',
            icon: Icons.campaign,
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BroadcastScreen())),
          ),
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
            title: 'Clear All Historical Visitor Data',
            subtitle: 'Permanently wipe all accumulated visitor entries & reset counter to 0',
            icon: Icons.delete_forever,
            onTap: _clearVisitorDataDialog,
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
