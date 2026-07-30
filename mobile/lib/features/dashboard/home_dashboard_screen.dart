import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/widgets/shared/stat_card.dart';
import 'package:temple_visitor_app/widgets/shared/temple_app_bar.dart';

class HomeDashboardScreen extends ConsumerWidget {
  final Function(int) onNavigateTab;

  const HomeDashboardScreen({Key? key, required this.onNavigateTab}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final loc = AppLocalizations.of(context);

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
                StatCard(title: loc.todayVisitors, value: '245', icon: Icons.today),
                StatCard(title: loc.monthlyVisitors, value: '7,450', icon: Icons.calendar_month),
                StatCard(title: loc.yearlyVisitors, value: '89,200', icon: Icons.insights),
                StatCard(title: loc.totalVisitors, value: '1,45,000', icon: Icons.groups),
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
