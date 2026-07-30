import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';

class FestivalInfoScreen extends StatefulWidget {
  const FestivalInfoScreen({super.key});

  @override
  State<FestivalInfoScreen> createState() => _FestivalInfoScreenState();
}

class _FestivalInfoScreenState extends State<FestivalInfoScreen> {
  final _nameCtrl = TextEditingController();
  final _dateCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  bool _enabled = true;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadFestival();
  }

  Future<void> _loadFestival() async {
    final db = await SQLiteDatabase.instance;
    final list = await db.query('festival_info');
    if (list.isNotEmpty) {
      final f = list.first;
      setState(() {
        _nameCtrl.text = f['festival_name']?.toString() ?? '';
        _dateCtrl.text = f['festival_date']?.toString() ?? '';
        _descCtrl.text = f['festival_description']?.toString() ?? '';
        _enabled = f['enabled'] == 1 || f['enabled'] == true;
        _isLoading = false;
      });
    } else {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _save() async {
    final db = await SQLiteDatabase.instance;
    await db.insert('festival_info', {
      'id': 'fest_main',
      'festival_name': _nameCtrl.text.trim(),
      'festival_date': _dateCtrl.text.trim(),
      'festival_description': _descCtrl.text.trim(),
      'enabled': _enabled ? 1 : 0,
    });

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Festival Information Saved Successfully'), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Festival Information', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Enable Festival Notifications', style: TextStyle(fontWeight: FontWeight.bold)),
                    value: _enabled,
                    activeColor: const Color(0xFFD4AF37),
                    onChanged: (v) => setState(() => _enabled = v),
                  ),
                  const SizedBox(height: 10),
                  TextField(controller: _nameCtrl, decoration: const InputDecoration(labelText: 'Festival Name', border: OutlineInputBorder())),
                  const SizedBox(height: 12),
                  TextField(controller: _dateCtrl, decoration: const InputDecoration(labelText: 'Festival Date (yyyy-MM-dd)', border: OutlineInputBorder())),
                  const SizedBox(height: 12),
                  TextField(controller: _descCtrl, maxLines: 3, decoration: const InputDecoration(labelText: 'Festival Description', border: OutlineInputBorder())),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFD4AF37),
                        foregroundColor: Colors.black,
                      ),
                      onPressed: _save,
                      icon: const Icon(Icons.save),
                      label: const Text('SAVE FESTIVAL INFO', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
