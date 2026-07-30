import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/models/communication_models.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/features/visitors/visitor_left_confirmation_dialog.dart';
import 'package:temple_visitor_app/features/visitors/visitor_profile_screen.dart';

class VisitorDetailDialog extends StatefulWidget {
  final VisitorModel visitor;
  final VoidCallback onCheckOut;

  const VisitorDetailDialog({
    super.key,
    required this.visitor,
    required this.onCheckOut,
  });

  @override
  State<VisitorDetailDialog> createState() => _VisitorDetailDialogState();
}

class _VisitorDetailDialogState extends State<VisitorDetailDialog> {
  final VisitorRepository _repository = VisitorRepository();
  List<CommunicationHistory> _commHistory = [];
  bool _isLoadingHistory = true;

  @override
  void initState() {
    super.initState();
    _loadCommHistory();
  }

  Future<void> _loadCommHistory() async {
    final list = await SQLiteDatabase.getCommunicationHistoryByVisitor(widget.visitor.id);
    if (mounted) {
      setState(() {
        _commHistory = list.map((m) => CommunicationHistory.fromJson(m)).toList();
        _isLoadingHistory = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCheckedIn = widget.visitor.status == 'CHECKED_IN';

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      widget.visitor.name,
                      style: GoogleFonts.cinzel(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF2C1A11),
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const Divider(color: Color(0xFFD4AF37)),
              const SizedBox(height: 8),

              _detailRow('Phone Number', widget.visitor.phoneNumber),
              _detailRow('Village / City', widget.visitor.village),
              _detailRow('Purpose', widget.visitor.purpose),
              _detailRow('Members', '${widget.visitor.personsCount} person(s)'),
              _detailRow('Date', widget.visitor.visitorDate),
              _detailRow('Time In', widget.visitor.timeIn),
              if (widget.visitor.timeOut != null && widget.visitor.timeOut!.isNotEmpty)
                _detailRow('Time Out', widget.visitor.timeOut!),
              if (widget.visitor.visitDuration != null && widget.visitor.visitDuration!.isNotEmpty)
                _detailRow('Duration', widget.visitor.visitDuration!),

              _detailRow('Status', isCheckedIn ? 'INSIDE TEMPLE' : 'VISITOR LEFT', isBadge: true, isCheckedIn: isCheckedIn),

              if (widget.visitor.notes != null && widget.visitor.notes!.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Text('Notes:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                Text(widget.visitor.notes!, style: const TextStyle(fontStyle: FontStyle.italic, fontSize: 13)),
              ],

              const SizedBox(height: 16),
              const Text('Communication History Audit Trail', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFFD4AF37))),
              const SizedBox(height: 6),

              if (_isLoadingHistory)
                const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
              else if (_commHistory.isEmpty)
                const Text('No automated communications recorded.', style: TextStyle(fontSize: 12, color: Colors.grey))
              else
                Column(
                  children: _commHistory.map((h) => _historyCard(h)).toList(),
                ),

              const SizedBox(height: 20),

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF2C1A11),
                        side: const BorderSide(color: Color(0xFFD4AF37)),
                      ),
                      icon: const Icon(Icons.person, size: 18),
                      label: const Text('View Profile'),
                      onPressed: () async {
                        final person = await _repository.getPersonByPhone(widget.visitor.phoneNumber);
                        if (person != null && context.mounted) {
                          Navigator.pop(context);
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => VisitorProfileScreen(personId: person.personId),
                            ),
                          );
                        }
                      },
                    ),
                  ),
                  if (isCheckedIn) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange.shade800,
                          foregroundColor: Colors.white,
                        ),
                        icon: const Icon(Icons.logout, size: 18),
                        label: const Text('VISITOR LEFT', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                        onPressed: () {
                          showDialog(
                            context: context,
                            builder: (_) => VisitorLeftConfirmationDialog(
                              visitorName: widget.visitor.name,
                              timeIn: widget.visitor.timeIn,
                              onConfirm: () async {
                                await _repository.checkOutVisitor(widget.visitor.id);
                                if (context.mounted) {
                                  Navigator.pop(context);
                                  widget.onCheckOut();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('${widget.visitor.name} marked as Visitor Left'),
                                      backgroundColor: Colors.orange,
                                    ),
                                  );
                                }
                              },
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _detailRow(String title, String value, {bool isBadge = false, bool isCheckedIn = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: const TextStyle(fontSize: 13, color: Colors.grey, fontWeight: FontWeight.w500)),
          isBadge
              ? Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: isCheckedIn ? Colors.green.shade100 : Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    value,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isCheckedIn ? Colors.green.shade800 : Colors.black87,
                    ),
                  ),
                )
              : Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _historyCard(CommunicationHistory h) {
    final isSent = h.status == 'SENT';

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${h.channel} • ${h.templateType}',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFFD4AF37)),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isSent ? Colors.green.shade100 : Colors.red.shade100,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  h.status,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: isSent ? Colors.green.shade800 : Colors.red.shade800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            h.renderedMessage,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 11, color: Colors.black87),
          ),
        ],
      ),
    );
  }
}
