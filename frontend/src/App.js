import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Educational Disclaimer Component
const EducationalDisclaimer = ({ onAccept }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="text-center mb-6">
          <div className="text-6xl mb-4">🚨</div>
          <h1 className="text-3xl font-bold text-red-600 mb-2">EDUCATIONAL CYBERSECURITY PLATFORM</h1>
          <p className="text-lg text-gray-700">For Authorized Learning and Research Only</p>
        </div>
        
        <div className="space-y-4 text-sm">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <h3 className="font-bold text-yellow-800 mb-2">⚠️ WARNING:</h3>
            <p className="text-yellow-700">This is an educational tool for authorized penetration testing and cybersecurity learning only.</p>
          </div>
          
          <div className="bg-green-50 border-l-4 border-green-400 p-4">
            <h3 className="font-bold text-green-800 mb-2">✅ AUTHORIZED USES:</h3>
            <ul className="list-disc list-inside text-green-700 space-y-1">
              <li>Educational coursework and research</li>
              <li>Authorized penetration testing on systems you own</li>
              <li>Cybersecurity training in controlled environments</li>
              <li>Academic projects and internships</li>
            </ul>
          </div>
          
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <h3 className="font-bold text-red-800 mb-2">❌ PROHIBITED USES:</h3>
            <ul className="list-disc list-inside text-red-700 space-y-1">
              <li>Unauthorized access to systems</li>
              <li>Malicious activities</li>
              <li>Illegal hacking or intrusion</li>
              <li>Any activity without explicit permission</li>
            </ul>
          </div>
          
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h3 className="font-bold text-blue-800 mb-2">📚 EDUCATIONAL PURPOSE:</h3>
            <p className="text-blue-700">This platform helps students understand reverse shell concepts, socket programming, cybersecurity defense techniques, and ethical hacking methodologies.</p>
          </div>
          
          <div className="bg-gray-50 border-l-4 border-gray-400 p-4">
            <h3 className="font-bold text-gray-800 mb-2">🛡️ LEGAL RESPONSIBILITY:</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              <li>Use only on systems you own or have explicit permission to test</li>
              <li>Comply with all applicable laws and regulations</li>
              <li>Understand the legal implications of cybersecurity tools</li>
              <li>Report vulnerabilities responsibly</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-gray-600 mb-4">By clicking "I Acknowledge", you confirm that you understand these guidelines and will use this tool responsibly for educational purposes only.</p>
          <button 
            onClick={onAccept}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors"
          >
            I Acknowledge and Agree to Use Responsibly
          </button>
        </div>
      </div>
    </div>
  );
};

// Command Terminal Component
const CommandTerminal = ({ sessionId, onCommandExecuted }) => {
  const [command, setCommand] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const executeCommand = async () => {
    if (!command.trim() || !sessionId || isExecuting) return;

    setIsExecuting(true);
    
    try {
      const response = await axios.post(`${API}/sessions/${sessionId}/execute`, {
        session_id: sessionId,
        command: command.trim()
      });

      setCommandHistory(prev => [...prev, command.trim()]);
      setCommand("");
      setHistoryIndex(-1);
      
      if (onCommandExecuted) {
        onCommandExecuted();
      }
      
    } catch (error) {
      console.error("Command execution failed:", error);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      executeCommand();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCommand(commandHistory[commandHistory.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCommand("");
      }
    }
  };

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <div className="text-green-400 font-mono text-sm mb-2">
        Educational Terminal - Session: {sessionId?.substring(0, 8)}
      </div>
      <div className="flex items-center">
        <span className="text-green-400 font-mono text-sm mr-2">root@cybersec:~$</span>
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command... (Use ↑↓ for history)"
          className="flex-1 bg-transparent text-green-400 font-mono text-sm outline-none"
          disabled={isExecuting || !sessionId}
        />
        <button
          onClick={executeCommand}
          disabled={isExecuting || !sessionId || !command.trim()}
          className="ml-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors"
        >
          {isExecuting ? "⏳" : "Execute"}
        </button>
      </div>
    </div>
  );
};

// Session Card Component
const SessionCard = ({ session, isSelected, onSelect, onExecuteCommand }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active": return "text-green-600 bg-green-100";
      case "disconnected": return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  return (
    <div 
      className={`border rounded-lg p-4 cursor-pointer transition-all ${
        isSelected ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:border-gray-300"
      }`}
      onClick={() => onSelect(session)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-800">{session.client_hostname}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(session.status)}`}>
          {session.status}
        </span>
      </div>
      
      <div className="text-sm text-gray-600 space-y-1">
        <div>📍 {session.client_ip}</div>
        <div>🕐 Connected: {formatTime(session.connection_time)}</div>
        {session.last_activity && (
          <div>⚡ Last Activity: {formatTime(session.last_activity)}</div>
        )}
      </div>
      
      {isSelected && session.status === "active" && (
        <div className="mt-3 pt-3 border-t">
          <CommandTerminal 
            sessionId={session.id} 
            onCommandExecuted={onExecuteCommand}
          />
        </div>
      )}
    </div>
  );
};

// Main Dashboard Component
const CyberSecDashboard = () => {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [analytics, setAnalytics] = useState({});
  const [commandHistory, setCommandHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const wsRef = useRef(null);

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [sessionsResponse, analyticsResponse] = await Promise.all([
          axios.get(`${API}/sessions`),
          axios.get(`${API}/analytics/sessions-summary`)
        ]);
        
        setSessions(sessionsResponse.data);
        setAnalytics(analyticsResponse.data);
        setIsLoading(false);
      } catch (error) {
        console.error("Failed to fetch initial data:", error);
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const wsUrl = `${BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/dashboard`;
    
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onopen = () => {
          console.log("Dashboard WebSocket connected");
        };
        
        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "dashboard_update") {
              setSessions(data.sessions);
            }
          } catch (error) {
            console.error("Error parsing WebSocket message:", error);
          }
        };
        
        wsRef.current.onclose = () => {
          console.log("Dashboard WebSocket disconnected, attempting to reconnect...");
          setTimeout(connectWebSocket, 3000);
        };
        
        wsRef.current.onerror = (error) => {
          console.error("Dashboard WebSocket error:", error);
        };
        
      } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        setTimeout(connectWebSocket, 5000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchCommandHistory = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/sessions/${sessionId}/commands`);
      setCommandHistory(response.data);
    } catch (error) {
      console.error("Failed to fetch command history:", error);
    }
  };

  const handleSessionSelect = (session) => {
    setSelectedSession(session);
    fetchCommandHistory(session.id);
  };

  const handleCommandExecuted = () => {
    if (selectedSession) {
      // Refresh command history after a short delay
      setTimeout(() => {
        fetchCommandHistory(selectedSession.id);
      }, 1000);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🔄</div>
          <p className="text-gray-600">Loading Educational CyberSec Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-2xl">🚨</div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Educational CyberSec Platform</h1>
                <p className="text-sm text-gray-600">Reverse Shell Learning Environment</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{analytics.connected_clients || 0}</div>
                <div className="text-xs text-gray-600">Connected</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{analytics.active_sessions || 0}</div>
                <div className="text-xs text-gray-600">Active Sessions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{analytics.total_commands || 0}</div>
                <div className="text-xs text-gray-600">Commands</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sessions Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Sessions</h2>
              
              {sessions.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📡</div>
                  <p className="text-gray-600 mb-2">No active sessions</p>
                  <p className="text-sm text-gray-500">Run the client script to connect</p>
                  <div className="mt-4 text-xs text-gray-400 font-mono bg-gray-50 p-2 rounded">
                    python3 client.py
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <SessionCard
                      key={session.id}
                      session={session}
                      isSelected={selectedSession?.id === session.id}
                      onSelect={handleSessionSelect}
                      onExecuteCommand={handleCommandExecuted}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Command History Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Command History
                {selectedSession && (
                  <span className="text-sm font-normal text-gray-600 ml-2">
                    - {selectedSession.client_hostname}
                  </span>
                )}
              </h2>
              
              {!selectedSession ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">🖥️</div>
                  <p className="text-gray-600">Select a session to view command history</p>
                </div>
              ) : commandHistory.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📝</div>
                  <p className="text-gray-600">No commands executed yet</p>
                  <p className="text-sm text-gray-500">Execute commands using the terminal below</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {commandHistory.map((cmd) => (
                    <div key={cmd.id} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <code className="text-sm font-mono text-blue-600">{cmd.command}</code>
                        <span className="text-xs text-gray-500">
                          {new Date(cmd.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="bg-gray-900 text-green-400 font-mono text-xs p-3 rounded">
                        {cmd.output || "No output"}
                      </div>
                      {cmd.execution_time && (
                        <div className="text-xs text-gray-500 mt-1">
                          Execution time: {cmd.execution_time.toFixed(3)}s
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Educational Information */}
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="text-yellow-400 text-xl mr-3">📚</div>
            <div>
              <h3 className="font-semibold text-yellow-800">Educational Learning Platform</h3>
              <p className="text-yellow-700 text-sm mt-1">
                This platform demonstrates reverse shell concepts for cybersecurity education. 
                Use only for authorized learning, testing on your own systems, and academic research.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

  // Check if disclaimer was previously accepted (in a real app, use secure storage)
  useEffect(() => {
    const accepted = localStorage.getItem('cybersec_disclaimer_accepted');
    if (accepted === 'true') {
      setDisclaimerAccepted(true);
    }
  }, []);

  const handleDisclaimerAccept = () => {
    setDisclaimerAccepted(true);
    localStorage.setItem('cybersec_disclaimer_accepted', 'true');
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <div>
              {!disclaimerAccepted && (
                <EducationalDisclaimer onAccept={handleDisclaimerAccept} />
              )}
              <CyberSecDashboard />
            </div>
          } />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
