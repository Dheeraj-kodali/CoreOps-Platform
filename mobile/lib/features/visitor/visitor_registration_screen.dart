import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:uuid/uuid.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/core/database/sqlite_helper.dart';

class VisitorRegistrationScreen extends StatefulWidget {
  const VisitorRegistrationScreen({Key? key}) : super(key: key);

  @override
  State<VisitorRegistrationScreen> createState() => _VisitorRegistrationScreenState();
}

class _VisitorRegistrationScreenState extends State<VisitorRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _ageController = TextEditingController();
  final _villageController = TextEditingController();
  final _serviceController = TextEditingController();
  final _notesController = TextEditingController();

  String _gender = 'MALE';
  int _personsCount = 1;
  int _purposeId = 1;
  bool _isSubmitting = false;

  final List<Map<String, dynamic>> _purposes = [
    {'id': 1, 'name_en': 'General Darshan', 'name_te': 'సాధారణ దర్శనం'},
    {'id': 2, 'name_en': 'Special Seva / Archana', 'name_te': 'ప్రత్యేక సేవ / అర్చన'},
    {'id': 3, 'name_en': 'Voluntary Service', 'name_te': 'స్వచ్ఛంద సేవ'},
    {'id': 4, 'name_en': 'Annadanam / Donation', 'name_te': 'విరాళం / అన్నదానం'},
  ];

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    final now = DateTime.now();
    final visitorUuid = const Uuid().v4();

    final visitorData = {
      'visitor_uuid': visitorUuid,
      'name': _nameController.text.trim(),
      'phone_number': _phoneController.text.trim(),
      'gender': _gender,
      'age': int.parse(_ageController.text.trim()),
      'persons_count': _personsCount,
      'village_name_custom': _villageController.text.trim(),
      'purpose_id': _purposeId,
      'temple_service': _serviceController.text.trim(),
      'visitor_date': now.toIso8601String().split('T')[0],
      'visitor_time': '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:00',
      'notes': _notesController.text.trim(),
      'sync_status': 'PENDING',
      'created_at': now.toIso8601String(),
    };

    await SQLiteHelper.insertVisitor(visitorData);

    setState(() => _isSubmitting = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Visitor registered successfully! (Stored locally)'),
          backgroundColor: const Color(0xFF2C1A11),
        ),
      );
      _formKey.currentState!.reset();
      _nameController.clear();
      _phoneController.clear();
      _ageController.clear();
      _villageController.clear();
      _serviceController.clear();
      _notesController.clear();
      setState(() {
        _personsCount = 1;
        _purposeId = 1;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.visitorRegistration),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Enter Visitor Details',
                style: GoogleFonts.cinzel(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF2C1A11),
                ),
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: loc.name,
                  prefixIcon: const Icon(Icons.person, color: Color(0xFFD4AF37)),
                ),
                validator: (v) => v == null || v.isEmpty ? 'Please enter name' : null,
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: InputDecoration(
                  labelText: loc.phone,
                  prefixIcon: const Icon(Icons.phone, color: Color(0xFFD4AF37)),
                ),
                validator: (v) => v == null || v.length < 10 ? 'Enter valid phone number' : null,
              ),
              const SizedBox(height: 14),

              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _gender,
                      decoration: InputDecoration(labelText: loc.gender),
                      items: const [
                        DropdownMenuItem(value: 'MALE', child: Text('Male')),
                        DropdownMenuItem(value: 'FEMALE', child: Text('Female')),
                        DropdownMenuItem(value: 'OTHER', child: Text('Other')),
                      ],
                      onChanged: (val) => setState(() => _gender = val!),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _ageController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(labelText: loc.age),
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              // Persons Count Counter
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    loc.persons,
                    style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                  ),
                  Row(
                    children: [
                      IconButton(
                        onPressed: _personsCount > 1 ? () => setState(() => _personsCount--) : null,
                        icon: const Icon(Icons.remove_circle_outline, color: Color(0xFFD4AF37)),
                      ),
                      Text(
                        '$_personsCount',
                        style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      IconButton(
                        onPressed: () => setState(() => _personsCount++),
                        icon: const Icon(Icons.add_circle_outline, color: Color(0xFFD4AF37)),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 14),

              DropdownButtonFormField<int>(
                value: _purposeId,
                decoration: InputDecoration(labelText: loc.purpose),
                items: _purposes.map((p) {
                  return DropdownMenuItem<int>(
                    value: p['id'] as int,
                    child: Text(p['name_en'] as String),
                  );
                }).toList(),
                onChanged: (val) => setState(() => _purposeId = val!),
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _villageController,
                decoration: InputDecoration(
                  labelText: loc.village,
                  prefixIcon: const Icon(Icons.location_on, color: Color(0xFFD4AF37)),
                ),
              ),
              const SizedBox(height: 14),

              TextFormField(
                controller: _serviceController,
                decoration: InputDecoration(
                  labelText: loc.service,
                  prefixIcon: const Icon(Icons.star, color: Color(0xFFD4AF37)),
                ),
              ),
              const SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submitForm,
                  child: _isSubmitting
                      ? const CircularProgressIndicator(color: Color(0xFF2C1A11))
                      : Text(loc.submit),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
