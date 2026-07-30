import 'package:flutter/material.dart';

class BroadcastCampaignItem {
  final String id;
  final String title;
  final String message;
  final String status;
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
  final List<BroadcastCampaignItem> _campaigns = [
    BroadcastCampaignItem(
      id: "camp-001",
      title: "Annual Brahmotsavam Invitation",
      message: "🙏 Namaste Devotee, Sri Kalki Seva Alayam invites you to Annual Brahmotsavam.",
      status: "COMPLETED",
      totalRecipients: 250,
      deliveredCount: 245,
      failedCount: 5,
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
    ),
    BroadcastCampaignItem(
      id: "camp-002",
      title: "Special Annadanam Announcement",
      message: "🙏 Mahaprasadam Annadanam Seva today at Sri Kalki Seva Alayam.",
      status: "SENDING",
      totalRecipients: 100,
      deliveredCount: 65,
      failedCount: 2,
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
    ),
  ];

  void _showCreateCampaignDialog() {
    final titleController = TextEditingController();
    final messageController = TextEditingController();
    bool isConfirmed = false;
    String selectedFilter = "ALL_DEVOTEES";

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text("Create Broadcast Campaign"),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: "Campaign Title",
                        hintText: "e.g., Festival Announcement",
                      ),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: selectedFilter,
                      decoration: const InputDecoration(labelText: "Target Audience"),
                      items: const [
                        DropdownMenuItem(value: "ALL_DEVOTEES", child: Text("All Devotees")),
                        DropdownMenuItem(value: "VILLAGE", child: Text("By Village")),
                        DropdownMenuItem(value: "REPEAT_VISITORS", child: Text("Repeat Visitors")),
                        DropdownMenuItem(value: "LAST_30_DAYS", child: Text("Visitors in Last 30 Days")),
                      ],
                      onChanged: (val) {
                        if (val != null) setDialogState(() => selectedFilter = val);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: messageController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: "Message Content",
                        hintText: "Enter Meta WhatsApp message text...",
                      ),
                    ),
                    const SizedBox(height: 12),
                    CheckboxListTile(
                      title: const Text("I confirm this broadcast dispatch (Safety Requirement)"),
                      value: isConfirmed,
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
                ElevatedButton(
                  onPressed: () {
                    if (titleController.text.trim().isEmpty || messageController.text.trim().isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Title and message cannot be empty")),
                      );
                      return;
                    }
                    if (!isConfirmed) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Explicit confirmation is required before dispatch")),
                      );
                      return;
                    }
                    setState(() {
                      _campaigns.insert(
                        0,
                        BroadcastCampaignItem(
                          id: "camp-${DateTime.now().millisecondsSinceEpoch}",
                          title: titleController.text.trim(),
                          message: messageController.text.trim(),
                          status: "QUEUED",
                          totalRecipients: 45,
                          deliveredCount: 0,
                          failedCount: 0,
                          createdAt: DateTime.now(),
                        ),
                      );
                    });
                    Navigator.pop(ctx);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("Broadcast Campaign Created & Queued Successfully")),
                    );
                  },
                  child: const Text("Create & Dispatch"),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case "COMPLETED":
        return Colors.green;
      case "SENDING":
      case "QUEUED":
        return Colors.orange;
      case "APPROVED":
        return Colors.blue;
      case "CANCELLED":
        return Colors.grey;
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
        title: const Text("Enterprise Broadcast System"),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showCreateCampaignDialog,
            tooltip: "New Campaign",
          ),
        ],
      ),
      body: _campaigns.isEmpty
          ? const Center(child: Text("No broadcast campaigns found."))
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: _campaigns.length,
              itemBuilder: (context, index) {
                final c = _campaigns[index];
                final progress = c.totalRecipients > 0 ? (c.deliveredCount / c.totalRecipients) : 0.0;

                return Card(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                c.title,
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ),
                            Chip(
                              label: Text(
                                c.status,
                                style: const TextStyle(color: Colors.white, fontSize: 12),
                              ),
                              backgroundColor: _getStatusColor(c.status),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          c.message,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(color: Colors.grey[700]),
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
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                            ),
                            if (c.failedCount > 0)
                              Text(
                                "Failed: ${c.failedCount}",
                                style: const TextStyle(fontSize: 12, color: Colors.red),
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCreateCampaignDialog,
        icon: const Icon(Icons.campaign),
        label: const Text("New Broadcast"),
      ),
    );
  }
}
