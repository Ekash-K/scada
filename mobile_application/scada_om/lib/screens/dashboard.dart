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
      ),
      
      // The Sidebar
      drawer: Drawer(
        backgroundColor: const Color(0xFF1e293b),
        child: Column(
          children: [
            // The Header
            const UserAccountsDrawerHeader(
              decoration: BoxDecoration(color: Color(0xFF0f172a)),
              accountName: Text("Field Engineer"),
              accountEmail: Text("System Online"),
              currentAccountPicture: CircleAvatar(
                backgroundColor: Color(0xFF0a66c2),
                child: Icon(Icons.person, color: Colors.white, size: 40),
              ),
            ),
            
            // The Top Options
            ListTile(
              leading: const Icon(Icons.analytics, color: Colors.white),
              title: const Text('Panel Option A', style: TextStyle(color: Colors.white)),
              onTap: () { /* TODO: Navigate to A */ },
            ),
            ListTile(
              leading: const Icon(Icons.speed, color: Colors.white),
              title: const Text('Panel Option B', style: TextStyle(color: Colors.white)),
              onTap: () { /* TODO: Navigate to B */ },
            ),
            ListTile(
              leading: const Icon(Icons.memory, color: Colors.white),
              title: const Text('Panel Option C', style: TextStyle(color: Colors.white)),
              onTap: () { /* TODO: Navigate to C */ },
            ),
            ListTile(
              leading: const Icon(Icons.settings_input_component, color: Colors.white),
              title: const Text('Panel Option D', style: TextStyle(color: Colors.white)),
              onTap: () { /* TODO: Navigate to D */ },
            ),
            
            // The Spacer pushes everything below it to the absolute bottom
            const Spacer(),
            const Divider(color: Colors.grey),
            
            // The Bottom Options
            ListTile(
              leading: const Icon(Icons.account_circle, color: Colors.white),
              title: const Text('Profile', style: TextStyle(color: Colors.white)),
              onTap: () { /* TODO: Navigate to Profile */ },
            ),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.redAccent),
              title: const Text('Terminate Session', style: TextStyle(color: Colors.redAccent)),
              onTap: () => _logout(context),
            ),
            const SizedBox(height: 20), // Just a little padding at the very bottom
          ],
        ),
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