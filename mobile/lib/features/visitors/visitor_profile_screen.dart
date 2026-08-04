import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/services/central_sync_manager.dart';
import 'package:temple_visitor_app/models/person_model.dart';
import 'package:temple_visitor_app/models/visit_model.dart';

class VisitorProfileScreen extends StatefulWidget {
  final String personId;
  const VisitorProfileScreen({Key? key, required this.personId}) : super(key: key);

  @override
  State<VisitorProfileScreen> createState() => _VisitorProfileScreenState();
}

class _VisitorProfileScreenState extends State<VisitorProfileScreen> {
  final VisitorRepository _repository = VisitorRepository();
  StreamSubscription? _syncSub;
  PersonModel? _person;
  List<VisitModel> _visits = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
    _syncSub = CentralSyncManager.instance.onSyncCompleted.listen((_) {
      _loadProfile(silent: true);
    });
  }

  @override
  void dispose() {
    _syncSub?.cancel();
    super.dispose();
  }

  Future<void> _loadProfile({bool silent = false}) async {
    if (!silent && _person == null) {
      setState(() => _isLoading = true);
    }
    final person = await _repository.getPersonById(widget.personId);
    final visits = await _repository.getVisitsForPerson(widget.personId);
    if (mounted) {
      setState(() {
        _person = person;
        _visits = visits;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Visitor Profile',
          style: GoogleFonts.cinzel(fontWeight: FontWeight.bold, color: const Color(0xFFD4AF37)),
        ),
        backgroundColor: const Color(0xFF2C1A11),
        iconTheme: const IconThemeData(color: Color(0xFFD4AF37)),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : _person == null
              ? const Center(child: Text('Visitor profile not found'))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header Profile Card
                      Card(
                        elevation: 3,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Row(
                            children: [
                              CircleAvatar(
                                radius: 32,
                                backgroundColor: const Color(0xFFD4AF37).withOpacity(0.2),
                                child: Text(
                                  _person!.name.isNotEmpty ? _person!.name[0].toUpperCase() : 'V',
                                  style: GoogleFonts.cinzel(fontSize: 26, fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _person!.name,
                                      style: GoogleFonts.cinzel(fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        const Icon(Icons.phone, size: 14, color: Colors.grey),
                                        const SizedBox(width: 4),
                                        Text(_person!.phone, style: const TextStyle(color: Colors.grey, fontSize: 13)),
                                      ],
                                    ),
                                    const SizedBox(height: 2),
                                    Row(
                                      children: [
                                        const Icon(Icons.location_on, size: 14, color: Colors.grey),
                                        const SizedBox(width: 4),
                                        Text(_person!.village, style: const TextStyle(color: Colors.grey, fontSize: 13)),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Metrics Row
                      Row(
                        children: [
                          Expanded(
                            child: _metricCard('Total Visits', '${_person!.totalVisits}', Icons.history, const Color(0xFFD4AF37)),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: _metricCard('First Visit', _person!.firstVisit.split(' ')[0], Icons.calendar_today, Colors.blue),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: _metricCard('Last Visit', _person!.lastVisit.split(' ')[0], Icons.event, Colors.green),
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),

                      // History Header
                      Text(
                        'Chronological Visit History (${_visits.length})',
                        style: GoogleFonts.cinzel(fontSize: 16, fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                      ),
                      const SizedBox(height: 10),

                      // Visit History List
                      ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _visits.length,
                        itemBuilder: (context, index) {
                          final visit = _visits[index];
                          final isInside = visit.status == 'CHECKED_IN' || visit.status == 'INSIDE';

                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 6),
                            elevation: 1.5,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: ListTile(
                              leading: Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: isInside ? Colors.green.withOpacity(0.15) : Colors.grey.withOpacity(0.15),
                                  shape: BoxShape.circle,
                                ),
                                child: Icon(
                                  isInside ? Icons.door_sliding : Icons.check_circle_outline,
                                  color: isInside ? Colors.green : Colors.grey,
                                  size: 20,
                                ),
                              ),
                              title: Text(
                                '${visit.purpose} (${visit.groupMembers} members)',
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text('Time In: ${visit.checkIn}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                  if (visit.checkOut != null && visit.checkOut!.isNotEmpty)
                                    Text('Time Out: ${visit.checkOut}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                  if (visit.notes != null && visit.notes!.isNotEmpty)
                                    Text('Notes: ${visit.notes}', style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
                                ],
                              ),
                              trailing: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: isInside ? Colors.green.shade50 : Colors.grey.shade100,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: isInside ? Colors.green : Colors.grey.shade400),
                                ),
                                child: Text(
                                  isInside ? 'INSIDE' : 'LEFT',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: isInside ? Colors.green.shade800 : Colors.grey.shade800,
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _metricCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 6),
            Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: color)),
            const SizedBox(height: 2),
            Text(title, style: const TextStyle(fontSize: 11, color: Colors.grey), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}
