import 'package:flutter/material.dart';

class VisitorLeftConfirmationDialog extends StatelessWidget {
  final String visitorName;
  final String timeIn;
  final VoidCallback onConfirm;

  const VisitorLeftConfirmationDialog({
    super.key,
    required this.visitorName,
    required this.timeIn,
    required this.onConfirm,
  });

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final currentTimeStr = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: const Text(
        'Confirm Visitor Left?',
        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.orange),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Are you sure this visitor has exited the temple grounds?'),
          const SizedBox(height: 14),
          _infoRow('Visitor Name:', visitorName),
          _infoRow('Time In:', timeIn),
          _infoRow('Current Time (Out):', currentTimeStr),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel', style: TextStyle(color: Colors.grey, fontSize: 15)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.orange,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          ),
          onPressed: () {
            Navigator.pop(context);
            onConfirm();
          },
          child: const Text('Confirm', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
        ),
      ],
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: Colors.grey)),
          Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
