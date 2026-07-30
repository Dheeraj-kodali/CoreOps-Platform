import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const _localizedValues = <String, Map<String, String>>{
    'en': {
      'app_title': 'Sri Kalki Seva Alayam',
      'dashboard': 'Live Dashboard',
      'visitor_registration': 'Visitor Registration',
      'visitor_list': 'Visitor Registry',
      'search': 'Search & Filter',
      'reports': 'Reports & Export',
      'settings': 'System Settings',
      'offline_sync': 'Offline Sync Engine',
      'login': 'Volunteer Login',
      'logout': 'Sign Out',
      'username': 'Username or Email',
      'password': 'Password',
      'login_btn': 'Authenticate & Sign In',
      'today_visitors': "Today's Visitors",
      'monthly_visitors': 'Monthly Total',
      'yearly_visitors': 'Yearly Total',
      'total_visitors': 'All Time Visitors',
      'quick_actions': 'Quick Actions',
      'new_visitor': 'New Visitor',
      'sync_status': 'Sync Status',
      'name': 'Visitor Full Name',
      'phone': 'Phone Number (+91)',
      'gender': 'Gender',
      'age': 'Age (Years)',
      'persons': 'Persons Count',
      'purpose': 'Purpose of Visit',
      'village': 'Village / Town Name',
      'service': 'Temple Service / Seva',
      'notes': 'Additional Notes / Remarks',
      'submit': 'Save & Register Visitor',
      'checking_duplicate': 'Checking duplicate records...',
      'duplicate_found': 'Duplicate visitor entry detected for today!',
      'sync_pending': 'Pending Offline Sync',
      'synced': 'Synced to Central Server',
      'manual_sync': 'Sync Pending Records Now',
      'language': 'Language / భాష',
      'select_language': 'Select App Language',
      'english': 'English',
      'telugu': 'తెలుగు',
    },
    'te': {
      'app_title': 'శ్రీ కల్కి సేవా ఆలయం',
      'dashboard': 'లైవ్ డాష్‌బోర్డ్',
      'visitor_registration': 'సందర్శకుల నమోదు',
      'visitor_list': 'సందర్శకుల రిజిస్టరు',
      'search': 'శోధన & ఫిల్టర్లు',
      'reports': 'నివేదికలు & ఎగుమతి',
      'settings': 'సిస్టమ్ సెట్టింగులు',
      'offline_sync': 'ఆఫ్‌లైన్ సింక్ ఇంజిన్',
      'login': 'వాలంటీర్ లాగిన్',
      'logout': 'సైన్ అవుట్',
      'username': 'యూజర్ పేరు లేదా ఈమెయిల్',
      'password': 'పాస్‌వర్డ్',
      'login_btn': 'ప్రవేశించండి',
      'today_visitors': 'నేటి సందర్శకులు',
      'monthly_visitors': 'ఈ నెల మొత్తం',
      'yearly_visitors': 'ఈ సంవత్సరం మొత్తం',
      'total_visitors': 'మొత్తం సందర్శకులు',
      'quick_actions': 'త్వరిత చర్యలు',
      'new_visitor': 'కొత్త సందర్శకుడు',
      'sync_status': 'సింక్ స్థితి',
      'name': 'సందర్శకుని పూర్తి పేరు',
      'phone': 'ఫోన్ నంబరు (+91)',
      'gender': 'లింగం',
      'age': 'వయస్సు (సంవత్సరాలు)',
      'persons': 'మంది సంఖ్య',
      'purpose': 'సందర్శన ఉద్దేశ్యం',
      'village': 'గ్రామం / పట్టణం పేరు',
      'service': 'దేవాలయ సేవ',
      'notes': 'అదనపు వివరాలు / గమనికలు',
      'submit': 'నమోదు చేయండి',
      'checking_duplicate': 'డూప్లికేట్ రికార్డులను పరిశీలిస్తోంది...',
      'duplicate_found': 'ఈ రోజుకి ఇప్పటికే ఈ నమోదు ఉంది!',
      'sync_pending': 'ఆఫ్‌లైన్‌లో వేచి ఉంది',
      'synced': 'సర్వర్‌కి సింక్ అయ్యింది',
      'manual_sync': 'ఇప్పుడే సింక్ చేయండి',
      'language': 'భాష / Language',
      'select_language': 'యాప్ భాషను ఎంచుకోండి',
      'english': 'English',
      'telugu': 'తెలుగు',
    },
  };

  String get appTitle => _localizedValues[locale.languageCode]!['app_title']!;
  String get dashboard => _localizedValues[locale.languageCode]!['dashboard']!;
  String get visitorRegistration => _localizedValues[locale.languageCode]!['visitor_registration']!;
  String get visitorList => _localizedValues[locale.languageCode]!['visitor_list']!;
  String get search => _localizedValues[locale.languageCode]!['search']!;
  String get reports => _localizedValues[locale.languageCode]!['reports']!;
  String get settings => _localizedValues[locale.languageCode]!['settings']!;
  String get offlineSync => _localizedValues[locale.languageCode]!['offline_sync']!;
  String get login => _localizedValues[locale.languageCode]!['login']!;
  String get logout => _localizedValues[locale.languageCode]!['logout']!;
  String get username => _localizedValues[locale.languageCode]!['username']!;
  String get password => _localizedValues[locale.languageCode]!['password']!;
  String get loginBtn => _localizedValues[locale.languageCode]!['login_btn']!;
  String get todayVisitors => _localizedValues[locale.languageCode]!['today_visitors']!;
  String get monthlyVisitors => _localizedValues[locale.languageCode]!['monthly_visitors']!;
  String get yearlyVisitors => _localizedValues[locale.languageCode]!['yearly_visitors']!;
  String get totalVisitors => _localizedValues[locale.languageCode]!['total_visitors']!;
  String get quickActions => _localizedValues[locale.languageCode]!['quick_actions']!;
  String get newVisitor => _localizedValues[locale.languageCode]!['new_visitor']!;
  String get syncStatus => _localizedValues[locale.languageCode]!['sync_status']!;
  String get name => _localizedValues[locale.languageCode]!['name']!;
  String get phone => _localizedValues[locale.languageCode]!['phone']!;
  String get gender => _localizedValues[locale.languageCode]!['gender']!;
  String get age => _localizedValues[locale.languageCode]!['age']!;
  String get persons => _localizedValues[locale.languageCode]!['persons']!;
  String get purpose => _localizedValues[locale.languageCode]!['purpose']!;
  String get village => _localizedValues[locale.languageCode]!['village']!;
  String get service => _localizedValues[locale.languageCode]!['service']!;
  String get notes => _localizedValues[locale.languageCode]!['notes']!;
  String get submit => _localizedValues[locale.languageCode]!['submit']!;
  String get checkingDuplicate => _localizedValues[locale.languageCode]!['checking_duplicate']!;
  String get duplicateFound => _localizedValues[locale.languageCode]!['duplicate_found']!;
  String get syncPending => _localizedValues[locale.languageCode]!['sync_pending']!;
  String get synced => _localizedValues[locale.languageCode]!['synced']!;
  String get manualSync => _localizedValues[locale.languageCode]!['manual_sync']!;
  String get language => _localizedValues[locale.languageCode]!['language']!;
  String get selectLanguage => _localizedValues[locale.languageCode]!['select_language']!;
  String get english => _localizedValues[locale.languageCode]!['english']!;
  String get telugu => _localizedValues[locale.languageCode]!['telugu']!;
}

class AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['en', 'te'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(AppLocalizations(locale));
  }

  @override
  bool shouldReload(AppLocalizationsDelegate old) => false;
}
