import 'dart:async';
import 'package:flutter/material.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/services/central_sync_manager.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/features/visitors/visitor_detail_dialog.dart';
import 'package:temple_visitor_app/features/visitors/visitor_left_confirmation_dialog.dart';

class VisitorListScreen extends StatefulWidget {
  const VisitorListScreen({super.key});

  @override
  State<VisitorListScreen> createState() => VisitorListScreenState();
}

class VisitorListScreenState extends State<VisitorListScreen> {
  final _repository = VisitorRepository();
  final _searchController = TextEditingController();
  StreamSubscription? _syncSubscription;

  List<VisitorModel> _visitors = [];
  Map<String, dynamic> _stats = {
    'total_visitors': 0,
    'visitors_inside': 0,
    'visitors_left': 0,
    'avg_duration_str': '0 min',
  };

  String _currentFilter = 'ALL'; // 'ALL', 'INSIDE', 'COMPLETED'
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    loadTodayVisitors();
    _syncSubscription = CentralSyncManager.instance.onSyncCompleted.listen((_) {
      loadTodayVisitors(silent: true);
    });
  }

  @override
  void dispose() {
    _syncSubscription?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> loadTodayVisitors({bool silent = false}) async {
    if (!silent && _visitors.isEmpty) {
      setState(() => _isLoading = true);
    }
    try {
      if (!silent) {
        await _repository.syncRemoteLedgerSessions();
      }
      final list = await _repository.getTodayVisitors(
        search: _searchController.text.trim(),
        statusFilter: _currentFilter,
      );
      final statsMap = await _repository.getTodayStatistics();

      if (mounted) {
        setState(() {
          _visitors = list;
          _stats = statsMap;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _triggerVisitorLeft(VisitorModel v) {
    showDialog(
      context: context,
      builder: (_) => VisitorLeftConfirmationDialog(
        visitorName: v.name,
        timeIn: v.timeIn,
        onConfirm: () async {
          await _repository.checkOutVisitor(v.id);
          await loadTodayVisitors();
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('${v.name} marked as Visitor Left'), backgroundColor: Colors.orange),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Top Dashboard Statistics Header Cards
        Container(
          padding: const EdgeInsets.all(12.0),
          color: const Color(0xFF2C1A11),
          child: Column(
            children: [
              Row(
                children: [
                  _statCard('Total Visitors', '${_stats['total_visitors']}', Colors.amber),
                  const SizedBox(width: 8),
                  _statCard('Inside Temple', '${_stats['visitors_inside']}', Colors.green),
                  const SizedBox(width: 8),
                  _statCard('Visitors Left', '${_stats['visitors_left']}', Colors.grey),
                ],
              ),
              const SizedBox(height: 6),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
                decoration: BoxDecoration(
                  color: Colors.black26,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.timer_outlined, size: 16, color: Color(0xFFD4AF37)),
                    const SizedBox(width: 6),
                    Text(
                      'Average Visit Duration: ${_stats['avg_duration_str']}',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Live Search Bar
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 10, 12, 4),
          child: TextField(
            controller: _searchController,
            onChanged: (_) => loadTodayVisitors(),
            decoration: InputDecoration(
              hintText: 'Search by name, phone, or village...',
              prefixIcon: const Icon(Icons.search, color: Color(0xFFD4AF37)),
              suffixIcon: _searchController.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                        loadTodayVisitors();
                      },
                    )
                  : null,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              contentPadding: const EdgeInsets.symmetric(vertical: 10),
              filled: true,
              fillColor: Colors.grey.shade50,
            ),
          ),
        ),

        // Status Filter Chips (All, Inside, Completed)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4),
          child: Row(
            children: [
              _filterChip('All', 'ALL'),
              const SizedBox(width: 8),
              _filterChip('Inside Temple', 'INSIDE'),
              const SizedBox(width: 8),
              _filterChip('Completed', 'COMPLETED'),
            ],
          ),
        ),

        // Visitor List Items
        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _visitors.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: const [
                          Icon(Icons.people_outline, size: 64, color: Colors.grey),
                          SizedBox(height: 12),
                          Text('No visitors matching criteria.', style: TextStyle(fontSize: 16, color: Colors.grey)),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: loadTodayVisitors,
                      child: ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        itemCount: _visitors.length,
                        itemBuilder: (context, index) {
                          final v = _visitors[index];
                          final isInside = v.status == 'CHECKED_IN' || v.status == 'INSIDE';

                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 5),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            elevation: 2,
                            child: ListTile(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                              onTap: () {
                                showDialog(
                                  context: context,
                                  builder: (_) => VisitorDetailDialog(
                                    visitor: v,
                                    onCheckOut: loadTodayVisitors,
                                  ),
                                );
                              },
                              leading: CircleAvatar(
                                radius: 22,
                                backgroundColor: isInside ? Colors.green : Colors.grey,
                                child: Text(
                                  v.name.isNotEmpty ? v.name[0].toUpperCase() : 'V',
                                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                                ),
                              ),
                              title: Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      v.name,
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: isInside ? Colors.green.shade100 : Colors.grey.shade200,
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      v.displayStatus,
                                      style: TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                        color: isInside ? Colors.green.shade800 : Colors.black87,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 3),
                                  Text('${v.phoneNumber}  •  ${v.village}'),
                                  Text(
                                    isInside
                                        ? 'In: ${v.timeIn}  •  ${v.personsCount} Person(s)'
                                        : 'In: ${v.timeIn}  •  Out: ${v.timeOut ?? "N/A"}  •  ${v.formattedDuration}',
                                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                                  ),
                                ],
                              ),
                              trailing: isInside
                                  ? ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.orange,
                                        foregroundColor: Colors.white,
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      ),
                                      onPressed: () => _triggerVisitorLeft(v),
                                      child: const Text('VISITOR LEFT', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                                    )
                                  : const Icon(Icons.check_circle, color: Colors.grey),
                            ),
                          );
                        },
                      ),
                    ),
        ),
      ],
    );
  }

  Widget _statCard(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Column(
          children: [
            Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
            const SizedBox(height: 2),
            Text(label, style: const TextStyle(fontSize: 11, color: Colors.white70)),
          ],
        ),
      ),
    );
  }

  Widget _filterChip(String label, String value) {
    final isSelected = _currentFilter == value;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      selectedColor: const Color(0xFFD4AF37),
      labelStyle: TextStyle(
        color: isSelected ? Colors.black : Colors.grey.shade700,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        fontSize: 12,
      ),
      onSelected: (selected) {
        if (selected) {
          setState(() => _currentFilter = value);
          loadTodayVisitors();
        }
      },
    );
  }
}
