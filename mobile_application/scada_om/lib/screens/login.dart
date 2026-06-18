import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dashboard.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // 1. Controllers to read the text typed into the boxes
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  
  // 2. State variables for UI feedback
  bool _isLoading = false;
  String _errorMessage = '';
  
  // 3. The Secure Storage instance
  final storage = const FlutterSecureStorage();

  // 4. The core API linking function
  // 4. The core API linking function
  Future<void> _loginToDjango() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final host = kIsWeb
          ? '127.0.0.1'
          : defaultTargetPlatform == TargetPlatform.android
              ? '10.0.2.2'
              : '127.0.0.1';
      final url = Uri.parse('http://$host:8000/api/mobile-login/');
      print('Login URL: $url');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': _emailController.text.trim(),
          'password': _passwordController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        // Success! Extract the JSON token.
        final data = jsonDecode(response.body);
        final token = data['token'];

        // Save it securely into the phone's hardware
        await storage.write(key: 'auth_token', value: token);
        
        print("SCADA LINK ESTABLISHED. TOKEN: $token");
        
        // CHECK IF MOUNTED BEFORE NAVIGATING (Flutter safety rule)
        if (!context.mounted) return;

        // DESTROY LOGIN SCREEN AND LAUNCH DASHBOARD
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const DashboardScreen()),
        );
      }
      else {
        print("DJANGO REJECTION: ${response.statusCode} - ${response.body}");
        setState(() {
          _errorMessage = 'Invalid credentials or server rejected access.';
        });
      }
    } catch (e) {
      print('Login request failed: $e');
      setState(() {
        _errorMessage = 'Connection Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // We removed the AppBar for a cleaner, full-screen modern look
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 20),
              const Text(
                'SCADA O&M',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 50),

              // Email Field
              TextField(
                controller: _emailController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Email Address',
                  labelStyle: const TextStyle(color: Colors.grey),
                  filled: true,
                  fillColor: const Color(0xFF1e293b),
                  prefixIcon: const Icon(Icons.email, color: Colors.grey),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide.none,
                  ),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 20),

              // Password Field
              TextField(
                controller: _passwordController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Password',
                  labelStyle: const TextStyle(color: Colors.grey),
                  filled: true,
                  fillColor: const Color(0xFF1e293b),
                  prefixIcon: const Icon(Icons.lock, color: Colors.grey),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide.none,
                  ),
                ),
                obscureText: true,
              ),
              const SizedBox(height: 20),
              
              if (_errorMessage.isNotEmpty) 
                Text(_errorMessage, style: const TextStyle(color: Colors.redAccent)),
                
              const SizedBox(height: 20),
              
              // Authenticate Button
              _isLoading 
                  ? const CircularProgressIndicator(color: Color(0xFF0a66c2))
                  : ElevatedButton(
                      onPressed: _loginToDjango,
                      child: const Text('AUTHENTICATE', style: TextStyle(letterSpacing: 1.5, fontWeight: FontWeight.bold)),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}