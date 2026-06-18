import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'login.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  // A quick function to destroy the token and kick the user out
  Future<void> _logout(BuildContext context) async {
    const storage = FlutterSecureStorage();
    await storage.delete(key: 'auth_token');
    
    // Check if the widget is still mounted before navigating
    if (!context.mounted) return;
    
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SCADA Command Center', style: TextStyle(letterSpacing: 1.5)),
        backgroundColor: const Color(0xFF0f172a),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.logout, 
              color: Colors.redAccent, // A nice alert color for logging out
            ),
            tooltip: 'Logout', // Shows text if they long-press the button
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      
      // The Empty Dashboard Body
      body: const Center(
        child: Text(
          'AWAITING TELEMETRY DATA...',
          style: TextStyle(color: Colors.grey, letterSpacing: 2),
        ),
      ),
    );
  }
}