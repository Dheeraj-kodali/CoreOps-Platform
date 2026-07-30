import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/widgets/shared/sync_badge.dart';
import 'package:temple_visitor_app/widgets/shared/temple_app_bar.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({Key? key}) : super(key: key);

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  List<VisitorModel> _results = [];
  bool _hasSearched = false;

  Future<void> _performSearch() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;

    final rows = await SQLiteDatabase.getVisitors(searchQuery: query);
    setState(() {
      _results = rows.map((r) => VisitorModel.fromJson(r)).toList();
      _hasSearched = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const TempleAppBar(title: 'Search Visitor Registry'),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      hintText: 'Search by Name, Phone, Village, Purpose...',
                      prefixIcon: Icon(Icons.search, color: Color(0xFFD4AF37)),
                    ),
                    onSubmitted: (_) => _performSearch(),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _performSearch,
                  child: const Text('Search'),
                ),
              ],
            ),
            const SizedBox(height: 20),

            Expanded(
              child: !_hasSearched
                  ? Center(
                      child: Text(
                        'Enter query above to search local visitor registry.',
                        style: GoogleFonts.inter(color: Colors.grey[600]),
                      ),
                    )
                  : _results.isEmpty
                      ? Center(
                          child: Text(
                            'No matching records found.',
                            style: GoogleFonts.inter(color: Colors.grey[600]),
                          ),
                        )
                      : ListView.builder(
                          itemCount: _results.length,
                          itemBuilder: (context, idx) {
                            final v = _results[idx];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 10),
                              child: ListTile(
                                title: Text(v.name, style: GoogleFonts.inter(fontWeight: FontWeight.bold)),
                                subtitle: Text('Phone: ${v.phoneNumber} | Date: ${v.visitorDate}'),
                                trailing: SyncBadge(status: v.syncStatus),
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}
