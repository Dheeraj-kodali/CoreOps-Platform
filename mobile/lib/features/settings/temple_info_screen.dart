import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';

class TempleInfoScreen extends StatefulWidget {
  const TempleInfoScreen({super.key});

  @override
  State<TempleInfoScreen> createState() => _TempleInfoScreenState();
}

class _TempleInfoScreenState extends State<TempleInfoScreen> {
  final _formKey = GlobalKey<FormState>();

  final _nameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _addressCtrl = TextEditingController();
  final _websiteCtrl = TextEditingController();
  final _mapsCtrl = TextEditingController();
  final _donationCtrl = TextEditingController();
  final _fbCtrl = TextEditingController();
  final _instaCtrl = TextEditingController();
  final _ytCtrl = TextEditingController();

  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadTempleInfo();
  }

  Future<void> _loadTempleInfo() async {
    final raw = await SQLiteDatabase.getTempleInfo();
    setState(() {
      _nameCtrl.text = raw['temple_name'] ?? '';
      _phoneCtrl.text = raw['temple_phone'] ?? '';
      _addressCtrl.text = raw['temple_address'] ?? '';
      _websiteCtrl.text = raw['website'] ?? '';
      _mapsCtrl.text = raw['google_maps_link'] ?? '';
      _donationCtrl.text = raw['donation_link'] ?? '';
      _fbCtrl.text = raw['facebook'] ?? '';
      _instaCtrl.text = raw['instagram'] ?? '';
      _ytCtrl.text = raw['youtube'] ?? '';
      _isLoading = false;
    });
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    final db = await SQLiteDatabase.instance;
    await db.insert('temple_info', {
      'id': 'temple_main',
      'temple_name': _nameCtrl.text.trim(),
      'temple_phone': _phoneCtrl.text.trim(),
      'temple_address': _addressCtrl.text.trim(),
      'website': _websiteCtrl.text.trim(),
      'google_maps_link': _mapsCtrl.text.trim(),
      'donation_link': _donationCtrl.text.trim(),
      'facebook': _fbCtrl.text.trim(),
      'instagram': _instaCtrl.text.trim(),
      'youtube': _ytCtrl.text.trim(),
    });

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Temple Information Saved Successfully'), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Temple Organization Info', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  children: [
                    _inputField(_nameCtrl, 'Temple Name *', required: true),
                    _inputField(_phoneCtrl, 'Temple Contact Phone *', required: true),
                    _inputField(_addressCtrl, 'Temple Address *', required: true),
                    _inputField(_websiteCtrl, 'Official Website URL'),
                    _inputField(_mapsCtrl, 'Google Maps Location Link'),
                    _inputField(_donationCtrl, 'Donation Portal Link'),
                    _inputField(_fbCtrl, 'Facebook Page URL'),
                    _inputField(_instaCtrl, 'Instagram Handle URL'),
                    _inputField(_ytCtrl, 'YouTube Channel URL'),
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
                        label: const Text('SAVE TEMPLE INFO', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _inputField(TextEditingController controller, String label, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (v) {
          if (required && (v == null || v.trim().isEmpty)) return 'Field is required';
          return null;
        },
      ),
    );
  }
}
