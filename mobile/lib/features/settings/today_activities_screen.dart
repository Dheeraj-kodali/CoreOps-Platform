import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';

class TodayActivitiesScreen extends StatefulWidget {
  const TodayActivitiesScreen({super.key});

  @override
  State<TodayActivitiesScreen> createState() => _TodayActivitiesScreenState();
}

class _TodayActivitiesScreenState extends State<TodayActivitiesScreen> {
  List<Map<String, dynamic>> _activities = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadActivities();
  }

  Future<void> _loadActivities() async {
    final db = await SQLiteDatabase.instance;
    final list = await db.query('today_activities');
    setState(() {
      _activities = list;
      _isLoading = false;
    });
  }

  Future<void> _toggleActivity(String id, bool currentStatus) async {
    final db = await SQLiteDatabase.instance;
    await db.update('today_activities', {'is_active': currentStatus ? 0 : 1}, where: 'id = ?', whereArgs: [id]);
    _loadActivities();
  }

  Future<void> _deleteActivity(String id) async {
    final db = await SQLiteDatabase.instance;
    await db.delete('today_activities', where: 'id = ?', whereArgs: [id]);
    _loadActivities();
  }

  void _showAddEditDialog([Map<String, dynamic>? item]) {
    final titleCtrl = TextEditingController(text: item?['title'] ?? '');
    final descCtrl = TextEditingController(text: item?['description'] ?? '');

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(item == null ? 'Add Today\'s Activity' : 'Edit Activity'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: titleCtrl, decoration: const InputDecoration(labelText: 'Activity Title *')),
            const SizedBox(height: 8),
            TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'Description')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              if (titleCtrl.text.trim().isEmpty) return;
              final db = await SQLiteDatabase.instance;
              if (item == null) {
                await db.insert('today_activities', {
                  'id': const Uuid().v4(),
                  'title': titleCtrl.text.trim(),
                  'description': descCtrl.text.trim(),
                  'is_active': 1,
                });
              } else {
                await db.update('today_activities', {
                  'title': titleCtrl.text.trim(),
                  'description': descCtrl.text.trim(),
                }, where: 'id = ?', whereArgs: [item['id']]);
              }
              if (mounted) {
                Navigator.pop(context);
                _loadActivities();
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Today\'s Activities Manager', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color(0xFFD4AF37),
        onPressed: () => _showAddEditDialog(),
        child: const Icon(Icons.add, color: Colors.black),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _activities.length,
              itemBuilder: (context, index) {
                final item = _activities[index];
                final isActive = item['is_active'] == 1 || item['is_active'] == true;

                return Card(
                  margin: const EdgeInsets.symmetric(vertical: 6),
                  child: ListTile(
                    title: Text(item['title'].toString(), style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text(item['description'].toString()),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Switch(
                          value: isActive,
                          onChanged: (_) => _toggleActivity(item['id'].toString(), isActive),
                        ),
                        IconButton(icon: const Icon(Icons.edit, color: Colors.blue), onPressed: () => _showAddEditDialog(item)),
                        IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () => _deleteActivity(item['id'].toString())),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
