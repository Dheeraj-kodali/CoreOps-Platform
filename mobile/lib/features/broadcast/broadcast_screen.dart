import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/models/communication_models.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';

class BroadcastCampaignItem {
  final String id;
  final String title;
  final String message;
  final String status; // 'COMPLETED', 'SENDING', 'QUEUED', 'FAILED'
  final int totalRecipients;
  final int deliveredCount;
  final int failedCount;
  final DateTime createdAt;

  BroadcastCampaignItem({
    required this.id,
    required this.title,
    required this.message,
    required this.status,
    required this.totalRecipients,
    required this.deliveredCount,
    required this.failedCount,
    required this.createdAt,
  });
}

class BroadcastScreen extends StatefulWidget {
  const BroadcastScreen({super.key});

  @override
  State<BroadcastScreen> createState() => _BroadcastScreenState();
}

class _BroadcastScreenState extends State<BroadcastScreen> {
  final CommunicationService _commService = CommunicationService();
  bool _isLoading = true;
  List<Map<String, String>> _allContacts = [];
  List<String> _villages = [];
  String _selectedVillage = 'ALL';

  bool _isSending = false;
  int _currentProgress = 0;
  int _totalRecipients = 0;
  int _deliveredCount = 0;
  int _failedCount = 0;

  final List<BroadcastCampaignItem> _campaigns = [];

  @override
  void initState() {
    super.initState();
    _loadLedgerData();
  }

  Future<void> _loadLedgerData() async {
    setState(() => _isLoading = true);
    final contacts = await SQLiteDatabase.getAllUniqueDevoteeContacts(
      villageFilter: _selectedVillage == 'ALL' ? null : _selectedVillage,
    );
    final villageList = await SQLiteDatabase.getAllUniqueVillages();

    setState(() {
      _allContacts = contacts;
      _villages = ['ALL', ...villageList];
      _isLoading = false;
    });
  }

  void _showCreateCampaignDialog() {
    final titleController = TextEditingController(text: 'Festival & Temple Announcement');
    final messageController = TextEditingController(
      text: '🙏 Jai Kalki {name}!\n\nSri Kalki Seva Alayam invites you and your family for special Darshan and Mahaprasadam.\n\nDate: Festival Season 2026\nLocation: Temple Premises\n\nMay you be blessed with peace and prosperity.',
    );
    bool isConfirmed = false;
    String targetVillage = _selectedVillage;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            final filteredContacts = _allContacts.where((c) {
              if (targetVillage == 'ALL') return true;
              return c['village']?.toLowerCase() == targetVillage.toLowerCase();
            }).toList();

            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Row(
                children: const [
                  Icon(Icons.campaign, color: Color(0xFFD4AF37)),
                  SizedBox(width: 8),
                  Text("New Devotee Broadcast", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ],
              ),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Recipient Ledger Badge
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFF8E7),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFD4AF37)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.people, color: Color(0xFF2C1A11)),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text("Audience from Temple Ledger", style: TextStyle(fontSize: 11, color: Colors.grey)),
                                Text(
                                  "${filteredContacts.length} Unique Devotees Registered",
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF2C1A11)),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),

                    // Campaign Title
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: "Campaign Title",
                        hintText: "e.g., Mahaprasadam Announcement",
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Audience Filter
                    DropdownButtonFormField<String>(
                      value: targetVillage,
                      decoration: const InputDecoration(
                        labelText: "Filter Target Village",
                        border: OutlineInputBorder(),
                      ),
                      items: _villages.map((v) {
                        return DropdownMenuItem(
                          value: v,
                          child: Text(v == 'ALL' ? "All Villages & Devotees (${_allContacts.length})" : "Village: $v"),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setDialogState(() => targetVillage = val);
                        }
                      },
                    ),
                    const SizedBox(height: 12),

                    // Message Content Text Field
                    TextField(
                      controller: messageController,
                      maxLines: 5,
                      decoration: const InputDecoration(
                        labelText: "Designed Message Content",
                        hintText: "Enter WhatsApp message text... (Supports {name}, {village}, {temple})",
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      "Placeholders: {name} = Devotee Name, {village} = Devotee Village, {temple} = Temple Name",
                      style: TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                    const SizedBox(height: 12),

                    // Preset Templates Chips
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: [
                        ActionChip(
                          avatar: const Icon(Icons.festival, size: 14),
                          label: const Text("Festival Darshan", style: TextStyle(fontSize: 11)),
                          onPressed: () {
                            setDialogState(() {
                              titleController.text = "Festival Darshan Invitation";
                              messageController.text = "🙏 Jai Kalki {name}!\n\nWe cordially invite you and your family for the auspicious Festival Darshan at Sri Kalki Seva Alayam.\n\nVillage: {village}\nMay divine blessings be upon you.";
                            });
                          },
                        ),
                        ActionChip(
                          avatar: const Icon(Icons.restaurant, size: 14),
                          label: const Text("Mahaprasadam", style: TextStyle(fontSize: 11)),
                          onPressed: () {
                            setDialogState(() {
                              titleController.text = "Mahaprasadam Seva Notice";
                              messageController.text = "🙏 Namaste {name}!\n\nMahaprasadam Annadanam Seva is arranged today at Sri Kalki Seva Alayam. Please visit and receive divine prasadam.";
                            });
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Safety Confirmation Checkbox
                    CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(
                        "I confirm sending this message to ${filteredContacts.length} devotees via n8n WhatsApp automation.",
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                      value: isConfirmed,
                      activeColor: const Color(0xFFD4AF37),
                      onChanged: (val) {
                        setDialogState(() => isConfirmed = val ?? false);
                      },
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text("Cancel"),
                ),
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFD4AF37),
                    foregroundColor: Colors.black,
                  ),
                  icon: const Icon(Icons.send),
                  label: Text("SEND TO ALL (${filteredContacts.length})", style: const TextStyle(fontWeight: FontWeight.bold)),
                  onPressed: () {
                    if (titleController.text.trim().isEmpty || messageController.text.trim().isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Campaign title and message content cannot be empty")),
                      );
                      return;
                    }
                    if (!isConfirmed) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Please check the confirmation box before sending broadcast")),
                      );
                      return;
                    }
                    Navigator.pop(ctx);
                    _executeBroadcastDispatch(
                      title: titleController.text.trim(),
                      messageTemplate: messageController.text.trim(),
                      recipients: filteredContacts,
                    );
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _executeBroadcastDispatch({
    required String title,
    required String messageTemplate,
    required List<Map<String, String>> recipients,
  }) async {
    if (recipients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("No devotees found in ledger for broadcast")),
      );
      return;
    }

    setState(() {
      _isSending = true;
      _currentProgress = 0;
      _totalRecipients = recipients.length;
      _deliveredCount = 0;
      _failedCount = 0;
    });

    final settings = await _commService.getSettings();
    final rawTemple = await SQLiteDatabase.getTempleInfo();
    final templeName = rawTemple['temple_name'] ?? 'Sri Kalki Seva Alayam';

    // Provider override: use N8NWhatsAppProvider by default as requested
    ChannelProvider provider;
    if (settings.mode == 'META_CLOUD_API') {
      provider = MetaWhatsAppProvider(settings);
    } else {
      provider = N8NWhatsAppProvider(settings);
    }

    final campaignId = "camp-${DateTime.now().millisecondsSinceEpoch}";

    for (int i = 0; i < recipients.length; i++) {
      final contact = recipients[i];
      final rawPhone = contact['phone'] ?? '';
      final name = contact['name'] ?? 'Devotee';
      final village = contact['village'] ?? '';

      final rendered = messageTemplate
          .replaceAll('{name}', name)
          .replaceAll('{{name}}', name)
          .replaceAll('{village}', village)
          .replaceAll('{{village}}', village)
          .replaceAll('{temple}', templeName)
          .replaceAll('{{temple}}', templeName);

      final formattedPhone = CommunicationService.formatPhoneNumberForWhatsApp(rawPhone);
      final res = await provider.sendMessage(formattedPhone, rendered);

      if (res.success) {
        _deliveredCount++;
      } else {
        _failedCount++;
      }

      // Record History
      await SQLiteDatabase.insertCommunicationHistory({
        'id': campaignId + "_$i",
        'visitor_id': 'BROADCAST',
        'phone': formattedPhone,
        'channel': provider.channelName,
        'template_type': 'BROADCAST',
        'rendered_message': rendered,
        'status': res.success ? 'SENT' : 'FAILED',
        'meta_message_id': res.metaMessageId,
        'error_message': res.errorMessage,
        'failure_reason': res.errorMessage,
        'created_at': DateTime.now().toIso8601String(),
      });

      if (mounted) {
        setState(() {
          _currentProgress = i + 1;
        });
      }
    }

    final newItem = BroadcastCampaignItem(
      id: campaignId,
      title: title,
      message: messageTemplate,
      status: 'COMPLETED',
      totalRecipients: recipients.length,
      deliveredCount: _deliveredCount,
      failedCount: _failedCount,
      createdAt: DateTime.now(),
    );

    if (mounted) {
      setState(() {
        _campaigns.insert(0, newItem);
        _isSending = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Broadcast Completed! Delivered: $_deliveredCount / ${recipients.length} via ${provider.channelName}"),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case "COMPLETED":
        return Colors.green;
      case "SENDING":
      case "QUEUED":
        return Colors.orange;
      case "FAILED":
        return Colors.red;
      default:
        return Colors.blueGrey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("n8n Devotee Broadcast System", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadLedgerData,
            tooltip: "Refresh Devotee Ledger",
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : Column(
              children: [
                // Top Header Card with Ledger Stats
                Card(
                  margin: const EdgeInsets.all(12),
                  elevation: 3,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const CircleAvatar(
                              backgroundColor: Color(0xFFD4AF37),
                              child: Icon(Icons.campaign, color: Colors.black),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text("Historical Devotee Ledger", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                  Text(
                                    "${_allContacts.length} Total Registered Phone Numbers",
                                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                                  ),
                                ],
                              ),
                            ),
                            DropdownButton<String>(
                              value: _selectedVillage,
                              items: _villages.map((v) {
                                return DropdownMenuItem(
                                  value: v,
                                  child: Text(v == 'ALL' ? 'All Villages' : v, style: const TextStyle(fontSize: 12)),
                                );
                              }).toList(),
                              onChanged: (val) {
                                if (val != null) {
                                  setState(() => _selectedVillage = val);
                                  _loadLedgerData();
                                }
                              },
                            ),
                          ],
                        ),
                        if (_isSending) ...[
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text("Dispatching to Devotees: $_currentProgress / $_totalRecipients", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                              Text("Delivered: $_deliveredCount | Failed: $_failedCount", style: const TextStyle(fontSize: 12, color: Colors.green)),
                            ],
                          ),
                          const SizedBox(height: 6),
                          LinearProgressIndicator(
                            value: _totalRecipients > 0 ? (_currentProgress / _totalRecipients) : 0,
                            backgroundColor: Colors.grey[300],
                            color: const Color(0xFFD4AF37),
                            minHeight: 8,
                          ),
                        ],
                      ],
                    ),
                  ),
                ),

                // Campaigns List
                Expanded(
                  child: _campaigns.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.send_to_mobile, size: 48, color: Colors.grey),
                              const SizedBox(height: 12),
                              Text(
                                "No Broadcast Campaigns Sent Yet.\nTap 'CREATE & SEND BROADCAST' to dispatch a custom message to all ${_allContacts.length} devotees in ledger.",
                                textAlign: TextAlign.center,
                                style: const TextStyle(color: Colors.grey),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          itemCount: _campaigns.length,
                          itemBuilder: (context, index) {
                            final c = _campaigns[index];
                            final progress = c.totalRecipients > 0 ? (c.deliveredCount / c.totalRecipients) : 0.0;

                            return Card(
                              margin: const EdgeInsets.only(bottom: 12.0),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              elevation: 2,
                              child: Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Expanded(
                                          child: Text(
                                            c.title,
                                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                          ),
                                        ),
                                        Chip(
                                          label: Text(
                                            c.status,
                                            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                                          ),
                                          backgroundColor: _getStatusColor(c.status),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      c.message,
                                      maxLines: 3,
                                      overflow: TextOverflow.ellipsis,
                                      style: TextStyle(color: Colors.grey[800], fontSize: 13),
                                    ),
                                    const SizedBox(height: 12),
                                    LinearProgressIndicator(
                                      value: progress.clamp(0.0, 1.0),
                                      backgroundColor: Colors.grey[200],
                                      color: _getStatusColor(c.status),
                                    ),
                                    const SizedBox(height: 8),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          "Delivered: ${c.deliveredCount}/${c.totalRecipients} (${(progress * 100).toStringAsFixed(1)}%)",
                                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                                        ),
                                        if (c.failedCount > 0)
                                          Text(
                                            "Failed: ${c.failedCount}",
                                            style: const TextStyle(fontSize: 12, color: Colors.red, fontWeight: FontWeight.bold),
                                          ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _isSending ? null : _showCreateCampaignDialog,
        backgroundColor: const Color(0xFFD4AF37),
        foregroundColor: Colors.black,
        icon: const Icon(Icons.campaign),
        label: Text(
          "CREATE & SEND BROADCAST (${_allContacts.length})",
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
