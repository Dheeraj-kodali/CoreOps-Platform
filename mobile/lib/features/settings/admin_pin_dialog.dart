import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/services/admin_security_service.dart';

class AdminPinDialog extends StatefulWidget {
  final VoidCallback onUnlocked;

  const AdminPinDialog({super.key, required this.onUnlocked});

  @override
  State<AdminPinDialog> createState() => _AdminPinDialogState();
}

class _AdminPinDialogState extends State<AdminPinDialog> {
  final _pinController = TextEditingController();
  String _errorMessage = '';
  bool _isChecking = false;

  Future<void> _verify() async {
    final pin = _pinController.text.trim();
    if (pin.isEmpty) {
      setState(() => _errorMessage = 'Please enter Admin PIN');
      return;
    }

    setState(() {
      _isChecking = true;
      _errorMessage = '';
    });

    final res = await AdminSecurityService.verifyPin(pin);

    if (!mounted) return;

    if (res['success'] == true) {
      Navigator.pop(context);
      widget.onUnlocked();
    } else {
      setState(() {
        _isChecking = false;
        _errorMessage = res['message'] ?? 'Incorrect PIN';
        _pinController.clear();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: const [
          Icon(Icons.lock, color: Color(0xFFD4AF37)),
          SizedBox(width: 8),
          Text('Admin PIN Required', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Enter Administrator Security PIN to access configuration settings (Default: 1234):'),
          const SizedBox(height: 14),
          TextField(
            controller: _pinController,
            obscureText: true,
            keyboardType: TextInputType.number,
            maxLength: 6,
            autofocus: true,
            decoration: const InputDecoration(
              labelText: 'Admin PIN',
              prefixIcon: Icon(Icons.security, color: Color(0xFFD4AF37)),
              border: OutlineInputBorder(),
              counterText: '',
            ),
            onSubmitted: (_) => _verify(),
          ),
          if (_errorMessage.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              _errorMessage,
              style: const TextStyle(color: Colors.red, fontSize: 12, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFD4AF37),
            foregroundColor: Colors.black,
          ),
          onPressed: _isChecking ? null : _verify,
          child: Text(_isChecking ? 'Verifying...' : 'Unlock Portal', style: const TextStyle(fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}
