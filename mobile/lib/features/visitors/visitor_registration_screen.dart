import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/services/communication_service.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/models/communication_models.dart';
import 'package:temple_visitor_app/models/person_model.dart';

class VisitorRegistrationScreen extends StatefulWidget {
  final VoidCallback onVisitorAdded;

  const VisitorRegistrationScreen({super.key, required this.onVisitorAdded});

  @override
  State<VisitorRegistrationScreen> createState() => _VisitorRegistrationScreenState();
}

class _VisitorRegistrationScreenState extends State<VisitorRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _repository = VisitorRepository();

  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _villageController = TextEditingController();
  final _notesController = TextEditingController();
  final _customPurposeController = TextEditingController();

  String _selectedPurpose = 'General Darshan';
  int _membersCount = 1;
  bool _isSubmitting = false;

  PersonModel? _matchedPerson;
  bool _isAutoFilled = false;

  final List<String> _purposes = [
    'General Darshan',
    'Special Seva',
    'Voluntary Work',
    'Annadanam',
    'Donation / Prasadam',
    'Other',
  ];

  @override
  void initState() {
    super.initState();
    _phoneController.addListener(_onPhoneChanged);
  }

  @override
  void dispose() {
    _phoneController.removeListener(_onPhoneChanged);
    _nameController.dispose();
    _phoneController.dispose();
    _villageController.dispose();
    _notesController.dispose();
    _customPurposeController.dispose();
    super.dispose();
  }

  Future<void> _onPhoneChanged() async {
    final phone = _phoneController.text.trim();
    if (phone.length >= 5) {
      var person = await _repository.getPersonByPhone(phone);

      // Perform remote API phone lookup if local record not found
      if (person == null && phone.length >= 10) {
        try {
          final remoteResp = await _repository.lookupPhone(phone);
          if (remoteResp != null && (remoteResp['profile_exists'] == true || remoteResp['profile'] != null)) {
            final prof = remoteResp['profile'];
            final lastV = remoteResp['last_visit'];
            if (prof != null) {
              person = PersonModel(
                personId: prof['id']?.toString() ?? '',
                name: prof['name']?.toString() ?? '',
                phone: prof['phone_number']?.toString() ?? phone,
                village: prof['village']?.toString() ?? prof['city']?.toString() ?? 'Local',
                firstVisit: lastV?['first_visit']?.toString() ?? 'Today',
                lastVisit: lastV?['last_visit_date']?.toString() ?? 'Recently',
                totalVisits: lastV?['total_visits'] != null ? int.tryParse(lastV['total_visits'].toString()) ?? 1 : 1,
                createdAt: DateTime.now().toIso8601String(),
                updatedAt: DateTime.now().toIso8601String(),
              );
            }
          }
        } catch (_) {}
      }

      if (mounted) {
        setState(() {
          _matchedPerson = person;
          if (person != null) {
            _isAutoFilled = true;
            // Google Password Manager Style Auto-fill into editable fields
            _nameController.text = person.name;
            _villageController.text = person.village;
          } else {
            _isAutoFilled = false;
          }
        });
      }
    } else if (_matchedPerson != null) {
      setState(() {
        _matchedPerson = null;
        _isAutoFilled = false;
      });
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    final finalPurpose = _selectedPurpose == 'Other'
        ? _customPurposeController.text.trim()
        : _selectedPurpose;

    try {
      final visitorModel = await _repository.registerVisitor(
        name: _nameController.text.trim(),
        phoneNumber: _phoneController.text.trim(),
        village: _villageController.text.trim(),
        purpose: finalPurpose,
        personsCount: _membersCount,
        notes: _notesController.text.trim(),
      );

      if (!mounted) return;

      // Check if Allow Edit Before Sending is enabled
      final commService = CommunicationService();
      final settings = await commService.getSettings();

      if (settings.mode != 'DISABLED' && settings.allowEdit) {
        final tmplData = await SQLiteDatabase.getTemplate('ENTRY');
        final rawText = tmplData?['message']?.toString() ?? '🙏 Welcome {name}\n\nYou have successfully entered\n{temple}\n\nEntry Time:\n{time}\n\nHave a blessed day.';
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

        final rendered = TemplateEngine.render(
          templateText: rawText,
          visitor: visitorModel,
          templeInfo: templeInfo,
        );

        final msgCtrl = TextEditingController(text: rendered);

        if (!mounted) return;

        await showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Edit Entry WhatsApp Message', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            content: TextField(
              controller: msgCtrl,
              maxLines: 6,
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            actions: [
              TextButton(
                onPressed: () async {
                  Navigator.pop(ctx);
                  if (settings.autoSend) {
                    final res = await commService.sendVisitorEntryMessage(visitorModel);
                    if (mounted && res != null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(res.success
                              ? 'Auto WhatsApp Message Sent (ID: ${res.metaMessageId})'
                              : 'Auto WhatsApp Failed: ${res.errorMessage}'),
                          backgroundColor: res.success ? Colors.green : Colors.red,
                          duration: const Duration(seconds: 4),
                        ),
                      );
                    }
                  }
                },
                child: const Text('Skip'),
              ),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFD4AF37), foregroundColor: Colors.black),
                icon: const Icon(Icons.send, size: 18),
                label: const Text('SEND NOW', style: TextStyle(fontWeight: FontWeight.bold)),
                onPressed: () async {
                  final result = await commService.dispatchDirectMessage(
                    visitor: visitorModel,
                    templateType: 'ENTRY',
                    customMessage: msgCtrl.text.trim(),
                  );
                  if (ctx.mounted) Navigator.pop(ctx);
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(result.success
                            ? 'WhatsApp Message Sent (ID: ${result.metaMessageId})'
                            : 'WhatsApp Delivery Failed: ${result.errorMessage}'),
                        backgroundColor: result.success ? Colors.green : Colors.red,
                        duration: const Duration(seconds: 4),
                      ),
                    );
                  }
                },
              ),
            ],
          ),
        );
      } else {
        // Automatic sending branch when allowEdit is disabled
        final result = await commService.sendVisitorEntryMessage(visitorModel);
        if (mounted && result != null && settings.mode != 'DISABLED') {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result.success
                  ? 'WhatsApp Message Sent Automatically (ID: ${result.metaMessageId})'
                  : 'WhatsApp Automatic Dispatch Failed: ${result.errorMessage}'),
              backgroundColor: result.success ? Colors.green : Colors.red,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      }

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Visitor Entered & Registered Successfully'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );

      // Reset Form
      _nameController.clear();
      _phoneController.clear();
      _villageController.clear();
      _notesController.clear();
      setState(() {
        _selectedPurpose = 'General Darshan';
        _membersCount = 1;
        _matchedPerson = null;
      });

      widget.onVisitorAdded();
    } catch (e) {
      if (!mounted) return;
      final errorStr = e.toString();
      final isAlreadyInside = errorStr.contains('Visitor already inside temple');
      final msg = isAlreadyInside ? 'Visitor already inside temple.' : 'Error registering visitor: $e';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(msg, style: const TextStyle(fontWeight: FontWeight.bold)),
          backgroundColor: isAlreadyInside ? Colors.orange[900] : Colors.red,
          duration: const Duration(seconds: 4),
        ),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'New Visitor Entry Form',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
            ),
            const SizedBox(height: 16),

            // Mobile Number (Required - Auto Searches Person Table)
            TextFormField(
              controller: _phoneController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Mobile Number *',
                prefixIcon: Icon(Icons.phone, color: Color(0xFFD4AF37)),
                border: OutlineInputBorder(),
                helperText: 'Auto-completes details for returning visitors',
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Mobile Number is required';
                if (v.trim().length < 10) return 'Enter a valid 10-digit mobile number';
                return null;
              },
            ),
            const SizedBox(height: 10),

            // Repeat Visitor Recognition Banner (Google Password Manager Style Auto-Fill)
            if (_matchedPerson != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFD4AF37)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.vpn_key_rounded, color: Color(0xFFD4AF37), size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '🔑 Auto-Filled Repeat Visitor Profile',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.brown.shade900),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Matched ${_matchedPerson!.name} (${_matchedPerson!.totalVisits} previous visits). All fields below remain fully editable.',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Colors.black87),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
            ],

            // Visitor Name (Required - Fully Editable)
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Visitor Name *',
                prefixIcon: Icon(Icons.person, color: Color(0xFFD4AF37)),
                border: OutlineInputBorder(),
                helperText: 'Editable for profile updates',
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Visitor Name is required';
                return null;
              },
            ),
            const SizedBox(height: 14),

            // Village / City (Required - Fully Editable)
            TextFormField(
              controller: _villageController,
              decoration: const InputDecoration(
                labelText: 'Village / City *',
                prefixIcon: Icon(Icons.location_city, color: Color(0xFFD4AF37)),
                border: OutlineInputBorder(),
                helperText: 'Editable for profile updates',
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Village is required';
                return null;
              },
            ),
            const SizedBox(height: 14),

            // Purpose of Visit (Required)
            DropdownButtonFormField<String>(
              value: _selectedPurpose,
              decoration: const InputDecoration(
                labelText: 'Purpose of Visit *',
                prefixIcon: Icon(Icons.temple_hindu, color: Color(0xFFD4AF37)),
                border: OutlineInputBorder(),
              ),
              items: _purposes
                  .map((p) => DropdownMenuItem(value: p, child: Text(p)))
                  .toList(),
              onChanged: (v) {
                if (v != null) setState(() => _selectedPurpose = v);
              },
            ),

            // Custom Purpose Field (Only shown when "Other" is selected)
            if (_selectedPurpose == 'Other') ...[
              const SizedBox(height: 14),
              TextFormField(
                controller: _customPurposeController,
                decoration: const InputDecoration(
                  labelText: 'Specify Custom Purpose *',
                  hintText: 'e.g. Marriage Blessing, Archana, Special Darshan',
                  prefixIcon: Icon(Icons.edit_note, color: Color(0xFFD4AF37)),
                  border: OutlineInputBorder(),
                ),
                validator: (v) {
                  if (_selectedPurpose == 'Other' && (v == null || v.trim().isEmpty)) {
                    return 'Please specify custom purpose';
                  }
                  return null;
                },
              ),
            ],
            const SizedBox(height: 14),

            // Number of Members (Must be >= 1)
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Number of Members *',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.remove_circle_outline, size: 32, color: Colors.red),
                  onPressed: () {
                    if (_membersCount > 1) {
                      setState(() => _membersCount--);
                    }
                  },
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.amber),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '$_membersCount',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add_circle_outline, size: 32, color: Colors.green),
                  onPressed: () {
                    setState(() => _membersCount++);
                  },
                ),
              ],
            ),
            const SizedBox(height: 14),

            // Notes (Optional)
            TextFormField(
              controller: _notesController,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Notes (Optional)',
                prefixIcon: Icon(Icons.note, color: Colors.grey),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),

            // Large Reception-Friendly "VISITOR ENTERED" Button
            SizedBox(
              height: 56,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFD4AF37),
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: _isSubmitting ? null : _submitForm,
                icon: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.black)
                    : const Icon(Icons.login, size: 28),
                label: Text(
                  _isSubmitting ? 'PROCESSING...' : 'VISITOR ENTERED',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

