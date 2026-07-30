import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/models/communication_models.dart';

class CommunicationSettingsScreen extends StatefulWidget {
  const CommunicationSettingsScreen({super.key});

  @override
  State<CommunicationSettingsScreen> createState() => _CommunicationSettingsScreenState();
}

class _CommunicationSettingsScreenState extends State<CommunicationSettingsScreen> {
  final _service = CommunicationService();
  bool _isLoading = true;
  bool _isSaving = false;

  String _mode = 'DISABLED';
  final _accessTokenCtrl = TextEditingController();
  final _phoneNumberIdCtrl = TextEditingController();
  final _businessAccountIdCtrl = TextEditingController();

  bool _autoSend = false;
  bool _allowEdit = false;
  bool _saveHistory = true;
  bool _retryFailed = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final settings = await _service.getSettings();
    setState(() {
      _mode = settings.mode;
      _accessTokenCtrl.text = settings.accessToken ?? '';
      _phoneNumberIdCtrl.text = settings.phoneNumberId ?? '';
      _businessAccountIdCtrl.text = settings.businessAccountId ?? '';
      _autoSend = settings.autoSend;
      _allowEdit = settings.allowEdit;
      _saveHistory = settings.saveHistory;
      _retryFailed = settings.retryFailed;
      _isLoading = false;
    });
  }

  Future<void> _saveSettings() async {
    setState(() => _isSaving = true);

    final updated = CommunicationSettings(
      id: 'comm_settings_default',
      mode: _mode,
      accessToken: _accessTokenCtrl.text.trim().isEmpty ? null : _accessTokenCtrl.text.trim(),
      phoneNumberId: _phoneNumberIdCtrl.text.trim().isEmpty ? null : _phoneNumberIdCtrl.text.trim(),
      businessAccountId: _businessAccountIdCtrl.text.trim().isEmpty ? null : _businessAccountIdCtrl.text.trim(),
      autoSend: _autoSend,
      allowEdit: _allowEdit,
      saveHistory: _saveHistory,
      retryFailed: _retryFailed,
      updatedAt: DateTime.now().toIso8601String(),
    );

    await _service.saveSettings(updated);

    if (!mounted) return;
    setState(() => _isSaving = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Communication Settings saved successfully'),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  void dispose() {
    _accessTokenCtrl.dispose();
    _phoneNumberIdCtrl.dispose();
    _businessAccountIdCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Communication Settings', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Communication Mode Card
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Communication Mode',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF2C1A11)),
                          ),
                          const SizedBox(height: 12),
                          RadioListTile<String>(
                            title: const Text('Manual WhatsApp'),
                            subtitle: const Text('Opens WhatsApp application with pre-filled message'),
                            value: 'MANUAL_WHATSAPP',
                            groupValue: _mode,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _mode = val!),
                          ),
                          RadioListTile<String>(
                            title: const Text('Meta Cloud API'),
                            subtitle: const Text('Direct API integration with Meta WhatsApp Business platform'),
                            value: 'META_CLOUD_API',
                            groupValue: _mode,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _mode = val!),
                          ),
                          RadioListTile<String>(
                            title: const Text('Disabled'),
                            subtitle: const Text('Disable all automatic messaging features'),
                            value: 'DISABLED',
                            groupValue: _mode,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _mode = val!),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Meta API Credentials Section
                  if (_mode == 'META_CLOUD_API') ...[
                    Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Meta API Credentials',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF2C1A11)),
                            ),
                            const SizedBox(height: 14),
                            TextField(
                              controller: _accessTokenCtrl,
                              obscureText: true,
                              decoration: const InputDecoration(
                                labelText: 'Access Token',
                                border: OutlineInputBorder(),
                                prefixIcon: Icon(Icons.key, color: Color(0xFFD4AF37)),
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _phoneNumberIdCtrl,
                              decoration: const InputDecoration(
                                labelText: 'Phone Number ID',
                                border: OutlineInputBorder(),
                                prefixIcon: Icon(Icons.phone, color: Color(0xFFD4AF37)),
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _businessAccountIdCtrl,
                              decoration: const InputDecoration(
                                labelText: 'Business Account ID',
                                border: OutlineInputBorder(),
                                prefixIcon: Icon(Icons.business, color: Color(0xFFD4AF37)),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Options Checkboxes
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Automation & Behavior Settings',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF2C1A11)),
                          ),
                          const SizedBox(height: 8),
                          CheckboxListTile(
                            title: const Text('Enable Automatic Sending'),
                            subtitle: const Text('Automatically trigger message send on visitor registration or check-out'),
                            value: _autoSend,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _autoSend = val ?? false),
                          ),
                          CheckboxListTile(
                            title: const Text('Allow Edit Before Sending'),
                            subtitle: const Text('Show editable message dialog before dispatching'),
                            value: _allowEdit,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _allowEdit = val ?? false),
                          ),
                          CheckboxListTile(
                            title: const Text('Save Communication History'),
                            subtitle: const Text('Store message log records in database'),
                            value: _saveHistory,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _saveHistory = val ?? true),
                          ),
                          CheckboxListTile(
                            title: const Text('Retry Failed Messages'),
                            subtitle: const Text('Automatically attempt retry for failed message transmissions'),
                            value: _retryFailed,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _retryFailed = val ?? false),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Save Button
                  SizedBox(
                    height: 50,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFD4AF37),
                        foregroundColor: Colors.black,
                      ),
                      onPressed: _isSaving ? null : _saveSettings,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                            )
                          : const Icon(Icons.save),
                      label: Text(
                        _isSaving ? 'SAVING...' : 'SAVE SETTINGS',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
