import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/models/communication_models.dart';

class CommunicationTemplatesScreen extends StatefulWidget {
  const CommunicationTemplatesScreen({super.key});

  @override
  State<CommunicationTemplatesScreen> createState() => _CommunicationTemplatesScreenState();
}

class _CommunicationTemplatesScreenState extends State<CommunicationTemplatesScreen> {
  String _activeType = 'ENTRY'; // 'ENTRY' or 'EXIT'

  final _entryCtrl = TextEditingController();
  bool _entryEnabled = true;

  final _exitCtrl = TextEditingController();
  bool _exitEnabled = true;

  bool _isLoading = true;

  final List<String> _placeholders = [
    '{name}',
    '{phone}',
    '{village}',
    '{persons}',
    '{purpose}',
    '{date}',
    '{time}',
    '{duration}',
    '{visitor_id}',
    '{temple}',
    '{volunteer}',
  ];

  @override
  void initState() {
    super.initState();
    _loadTemplates();
  }

  Future<void> _loadTemplates() async {
    final entry = await SQLiteDatabase.getTemplate('ENTRY');
    final exit = await SQLiteDatabase.getTemplate('EXIT');

    setState(() {
      _entryCtrl.text = entry?['message'] ?? '🙏 Welcome {name}\n\nYou have successfully entered\n{temple}\n\nEntry Time:\n{time}\n\nHave a blessed day.';
      _entryEnabled = entry?['is_enabled'] == 1 || entry?['is_enabled'] == true;

      _exitCtrl.text = exit?['message'] ?? '🙏 Thank you {name}\n\nExit Time:\n{time}\n\nVisit Duration:\n{duration}\n\nThank you for visiting\n{temple}';
      _exitEnabled = exit?['is_enabled'] == 1 || exit?['is_enabled'] == true;

      _isLoading = false;
    });
  }

  void _insertPlaceholder(String placeholder) {
    final ctrl = _activeType == 'ENTRY' ? _entryCtrl : _exitCtrl;
    final text = ctrl.text;
    final selection = ctrl.selection;

    final newText = text.replaceRange(
      selection.start >= 0 ? selection.start : text.length,
      selection.end >= 0 ? selection.end : text.length,
      placeholder,
    );

    setState(() {
      ctrl.text = newText;
      ctrl.selection = TextSelection.collapsed(
        offset: (selection.start >= 0 ? selection.start : text.length) + placeholder.length,
      );
    });
  }

  Future<void> _save() async {
    final now = DateTime.now().toIso8601String();

    await SQLiteDatabase.saveMessageTemplate({
      'id': 'tmpl_entry',
      'template_type': 'ENTRY',
      'title': 'Visitor Entry Message',
      'message': _entryCtrl.text.trim(),
      'is_enabled': _entryEnabled ? 1 : 0,
      'created_at': now,
      'updated_at': now,
    });

    await SQLiteDatabase.saveMessageTemplate({
      'id': 'tmpl_exit',
      'template_type': 'EXIT',
      'title': 'Visitor Exit Message',
      'message': _exitCtrl.text.trim(),
      'is_enabled': _exitEnabled ? 1 : 0,
      'created_at': now,
      'updated_at': now,
    });

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Templates Saved Successfully'), backgroundColor: Colors.green),
    );
  }

  void _restoreDefaults() {
    setState(() {
      if (_activeType == 'ENTRY') {
        _entryCtrl.text = '🙏 Welcome {name}\n\nYou have successfully entered\n{temple}\n\nEntry Time:\n{time}\n\nHave a blessed day.';
        _entryEnabled = true;
      } else {
        _exitCtrl.text = '🙏 Thank you {name}\n\nExit Time:\n{time}\n\nVisit Duration:\n{duration}\n\nThank you for visiting\n{temple}';
        _exitEnabled = true;
      }
    });
  }

  String _renderPreviewText() {
    final rawText = _activeType == 'ENTRY' ? _entryCtrl.text : _exitCtrl.text;

    final sampleVisitor = VisitorModel(
      id: 'v_sample',
      visitorUuid: 'VST-98210',
      name: 'Ramesh Kumar',
      phoneNumber: '+91 98765 43210',
      village: 'Chittoor',
      purpose: 'General Darshan',
      personsCount: 3,
      visitorDate: '2026-07-28',
      timeIn: '10:15 AM',
      timeOut: '11:40 AM',
      visitDuration: '1 hr 25 min',
      status: 'CHECKED_IN',
      syncStatus: 'SYNCED',
    );

    final sampleTemple = TempleInfo.defaultInfo();

    return TemplateEngine.render(
      templateText: rawText,
      visitor: sampleVisitor,
      templeInfo: sampleTemple,
      volunteerName: 'Venkat',
    );
  }

  @override
  Widget build(BuildContext context) {
    final activeCtrl = _activeType == 'ENTRY' ? _entryCtrl : _exitCtrl;
    final isEnabled = _activeType == 'ENTRY' ? _entryEnabled : _exitEnabled;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Communication Templates', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Tab Selector
                  Row(
                    children: [
                      Expanded(
                        child: ChoiceChip(
                          label: const Center(child: Text('Visitor Entry Template')),
                          selected: _activeType == 'ENTRY',
                          selectedColor: const Color(0xFFD4AF37),
                          onSelected: (_) => setState(() => _activeType = 'ENTRY'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ChoiceChip(
                          label: const Center(child: Text('Visitor Exit Template')),
                          selected: _activeType == 'EXIT',
                          selectedColor: const Color(0xFFD4AF37),
                          onSelected: (_) => setState(() => _activeType = 'EXIT'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // Enable Switch & Character Counter
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Switch(
                            value: isEnabled,
                            activeThumbColor: const Color(0xFFD4AF37),
                            onChanged: (val) {
                              setState(() {
                                if (_activeType == 'ENTRY') {
                                  _entryEnabled = val;
                                } else {
                                  _exitEnabled = val;
                                }
                              });
                            },
                          ),
                          Text(isEnabled ? 'Template Enabled' : 'Template Disabled', style: const TextStyle(fontWeight: FontWeight.bold)),
                        ],
                      ),
                      Text('${activeCtrl.text.length} chars', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                    ],
                  ),
                  const SizedBox(height: 10),

                  // Multi-line Editor
                  TextField(
                    controller: activeCtrl,
                    maxLines: 7,
                    onChanged: (_) => setState(() {}),
                    decoration: const InputDecoration(
                      labelText: 'Template Text',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),

                  // Placeholder Chips Bar
                  const Text('Tap Placeholder to Insert:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFFD4AF37))),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: _placeholders.map((p) {
                      return ActionChip(
                        label: Text(p, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                        backgroundColor: Colors.amber.shade50,
                        onPressed: () => _insertPlaceholder(p),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 18),

                  // Live Preview Panel
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.green.shade300),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.remove_red_eye, size: 18, color: Colors.green),
                            SizedBox(width: 6),
                            Text('Live WhatsApp Preview:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green, fontSize: 13)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _renderPreviewText(),
                          style: const TextStyle(fontSize: 13, color: Colors.black87),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Buttons Bar
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _restoreDefaults,
                          child: const Text('Restore Default Template'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFD4AF37),
                            foregroundColor: Colors.black,
                          ),
                          onPressed: _save,
                          child: const Text('SAVE TEMPLATES', style: TextStyle(fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }
}
