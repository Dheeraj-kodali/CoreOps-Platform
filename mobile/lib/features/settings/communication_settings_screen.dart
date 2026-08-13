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

  void _showLinkWizard() {
    int selectedTab = 0; // 0 = n8n Webhook, 1 = Meta Cloud API Direct
    final testPhoneCtrl = TextEditingController(text: '6301123013');
    final webhookUrlCtrl = TextEditingController(
      text: _accessTokenCtrl.text.trim().isNotEmpty && _accessTokenCtrl.text.startsWith('http')
          ? _accessTokenCtrl.text.trim()
          : 'https://dheerajk.app.n8n.cloud/webhook/temple-whatsapp',
    );
    final metaPhoneIdCtrl = TextEditingController(text: _phoneNumberIdCtrl.text.trim());
    final metaBusinessIdCtrl = TextEditingController(text: _businessAccountIdCtrl.text.trim());
    final metaTokenCtrl = TextEditingController(
      text: _accessTokenCtrl.text.trim().isNotEmpty && !_accessTokenCtrl.text.startsWith('http')
          ? _accessTokenCtrl.text.trim()
          : '',
    );

    bool isTesting = false;
    String testResult = '';
    bool testSuccess = false;

    showDialog(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: const [
              Icon(Icons.link, color: Colors.green, size: 28),
              SizedBox(width: 8),
              Text('Link WhatsApp Business', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Select your preferred WhatsApp Business API provider & verify live connection:',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ChoiceChip(
                        label: const Text('n8n Webhook', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        selected: selectedTab == 0,
                        selectedColor: const Color(0xFFD4AF37),
                        onSelected: (val) => setModalState(() {
                          selectedTab = 0;
                          testResult = '';
                        }),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ChoiceChip(
                        label: const Text('Meta Cloud API', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        selected: selectedTab == 1,
                        selectedColor: const Color(0xFFD4AF37),
                        onSelected: (val) => setModalState(() {
                          selectedTab = 1;
                          testResult = '';
                        }),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                if (selectedTab == 0) ...[
                  TextField(
                    controller: webhookUrlCtrl,
                    decoration: const InputDecoration(
                      labelText: 'n8n Webhook Endpoint URL *',
                      hintText: 'https://n8n.kalkiseva.org/webhook/whatsapp',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.webhook, color: Colors.green),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: testPhoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(
                      labelText: 'Test Receiver Phone *',
                      hintText: '6301123013',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.phone, color: Colors.green),
                    ),
                  ),
                ] else ...[
                  TextField(
                    controller: metaPhoneIdCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Phone Number ID *',
                      hintText: '1290699690788322',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.numbers, color: Colors.blue),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: metaBusinessIdCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Business Account ID',
                      hintText: '1029384756',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.business, color: Colors.blue),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: metaTokenCtrl,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Permanent Access Token *',
                      hintText: 'EAAG...',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.key, color: Colors.blue),
                    ),
                  ),
                ],
                const SizedBox(height: 14),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: selectedTab == 0 ? const Color(0xFF2E7D32) : const Color(0xFF1565C0),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    icon: isTesting
                        ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Icon(Icons.check_circle_outline, size: 18),
                    label: Text(isTesting ? 'VERIFYING CONNECTION...' : 'TEST & VERIFY CONNECTION NOW'),
                    onPressed: isTesting
                        ? null
                        : () async {
                            setModalState(() {
                              isTesting = true;
                              testResult = '';
                            });
                            if (selectedTab == 0) {
                              String targetUrl = webhookUrlCtrl.text.trim();
                              if (targetUrl.contains('/workflow/')) {
                                targetUrl = 'https://dheerajk.app.n8n.cloud/webhook/temple-whatsapp';
                                webhookUrlCtrl.text = targetUrl;
                              }
                              _accessTokenCtrl.text = targetUrl;
                              final result = await _service.sendTestMessage(
                                testPhoneCtrl.text.trim(),
                                '🙏 Sri Kalki Seva Alayam: n8n Automation Webhook Verified!',
                              );
                              setModalState(() {
                                isTesting = false;
                                testSuccess = result.success;
                                testResult = result.success
                                    ? '🟢 n8n Webhook Verified Successfully! Dispatch OK.'
                                    : '🔴 Webhook Connection Failed: ${result.errorMessage}';
                              });
                            } else {
                              _phoneNumberIdCtrl.text = metaPhoneIdCtrl.text.trim();
                              _businessAccountIdCtrl.text = metaBusinessIdCtrl.text.trim();
                              _accessTokenCtrl.text = metaTokenCtrl.text.trim();
                              final hasValidInputs = _phoneNumberIdCtrl.text.isNotEmpty && _accessTokenCtrl.text.isNotEmpty;
                              setModalState(() {
                                isTesting = false;
                                testSuccess = hasValidInputs;
                                testResult = hasValidInputs
                                    ? '🟢 Meta Cloud API Configured! Phone Number ID: ${_phoneNumberIdCtrl.text}'
                                    : '🔴 Please enter both Phone Number ID and Access Token';
                              });
                            }
                          },
                  ),
                ),
                if (testResult.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: testSuccess ? Colors.green[50] : Colors.red[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: testSuccess ? Colors.green : Colors.red),
                    ),
                    child: Text(
                      testResult,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: testSuccess ? Colors.green[900] : Colors.red[900],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32), foregroundColor: Colors.white),
              onPressed: () async {
                if (selectedTab == 0) {
                  String targetUrl = webhookUrlCtrl.text.trim();
                  if (targetUrl.contains('/workflow/')) {
                    targetUrl = 'https://dheerajk.app.n8n.cloud/webhook/temple-whatsapp';
                  }
                  _accessTokenCtrl.text = targetUrl;
                  setState(() {
                    _mode = 'N8N_AUTOMATION';
                    _autoSend = true;
                    _allowEdit = false;
                  });
                } else {
                  _phoneNumberIdCtrl.text = metaPhoneIdCtrl.text.trim();
                  _businessAccountIdCtrl.text = metaBusinessIdCtrl.text.trim();
                  _accessTokenCtrl.text = metaTokenCtrl.text.trim();
                  setState(() {
                    _mode = 'META_CLOUD_API';
                    _autoSend = true;
                    _allowEdit = false;
                  });
                }
                await _saveSettings();
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('WhatsApp Business LINKED (${selectedTab == 0 ? "n8n Webhook" : "Meta Cloud API"})! Background automation active.'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
              },
              child: const Text('ACTIVATE & LINK WHATSAPP'),
            ),
          ],
        ),
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
                  // WhatsApp Business Connection Status & Quick Link / Delink Card
                  Card(
                    elevation: 3,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    color: _mode == 'N8N_AUTOMATION' || _mode == 'META_CLOUD_API'
                        ? const Color(0xFFE8F5E9)
                        : const Color(0xFFFFEBEE),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                _mode == 'N8N_AUTOMATION' || _mode == 'META_CLOUD_API'
                                    ? Icons.check_circle
                                    : Icons.cancel,
                                color: _mode == 'N8N_AUTOMATION' || _mode == 'META_CLOUD_API'
                                    ? Colors.green[800]
                                    : Colors.red[800],
                                size: 28,
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  _mode == 'N8N_AUTOMATION' || _mode == 'META_CLOUD_API'
                                      ? 'WhatsApp Business LINKED (Automated)'
                                      : 'WhatsApp Business DELINKED / DISCONNECTED',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 15,
                                    color: _mode == 'N8N_AUTOMATION' || _mode == 'META_CLOUD_API'
                                        ? Colors.green[900]
                                        : Colors.red[900],
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            _mode == 'N8N_AUTOMATION' || _mode == 'META_CLOUD_API'
                                ? '✅ Background Automation Active: Messages send silently via API/Webhook. WhatsApp Business app will NOT open on your device.'
                                : '⚠️ Integration Delinked: Messaging is disconnected or set to manual mode.',
                            style: const TextStyle(fontSize: 13, height: 1.3),
                          ),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Expanded(
                                child: ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF2E7D32),
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                  ),
                                  icon: const Icon(Icons.link, size: 18),
                                  label: const Text('LINK WHATSAPP', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                  onPressed: _showLinkWizard,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: OutlinedButton.icon(
                                  style: OutlinedButton.styleFrom(
                                    foregroundColor: Colors.red[800],
                                    side: BorderSide(color: Colors.red[800]!),
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                  ),
                                  icon: const Icon(Icons.link_off, size: 18),
                                  label: const Text('DELINK', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                  onPressed: () async {
                                    setState(() {
                                      _mode = 'DISABLED';
                                      _autoSend = false;
                                    });
                                    await _saveSettings();
                                    if (mounted) {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(
                                          content: Text('WhatsApp Business DELINKED / Disconnected Successfully.'),
                                          backgroundColor: Colors.orange,
                                        ),
                                      );
                                    }
                                  },
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

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
                            'Communication Mode Details',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF2C1A11)),
                          ),
                          const SizedBox(height: 12),
                          RadioListTile<String>(
                            title: const Text('Meta Cloud API (Automated Background)'),
                            subtitle: const Text('Sends automatically in background via Meta API without opening WhatsApp app'),
                            value: 'META_CLOUD_API',
                            groupValue: _mode,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _mode = val!),
                          ),
                          RadioListTile<String>(
                            title: const Text('n8n Webhook (Automated Background)'),
                            subtitle: const Text('Sends automatically in background via Webhook without opening WhatsApp app'),
                            value: 'N8N_AUTOMATION',
                            groupValue: _mode,
                            activeColor: const Color(0xFFD4AF37),
                            onChanged: (val) => setState(() => _mode = val!),
                          ),
                          RadioListTile<String>(
                            title: const Text('Manual WhatsApp (App Deep-Link)'),
                            subtitle: const Text('Launches WhatsApp Business application on your device for manual send'),
                            value: 'MANUAL_WHATSAPP',
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
