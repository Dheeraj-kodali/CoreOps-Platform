import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color templeGold = Color(0xFFD4AF37);
  static const Color templeGoldLight = Color(0xFFF3E5AB);
  static const Color templeGoldDark = Color(0xFF997A15);
  static const Color templeBrown = Color(0xFF2C1A11);
  static const Color templeBrownLight = Color(0xFF3E2723);
  static const Color templeIvory = Color(0xFFFAF8F5);
  static const Color templeCrimson = Color(0xFF900C3F);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: templeGold,
        primary: templeBrown,
        secondary: templeGold,
        surface: templeIvory,
        background: templeIvory,
      ),
      scaffoldBackgroundColor: templeIvory,
      appBarTheme: AppBarTheme(
        backgroundColor: templeBrown,
        foregroundColor: templeGold,
        elevation: 4,
        centerTitle: true,
        titleTextStyle: GoogleFonts.cinzel(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: templeGold,
          letterSpacing: 1.0,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: templeGold,
          foregroundColor: templeBrown,
          textStyle: GoogleFonts.inter(
            fontWeight: FontWeight.bold,
            fontSize: 15,
          ),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: templeGold),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: templeGold.withOpacity(0.4)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: templeGold, width: 2),
        ),
        labelStyle: GoogleFonts.inter(color: templeBrown),
      ),
    );
  }
}
