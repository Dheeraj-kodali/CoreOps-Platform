import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:temple_visitor_app/core/theme/app_theme.dart';
import 'package:temple_visitor_app/core/localization/app_localizations.dart';
import 'package:temple_visitor_app/core/services/storage_service.dart';
import 'package:temple_visitor_app/features/authentication/auth_provider.dart';
import 'package:temple_visitor_app/features/authentication/login_screen.dart';
import 'package:temple_visitor_app/features/visitors/visitor_registration_screen.dart';
import 'package:temple_visitor_app/features/visitors/visitor_list_screen.dart';
import 'package:temple_visitor_app/features/settings/admin_pin_dialog.dart';
import 'package:temple_visitor_app/features/settings/settings_home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final savedLang = await StorageService.getLanguage();

  runApp(
    ProviderScope(
      overrides: [
        localeProvider.overrideWith((ref) => Locale(savedLang)),
      ],
      child: const TempleVisitorApp(),
    ),
  );
}

final localeProvider = StateProvider<Locale>((ref) => const Locale('en'));

class TempleVisitorApp extends ConsumerWidget {
  const TempleVisitorApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    final authState = ref.watch(authStateProvider);

    return MaterialApp(
      title: 'Sri Kalki Seva Alayam',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      locale: locale,
      supportedLocales: const [
        Locale('en', ''),
        Locale('te', ''),
      ],
      localizationsDelegates: const [
        AppLocalizationsDelegate(),
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      home: authState.when(
        data: (user) => user == null ? const LoginScreen() : const MainNavigationShell(),
        loading: () => const Scaffold(
          body: Center(child: CircularProgressIndicator(color: Color(0xFFD4AF37))),
        ),
        error: (_, __) => const LoginScreen(),
      ),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;
  final GlobalKey<VisitorListScreenState> _listKey = GlobalKey<VisitorListScreenState>();

  void _openSettingsProtected() {
    showDialog(
      context: context,
      builder: (_) => AdminPinDialog(
        onUnlocked: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const SettingsHomeScreen()),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '🛕 Sri Kalki Seva Alayam',
          style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFD4AF37)),
        ),
        backgroundColor: const Color(0xFF2C1A11),
        elevation: 2,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFFD4AF37)),
            onPressed: () {
              _listKey.currentState?.loadTodayVisitors();
            },
            tooltip: 'Refresh Today List',
          ),
          IconButton(
            icon: const Icon(Icons.settings, color: Color(0xFFD4AF37)),
            onPressed: _openSettingsProtected,
            tooltip: 'Admin Settings',
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          VisitorRegistrationScreen(
            onVisitorAdded: () {
              _listKey.currentState?.loadTodayVisitors();
              setState(() => _currentIndex = 1); // Auto switch to Today's Visitor List tab
            },
          ),
          VisitorListScreen(key: _listKey),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: const Color(0xFFD4AF37),
        unselectedItemColor: Colors.grey[400],
        backgroundColor: const Color(0xFF2C1A11),
        type: BottomNavigationBarType.fixed,
        selectedFontSize: 14,
        unselectedFontSize: 12,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.login, size: 28),
            label: 'Visitor Entered',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.groups, size: 28),
            label: "Today's Visitors",
          ),
        ],
      ),
    );
  }
}
