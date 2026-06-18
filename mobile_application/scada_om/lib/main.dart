import 'package:flutter/material.dart';
import 'screens/login.dart';
import 'theme/theme.dart';

void main() {
  runApp(const ScadaMobileApp());
}

class ScadaMobileApp extends StatelessWidget {
  const ScadaMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SCADA O&M',
      debugShowCheckedModeBanner: false,

      theme: ThemeData(
        scaffoldBackgroundColor: ScadaColors.background,
        colorScheme: const ColorScheme.dark(
          primary: ScadaColors.primary,
          surface: ScadaColors.surface,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: ScadaColors.primary,
            foregroundColor: Colors.white,
            minimumSize: const Size(double.infinity, 50), // Wide buttons
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),
      
      home: const LoginScreen(),
    );
  }
}