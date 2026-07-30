import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/core/database/sqlite_helper.dart';

class VisitorListScreen extends StatefulWidget {
  const VisitorListScreen({Key? key}) : super(key: key);

  @override
  State<VisitorListScreen> createState() => _VisitorListScreenState();
}

class _VisitorListScreenState extends State<VisitorListScreen> {
  List<Map<String, dynamic>> _visitors = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadVisitors();
  }

  Future<void> _loadVisitors() async {
    setState(() => _isLoading = true);
    final data = await SQLiteHelper.getVisitors();
    setState(() {
      _visitors = data;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.visitorList),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadVisitors,
          )
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37)))
          : _visitors.isEmpty
              ? Center(
                  child: Text(
                    'No visitor records logged locally.',
                    style: GoogleFonts.inter(color: Colors.grey[600]),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _visitors.length,
                  itemBuilder: (context, index) {
                    final v = _visitors[index];
                    final isSynced = v['sync_status'] == 'SYNCED';

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: BorderSide(color: const Color(0xFFD4AF37).withOpacity(0.3)),
                      ),
                      child: ListTile(
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        title: Text(
                          v['name'] ?? '',
                          style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFF2C1A11)),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 4),
                            Text('Phone: ${v['phone_number']} | Persons: ${v['persons_count']}'),
                            Text('Date: ${v['visitor_date']} ${v['visitor_time']}'),
                          ],
                        ),
                        trailing: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: isSynced ? Colors.green[100] : Colors.amber[100],
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: isSynced ? Colors.green : const Color(0xFFD4AF37),
                            ),
                          ),
                          child: Text(
                            isSynced ? 'SYNCED' : 'PENDING',
                            style: GoogleFonts.inter(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: isSynced ? Colors.green[900] : const Color(0xFF3E2723),
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
