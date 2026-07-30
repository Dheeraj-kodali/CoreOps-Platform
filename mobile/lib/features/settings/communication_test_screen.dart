import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/models/communication_models.dart';

class CommunicationTestScreen extends StatefulWidget {
  const CommunicationTestScreen({super.key});

  @override
  State<CommunicationTestScreen> createState() => _CommunicationTestScreenState();
}

class _CommunicationTestScreenState extends State<CommunicationTestScreen> {
  final _phoneCtrl = TextEditingController(text: '+91 98765 43210');
  String _selectedTemplate = 'ENTRY';
  String _renderedPreview = '';
  bool _isSending = false;
  String? _lastStatus;
  String? _lastMetaMsgId;
  String? _lastErrorMsg;

  @override
  void initState() {
    super.initState();
    _generatePreview();
  }

  Future<void> _generatePreview() async {
    final tmplData = await SQLiteDatabase.getTemplate(_selectedTemplate);
    final rawText = tmplData?['message']?.toString() ?? '🙏 Welcome {name}\n\nYou have successfully entered\n{temple}\n\nEntry Time:\n{time}\n\nHave a blessed day.';

    final testVisitor = VisitorModel(
      id: 'v_test',
      visitorUuid: 'TEST-001',
      name: 'Administrator Test Visitor',
      phoneNumber: _phoneCtrl.text.trim(),
      village: 'Sample Village',
      purpose: 'Testing Gateway',
      personsCount: 1,
      visitorDate: '2026-07-28',
      timeIn: '10:00 AM',
      timeOut: '11:15 AM',
      visitDuration: '1 hr 15 min',
      status: 'CHECKED_IN',
      syncStatus: 'SYNCED',
    );

    final rawTemple = await SQLiteDatabase.getTempleInfo();
    final templeInfo = TempleInfo(
      templeName: rawTemple['temple_name'] ?? 'Sri Kalki Seva Alayam',
      website: rawTemple['website'] ?? 'https://kalkiseva.org',
      googleMapsLink: rawTemple['google_maps_link'] ?? '',
      donationLink: rawTemple['donation_link'] ?? '',
      facebook: rawTemple['facebook'] ?? '',
      instagram: rawTemple['instagram'] ?? '',
      youtube: rawTemple['youtube'] ?? '',
      templePhone: rawTemple['temple_phone'] ?? '',
      templeAddress: rawTemple['temple_address'] ?? '',
    );

    final preview = TemplateEngine.render(
      templateText: rawText,
      visitor: testVisitor,
      templeInfo: templeInfo,
      volunteerName: 'Admin',
    );

    setState(() => _renderedPreview = preview);
  }

  Future<void> _sendTestMessage() async {
    setState(() {
      _isSending = true;
      _lastStatus = 'Sending...';
      _lastMetaMsgId = null;
      _lastErrorMsg = null;
    });

    await _generatePreview();

    final service = CommunicationService();
    final settings = await service.getSettings();

    ChannelProvider provider;
    if (settings.mode == 'META_CLOUD_API') {
      provider = MetaWhatsAppProvider(settings);
    } else {
      provider = ManualWhatsAppProvider();
    }

    final result = await provider.sendMessage(_phoneCtrl.text.trim(), _renderedPreview);

    final statusStr = result.success ? 'Sent' : 'Failed';

    await SQLiteDatabase.insertCommunicationHistory({
      'id': const Uuid().v4(),
      'visitor_id': 'v_test_admin',
      'phone': _phoneCtrl.text.trim(),
      'channel': provider.channelName,
      'template_type': 'TEST',
      'rendered_message': _renderedPreview,
      'status': statusStr.toUpperCase(),
      'meta_message_id': result.metaMessageId,
      'error_message': result.errorMessage,
      'failure_reason': result.errorMessage,
      'created_at': DateTime.now().toIso8601String(),
    });

    if (!mounted) return;

    setState(() {
      _isSending = false;
      _lastStatus = statusStr;
      _lastMetaMsgId = result.metaMessageId;
      _lastErrorMsg = result.errorMessage;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result.success ? 'Test Message Dispatched Successfully (ID: ${result.metaMessageId})' : 'Test Dispatch Failed: ${result.errorMessage}'),
        backgroundColor: result.success ? Colors.green : Colors.red,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Communication Gateway Test', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _phoneCtrl,
              keyboardType: TextInputType.phone,
              onChanged: (_) => _generatePreview(),
              decoration: const InputDecoration(
                labelText: 'Test Recipient Phone Number',
                prefixIcon: Icon(Icons.phone, color: Color(0xFFD4AF37)),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 14),

            DropdownButtonFormField<String>(
              initialValue: _selectedTemplate,
              decoration: const InputDecoration(
                labelText: 'Template to Test',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'ENTRY', child: Text('Visitor Entry Message Template')),
                DropdownMenuItem(value: 'EXIT', child: Text('Visitor Exit Message Template')),
              ],
              onChanged: (v) {
                if (v != null) {
                  setState(() => _selectedTemplate = v);
                  _generatePreview();
                }
              },
            ),
            const SizedBox(height: 16),

            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.amber.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Rendered Test Payload:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.brown)),
                  const SizedBox(height: 6),
                  Text(_renderedPreview, style: const TextStyle(fontSize: 13)),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Live Test Results Status Card
            if (_lastStatus != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _lastStatus == 'Sending...'
                      ? Colors.blue.shade50
                      : (_lastStatus == 'Sent' ? Colors.green.shade50 : Colors.red.shade50),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _lastStatus == 'Sending...'
                        ? Colors.blue.shade300
                        : (_lastStatus == 'Sent' ? Colors.green.shade300 : Colors.red.shade300),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          _lastStatus == 'Sending...'
                              ? Icons.hourglass_top
                              : (_lastStatus == 'Sent' ? Icons.check_circle : Icons.error),
                          color: _lastStatus == 'Sending...'
                              ? Colors.blue
                              : (_lastStatus == 'Sent' ? Colors.green : Colors.red),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Status: $_lastStatus',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: _lastStatus == 'Sending...'
                                ? Colors.blue.shade900
                                : (_lastStatus == 'Sent' ? Colors.green.shade900 : Colors.red.shade900),
                          ),
                        ),
                      ],
                    ),
                    if (_lastMetaMsgId != null) ...[
                      const SizedBox(height: 6),
                      Text('Meta Message ID: $_lastMetaMsgId', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    ],
                    if (_lastErrorMsg != null) ...[
                      const SizedBox(height: 6),
                      Text('Meta Error: $_lastErrorMsg', style: const TextStyle(fontSize: 12, color: Colors.red)),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            SizedBox(
              height: 50,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFD4AF37),
                  foregroundColor: Colors.black,
                ),
                onPressed: _isSending ? null : _sendTestMessage,
                icon: _isSending
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                    : const Icon(Icons.send),
                label: Text(_isSending ? 'Sending...' : 'Send Test Message', style: const TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
