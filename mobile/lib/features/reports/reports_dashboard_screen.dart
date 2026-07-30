import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/core/services/export_service.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';

class ReportsDashboardScreen extends StatefulWidget {
  const ReportsDashboardScreen({super.key});

  @override
  State<ReportsDashboardScreen> createState() => _ReportsDashboardScreenState();
}

class _ReportsDashboardScreenState extends State<ReportsDashboardScreen> {
  String _selectedTab = 'TODAY'; // 'TODAY', 'WEEKLY', 'MONTHLY', 'CUSTOM'

  DateTime _startDate = DateTime.now();
  DateTime _endDate = DateTime.now();

  String _selectedStatus = 'ALL'; // 'ALL', 'CHECKED_IN', 'CHECKED_OUT'
  String _villageFilter = '';
  String _purposeFilter = 'ALL';
  String _sortBy = 'TIME_IN'; // 'TIME_IN', 'NAME', 'VILLAGE'

  List<VisitorModel> _allPeriodVisitors = [];
  List<VisitorModel> _filteredVisitors = [];
  Map<String, dynamic> _summary = {};

  bool _isLoading = true;

  final List<String> _purposes = ['ALL', 'General Darshan', 'Special Seva', 'Voluntary Work', 'Annadanam', 'Donation / Prasadam'];

  @override
  void initState() {
    super.initState();
    _loadReportData();
  }

  Future<void> _loadReportData() async {
    setState(() => _isLoading = true);

    final now = DateTime.now();
    DateTime start = DateTime(now.year, now.month, now.day);
    DateTime end = DateTime(now.year, now.month, now.day, 23, 59, 59);

    if (_selectedTab == 'WEEKLY') {
      start = now.subtract(const Duration(days: 7));
    } else if (_selectedTab == 'MONTHLY') {
      start = DateTime(now.year, now.month, 1);
    } else if (_selectedTab == 'CUSTOM') {
      start = DateTime(_startDate.year, _startDate.month, _startDate.day);
      end = DateTime(_endDate.year, _endDate.month, _endDate.day, 23, 59, 59);
    }

    final db = await SQLiteDatabase.instance;
    final results = await db.query(
      'visitors',
      where: 'is_deleted = 0',
      orderBy: 'created_at DESC',
    );

    final list = results.map((r) => VisitorModel.fromJson(r)).where((v) {
      try {
        final dateParts = v.visitorDate.split('-');
        final dt = DateTime(int.parse(dateParts[0]), int.parse(dateParts[1]), int.parse(dateParts[2]));
        return dt.isAfter(start.subtract(const Duration(days: 1))) && dt.isBefore(end.add(const Duration(days: 1)));
      } catch (_) {
        return true;
      }
    }).toList();

    _allPeriodVisitors = list;
    _applyFiltersAndSort();
  }

  void _applyFiltersAndSort() {
    List<VisitorModel> filtered = List.from(_allPeriodVisitors);

    // Status Filter
    if (_selectedStatus != 'ALL') {
      filtered = filtered.where((v) => v.status == _selectedStatus).toList();
    }

    // Village Filter
    if (_villageFilter.isNotEmpty) {
      filtered = filtered.where((v) => v.village.toLowerCase().contains(_villageFilter.toLowerCase())).toList();
    }

    // Purpose Filter
    if (_purposeFilter != 'ALL') {
      filtered = filtered.where((v) => v.purpose == _purposeFilter).toList();
    }

    // Sorting
    if (_sortBy == 'NAME') {
      filtered.sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
    } else if (_sortBy == 'VILLAGE') {
      filtered.sort((a, b) => a.village.toLowerCase().compareTo(b.village.toLowerCase()));
    } else {
      filtered.sort((a, b) => b.timeIn.compareTo(a.timeIn));
    }

    // Compute Summary Statistics
    final totalCount = filtered.length;
    final totalMembers = filtered.fold<int>(0, (sum, v) => sum + v.personsCount);
    final insideCount = filtered.where((v) => v.status == 'CHECKED_IN').fold<int>(0, (sum, v) => sum + v.personsCount);
    final leftCount = filtered.where((v) => v.status == 'CHECKED_OUT').fold<int>(0, (sum, v) => sum + v.personsCount);

    // Purpose & Village frequency maps
    final purposeMap = <String, int>{};
    final villageMap = <String, int>{};

    for (var v in filtered) {
      purposeMap[v.purpose] = (purposeMap[v.purpose] ?? 0) + 1;
      villageMap[v.village] = (villageMap[v.village] ?? 0) + 1;
    }

    String topPurpose = purposeMap.isNotEmpty ? (purposeMap.entries.toList()..sort((a, b) => b.value.compareTo(a.value))).first.key : 'N/A';
    String topVillage = villageMap.isNotEmpty ? (villageMap.entries.toList()..sort((a, b) => b.value.compareTo(a.value))).first.key : 'N/A';

    // Avg Duration
    final checkedOutVisitors = filtered.where((v) => v.status == 'CHECKED_OUT' && v.visitDuration != null).toList();
    String avgDurationStr = '0 min';
    if (checkedOutVisitors.isNotEmpty) {
      int totalMinutes = 0;
      int count = 0;
      for (var v in checkedOutVisitors) {
        if (v.visitDuration!.contains('min')) {
          try {
            final parts = v.visitDuration!.split(' ');
            if (parts.contains('hr')) {
              final h = int.parse(parts[0]);
              final m = int.parse(parts[2]);
              totalMinutes += (h * 60) + m;
            } else {
              final m = int.parse(parts[0]);
              totalMinutes += m;
            }
            count++;
          } catch (_) {}
        }
      }
      if (count > 0) {
        final avgMins = (totalMinutes / count).round();
        avgDurationStr = VisitorRepository.formatDuration(Duration(minutes: avgMins));
      }
    }

    setState(() {
      _filteredVisitors = filtered;
      _summary = {
        'total_visitors': totalCount,
        'total_members': totalMembers,
        'visitors_inside': insideCount,
        'visitors_left': leftCount,
        'top_purpose': topPurpose,
        'top_village': topVillage,
        'avg_duration_str': avgDurationStr,
      };
      _isLoading = false;
    });
  }

  Future<void> _exportExcel() async {
    final file = await ExportService.exportToExcel(
      visitors: _filteredVisitors,
      summary: _summary,
      periodName: _selectedTab,
    );

    if (file != null) {
      await Share.shareXFiles([XFile(file.path)], text: 'Temple Visitor Excel Audit Report');
    }
  }

  Future<void> _exportPDF() async {
    final file = await ExportService.exportToPDF(
      visitors: _filteredVisitors,
      summary: _summary,
      periodName: _selectedTab,
    );

    if (file != null) {
      await Share.shareXFiles([XFile(file.path)], text: 'Temple Visitor Printable PDF Report');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Reports & Audit Dashboard', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF2C1A11),
        actions: [
          IconButton(icon: const Icon(Icons.table_view, color: Color(0xFFD4AF37)), onPressed: _exportExcel, tooltip: 'Export Excel CSV'),
          IconButton(icon: const Icon(Icons.picture_as_pdf, color: Color(0xFFD4AF37)), onPressed: _exportPDF, tooltip: 'Export Printable PDF'),
        ],
      ),
      body: Column(
        children: [
          // Period Tabs
          Container(
            color: const Color(0xFF2C1A11),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Row(
              children: [
                _tabChip('Today', 'TODAY'),
                const SizedBox(width: 6),
                _tabChip('Weekly', 'WEEKLY'),
                const SizedBox(width: 6),
                _tabChip('Monthly', 'MONTHLY'),
                const SizedBox(width: 6),
                _tabChip('Custom', 'CUSTOM'),
              ],
            ),
          ),

          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Summary Cards Grid
                        _summaryGrid(),
                        const SizedBox(height: 14),

                        // Filters Bar
                        _filtersBar(),
                        const SizedBox(height: 14),

                        // Visitor Records Data Table Header
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Visitor Audit Records (${_filteredVisitors.length})',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFFD4AF37)),
                            ),
                            DropdownButton<String>(
                              value: _sortBy,
                              underline: const SizedBox(),
                              items: const [
                                DropdownMenuItem(value: 'TIME_IN', child: Text('Sort by Time In')),
                                DropdownMenuItem(value: 'NAME', child: Text('Sort by Name')),
                                DropdownMenuItem(value: 'VILLAGE', child: Text('Sort by Village')),
                              ],
                              onChanged: (v) {
                                if (v != null) {
                                  setState(() => _sortBy = v);
                                  _applyFiltersAndSort();
                                }
                              },
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),

                        // Records Table
                        _visitorTable(),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _tabChip(String label, String value) {
    final isSelected = _selectedTab == value;
    return ChoiceChip(
      label: Text(label, style: TextStyle(fontSize: 11, color: isSelected ? Colors.black : Colors.white, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal)),
      selected: isSelected,
      selectedColor: const Color(0xFFD4AF37),
      backgroundColor: Colors.white10,
      onSelected: (_) {
        setState(() => _selectedTab = value);
        _loadReportData();
      },
    );
  }

  Widget _summaryGrid() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.shade300),
      ),
      child: Column(
        children: [
          Row(
            children: [
              _metricTile('Total Records', '${_summary['total_visitors']}'),
              _metricTile('Total Members', '${_summary['total_members']}'),
              _metricTile('Avg Duration', '${_summary['avg_duration_str']}'),
            ],
          ),
          const Divider(height: 16),
          Row(
            children: [
              _metricTile('Visitors Inside', '${_summary['visitors_inside']}'),
              _metricTile('Visitors Left', '${_summary['visitors_left']}'),
              _metricTile('Top Purpose', '${_summary['top_purpose']}'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricTile(String title, String val) {
    return Expanded(
      child: Column(
        children: [
          Text(val, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.brown)),
          Text(title, style: const TextStyle(fontSize: 10, color: Colors.black54)),
        ],
      ),
    );
  }

  Widget _filtersBar() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: TextField(
                decoration: const InputDecoration(labelText: 'Filter Village', border: OutlineInputBorder(), isDense: true),
                onChanged: (v) {
                  _villageFilter = v;
                  _applyFiltersAndSort();
                },
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _purposeFilter,
                decoration: const InputDecoration(labelText: 'Filter Purpose', border: OutlineInputBorder(), isDense: true),
                items: _purposes.map((p) => DropdownMenuItem(value: p, child: Text(p, style: const TextStyle(fontSize: 12)))).toList(),
                onChanged: (v) {
                  if (v != null) {
                    _purposeFilter = v;
                    _applyFiltersAndSort();
                  }
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _visitorTable() {
    if (_filteredVisitors.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(24.0),
        child: Center(child: Text('No visitor records matching criteria.')),
      );
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columnSpacing: 16,
        columns: const [
          DataColumn(label: Text('ID', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Name', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Phone', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Village', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Purpose', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Members', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Time In', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Time Out', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Duration', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Status', style: TextStyle(fontWeight: FontWeight.bold))),
        ],
        rows: _filteredVisitors.map((v) {
          final id = v.visitorUuid.length > 8 ? v.visitorUuid.substring(0, 8) : v.visitorUuid;
          return DataRow(cells: [
            DataCell(Text(id)),
            DataCell(Text(v.name, style: const TextStyle(fontWeight: FontWeight.bold))),
            DataCell(Text(v.phoneNumber)),
            DataCell(Text(v.village)),
            DataCell(Text(v.purpose)),
            DataCell(Text('${v.personsCount}')),
            DataCell(Text(v.timeIn)),
            DataCell(Text(v.timeOut?.isNotEmpty == true ? v.timeOut! : 'Inside')),
            DataCell(Text(v.visitDuration?.isNotEmpty == true ? v.visitDuration! : 'In Progress')),
            DataCell(Text(v.status)),
          ]);
        }).toList(),
      ),
    );
  }
}
