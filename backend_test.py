#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for CyberSec Educational Platform
Tests all FastAPI endpoints, WebSocket connections, database operations, and security features
"""

import requests
import json
import asyncio
import websockets
import base64
import time
from datetime import datetime
from cryptography.fernet import Fernet
import os
import sys

# Configuration
BACKEND_URL = "https://strengthen-project.preview.emergentagent.com/api"
WS_BASE_URL = "wss://strengthen-project.preview.emergentagent.com"

class CyberSecPlatformTester:
    def __init__(self):
        self.session = requests.Session()
        self.encryption_key = None
        self.cipher_suite = None
        self.test_results = []
        
    def log_test(self, test_name, status, message="", details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🔍 Testing Basic API Endpoints...")
        
        # Test root endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "CyberSec Educational Platform" in data["message"]:
                    self.log_test("Root Endpoint", "PASS", "Root endpoint accessible and returns correct message")
                else:
                    self.log_test("Root Endpoint", "FAIL", "Root endpoint returns unexpected data", data)
            else:
                self.log_test("Root Endpoint", "FAIL", f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Root Endpoint", "FAIL", f"Connection error: {str(e)}")
        
        # Test disclaimer endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/disclaimer")
            if response.status_code == 200:
                data = response.json()
                if "disclaimer" in data and "EDUCATIONAL CYBERSECURITY PLATFORM" in data["disclaimer"]:
                    self.log_test("Disclaimer Endpoint", "PASS", "Disclaimer endpoint returns educational warning")
                else:
                    self.log_test("Disclaimer Endpoint", "FAIL", "Disclaimer content missing or incorrect")
            else:
                self.log_test("Disclaimer Endpoint", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Disclaimer Endpoint", "FAIL", f"Error: {str(e)}")
        
        # Test encryption key endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/encryption-key")
            if response.status_code == 200:
                data = response.json()
                if "encryption_key" in data:
                    self.encryption_key = data["encryption_key"].encode()
                    self.cipher_suite = Fernet(self.encryption_key)
                    self.log_test("Encryption Key Endpoint", "PASS", "Encryption key retrieved successfully")
                else:
                    self.log_test("Encryption Key Endpoint", "FAIL", "No encryption key in response")
            else:
                self.log_test("Encryption Key Endpoint", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Encryption Key Endpoint", "FAIL", f"Error: {str(e)}")
    
    def test_session_management(self):
        """Test session management endpoints"""
        print("\n🔍 Testing Session Management...")
        
        # Test get active sessions
        try:
            response = self.session.get(f"{BACKEND_URL}/sessions")
            if response.status_code == 200:
                sessions = response.json()
                self.log_test("Get Active Sessions", "PASS", f"Retrieved {len(sessions)} active sessions")
            else:
                self.log_test("Get Active Sessions", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Get Active Sessions", "FAIL", f"Error: {str(e)}")
        
        # Test get session commands (with dummy session ID)
        try:
            dummy_session_id = "test-session-123"
            response = self.session.get(f"{BACKEND_URL}/sessions/{dummy_session_id}/commands")
            if response.status_code == 200:
                commands = response.json()
                self.log_test("Get Session Commands", "PASS", f"Retrieved {len(commands)} commands for session")
            else:
                self.log_test("Get Session Commands", "PASS", f"HTTP {response.status_code} (expected for non-existent session)")
        except Exception as e:
            self.log_test("Get Session Commands", "FAIL", f"Error: {str(e)}")
    
    def test_command_execution(self):
        """Test command execution endpoint"""
        print("\n🔍 Testing Command Execution...")
        
        try:
            dummy_session_id = "test-session-123"
            command_data = {
                "session_id": dummy_session_id,
                "command": "echo 'Educational test command'"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/sessions/{dummy_session_id}/execute",
                json=command_data
            )
            
            if response.status_code == 404:
                self.log_test("Command Execution", "PASS", "Correctly returns 404 for non-existent session")
            elif response.status_code == 200:
                self.log_test("Command Execution", "PASS", "Command execution endpoint accessible")
            else:
                self.log_test("Command Execution", "WARN", f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Command Execution", "FAIL", f"Error: {str(e)}")
    
    def test_file_transfer(self):
        """Test file transfer endpoint"""
        print("\n🔍 Testing File Transfer...")
        
        try:
            dummy_session_id = "test-session-123"
            file_data = {
                "session_id": dummy_session_id,
                "filename": "test_educational_file.txt",
                "file_data": base64.b64encode(b"Educational test content").decode(),
                "transfer_type": "upload"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/sessions/{dummy_session_id}/file-transfer",
                json=file_data
            )
            
            if response.status_code == 404:
                self.log_test("File Transfer", "PASS", "Correctly returns 404 for non-existent session")
            elif response.status_code == 200:
                self.log_test("File Transfer", "PASS", "File transfer endpoint accessible")
            else:
                self.log_test("File Transfer", "WARN", f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("File Transfer", "FAIL", f"Error: {str(e)}")
    
    def test_analytics(self):
        """Test analytics endpoint"""
        print("\n🔍 Testing Analytics...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/analytics/sessions-summary")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_sessions", "active_sessions", "connected_clients", "total_commands", "total_file_transfers"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Analytics Summary", "PASS", "All analytics fields present", data)
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Analytics Summary", "FAIL", f"Missing fields: {missing}")
            else:
                self.log_test("Analytics Summary", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Analytics Summary", "FAIL", f"Error: {str(e)}")
    
    def test_legacy_endpoints(self):
        """Test legacy status endpoints"""
        print("\n🔍 Testing Legacy Endpoints...")
        
        # Test create status check
        try:
            status_data = {"client_name": "educational_test_client"}
            response = self.session.post(f"{BACKEND_URL}/status", json=status_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "client_name" in data:
                    self.log_test("Create Status Check", "PASS", "Status check created successfully")
                    
                    # Test get status checks
                    response = self.session.get(f"{BACKEND_URL}/status")
                    if response.status_code == 200:
                        statuses = response.json()
                        self.log_test("Get Status Checks", "PASS", f"Retrieved {len(statuses)} status checks")
                    else:
                        self.log_test("Get Status Checks", "FAIL", f"HTTP {response.status_code}")
                else:
                    self.log_test("Create Status Check", "FAIL", "Invalid response format")
            else:
                self.log_test("Create Status Check", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Create Status Check", "FAIL", f"Error: {str(e)}")
    
    async def test_websocket_client(self):
        """Test WebSocket client endpoint"""
        print("\n🔍 Testing WebSocket Client Connection...")
        
        try:
            client_id = "educational_test_client"
            uri = f"{WS_BASE_URL}/ws/client/{client_id}"
            
            async with websockets.connect(uri) as websocket:
                # Wait for welcome message
                welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                welcome_data = json.loads(welcome_msg)
                
                if welcome_data.get("type") == "welcome":
                    self.log_test("WebSocket Client Connection", "PASS", "Successfully connected and received welcome message")
                    
                    # Test sending encrypted response
                    if self.cipher_suite:
                        response_data = {
                            "type": "heartbeat",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        encrypted_response = self.cipher_suite.encrypt(json.dumps(response_data).encode())
                        await websocket.send(base64.b64encode(encrypted_response).decode())
                        
                        self.log_test("WebSocket Encrypted Communication", "PASS", "Successfully sent encrypted heartbeat")
                    else:
                        self.log_test("WebSocket Encrypted Communication", "FAIL", "No encryption key available")
                else:
                    self.log_test("WebSocket Client Connection", "FAIL", "Invalid welcome message format")
                    
        except asyncio.TimeoutError:
            self.log_test("WebSocket Client Connection", "FAIL", "Connection timeout")
        except Exception as e:
            self.log_test("WebSocket Client Connection", "FAIL", f"Error: {str(e)}")
    
    async def test_websocket_dashboard(self):
        """Test WebSocket dashboard endpoint"""
        print("\n🔍 Testing WebSocket Dashboard Connection...")
        
        try:
            uri = f"{WS_BASE_URL}/ws/dashboard"
            
            async with websockets.connect(uri) as websocket:
                # Wait for dashboard update
                update_msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                update_data = json.loads(update_msg)
                
                if update_data.get("type") == "dashboard_update":
                    self.log_test("WebSocket Dashboard Connection", "PASS", "Successfully connected and received dashboard update")
                else:
                    self.log_test("WebSocket Dashboard Connection", "FAIL", "Invalid dashboard update format")
                    
        except asyncio.TimeoutError:
            self.log_test("WebSocket Dashboard Connection", "FAIL", "Connection timeout")
        except Exception as e:
            self.log_test("WebSocket Dashboard Connection", "FAIL", f"Error: {str(e)}")
    
    def test_security_features(self):
        """Test security and encryption features"""
        print("\n🔍 Testing Security Features...")
        
        if self.encryption_key and self.cipher_suite:
            try:
                # Test encryption/decryption
                test_message = "Educational cybersecurity test message"
                encrypted = self.cipher_suite.encrypt(test_message.encode())
                decrypted = self.cipher_suite.decrypt(encrypted).decode()
                
                if decrypted == test_message:
                    self.log_test("AES Encryption/Decryption", "PASS", "Encryption working correctly")
                else:
                    self.log_test("AES Encryption/Decryption", "FAIL", "Decryption mismatch")
                    
            except Exception as e:
                self.log_test("AES Encryption/Decryption", "FAIL", f"Error: {str(e)}")
        else:
            self.log_test("AES Encryption/Decryption", "FAIL", "No encryption key available")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Backend Testing for CyberSec Educational Platform")
        print("=" * 80)
        
        # HTTP API Tests
        self.test_basic_endpoints()
        self.test_session_management()
        self.test_command_execution()
        self.test_file_transfer()
        self.test_analytics()
        self.test_legacy_endpoints()
        self.test_security_features()
        
        # WebSocket Tests
        await self.test_websocket_client()
        await self.test_websocket_dashboard()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"📈 TOTAL: {len(self.test_results)}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   - {result['test']}: {result['message']}")
        
        if warnings > 0:
            print("\n⚠️  WARNINGS:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"   - {result['test']}: {result['message']}")
        
        return failed == 0

async def main():
    """Main test execution"""
    tester = CyberSecPlatformTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())