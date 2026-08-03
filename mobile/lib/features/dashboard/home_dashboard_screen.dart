import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/core/repositories/visitor_repository.dart';
import 'package:temple_visitor_app/core/services/websocket_service.dart';
import 'package:temple_visitor_app/widgets/shared/stat_card.dart';
import 'package:temple_visitor_app/widgets/shared/temple_app_bar.dart';

class HomeDashboardScreen extends ConsumerStatefulWidget {
  final Function(int) onNavigateTab;

  const HomeDashboardScreen({Key? key, required this.onNavigateTab}) : super(key: key);

  @override
  ConsumerState<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends ConsumerState<HomeDashboardScreen> {
  final VisitorRepository _repository = VisitorRepository();
  StreamSubscription? _wsSubscription;
  Map<String, dynamic> _stats = {
    'total_visitors': 0,
    'visitors_inside': 0,
    'total_records': 0,
    'visitors_left': 0,
  };

  @override
  void initState() {
    super.initState();
    _loadLiveStats();
    _wsSubscription = WebSocketService().onEvent.listen((_) {
      _loadLiveStats();
    });
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    super.dispose();
  }

  Future<void> _loadLiveStats() async {
    try {
      final s = await _repository.getTodayStatistics();
      if (mounted) {
        setState(() {
          _stats = s;
        });
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);

    final todayVisitorsVal = '${_stats['total_visitors'] ?? 0}';
    final visitorsInsideVal = '${_stats['visitors_inside'] ?? 0}';
    final checkInsVal = '${_stats['total_records'] ?? 0}';
    final checkOutsVal = '${_stats['visitors_left'] ?? 0}';

    return Scaffold(
      appBar: TempleAppBar(title: loc.dashboard),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF2C1A11), Color(0xFF3E2723)],
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFD4AF37).withOpacity(0.4)),
                boxShadow: const [
                  BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 4)),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome Volunteer',
                    style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFFD4AF37)),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    loc.appTitle,
                    style: GoogleFonts.cinzel(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Stat Cards Grid
            GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.6,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                StatCard(title: loc.todayVisitors, value: todayVisitorsVal, icon: Icons.today),
                StatCard(title: 'Visitors Inside', value: visitorsInsideVal, icon: Icons.person_pin_circle),
                StatCard(title: 'Check-ins', value: checkInsVal, icon: Icons.trending_up),
                StatCard(title: 'Check-outs', value: checkOutsVal, icon: Icons.logout),
              ],
            ),
            const SizedBox(height: 24),

            // Quick Actions Title
            Text(
              loc.quickActions,
              style: GoogleFonts.cinzel(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF2C1A11),
              ),
            ),
            const SizedBox(height: 12),

            // Quick Action Buttons Grid
            GridView.count(
              crossAxisCount: 3,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildQuickActionButton(
                  icon: Icons.person_add,
                  label: loc.newVisitor,
                  onTap: () => onNavigateTab(1),
                ),
                _buildQuickActionButton(
                  icon: Icons.list_alt,
                  label: loc.visitorList,
                  onTap: () => onNavigateTab(2),
                ),
                _buildQuickActionButton(
                  icon: Icons.search,
                  label: loc.search,
                  onTap: () => onNavigateTab(3),
                ),
                _buildQuickActionButton(
                  icon: Icons.cloud_sync,
                  label: loc.syncStatus,
                  onTap: () => onNavigateTab(4),
                ),
                _buildQuickActionButton(
                  icon: Icons.file_present,
                  label: loc.reports,
                  onTap: () => onNavigateTab(5),
                ),
                _buildQuickActionButton(
                  icon: Icons.settings,
                  label: loc.settings,
                  onTap: () => onNavigateTab(6),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFD4AF37).withOpacity(0.3)),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFFD4AF37).withOpacity(0.08),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: const Color(0xFFD4AF37), size: 26),
            const SizedBox(height: 6),
            Text(
              label,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF2C1A11),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
