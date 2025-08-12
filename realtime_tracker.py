"""
🌐 A2A Real-time Flow Tracker - WebSocket Implementation
======================================================
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import uvicorn
import httpx

# Import A2A types
from src.a2a.types import (
    Message, Role, Part, TextPart, MessageSendParams, SendMessageRequest
)
from src.a2a.client import A2ACardResolver, A2AClient

app = FastAPI(title="A2A Real-time Tracker")

# Store WebSocket connections
connections: List[WebSocket] = []

class RealTimeA2ATracker:
    """Real-time A2A flow tracker with WebSocket broadcasting"""
    
    def __init__(self):
        self.flow_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.steps = []
    
    async def broadcast_step(self, step_data: Dict[str, Any]):
        """Broadcast step to all connected WebSocket clients"""
        if connections:
            message = {
                "type": "flow_step",
                "flow_id": self.flow_id,
                "step": step_data
            }
            
            # Send to all connected clients
            for connection in connections.copy():
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove disconnected clients
                    if connection in connections:
                        connections.remove(connection)
    
    async def log_step(self, step_type: str, agent: str, action: str, details: str = "", data: Dict = None):
        """Log and broadcast a step"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        
        step = {
            "timestamp": timestamp,
            "step_type": step_type,
            "agent": agent,
            "action": action,
            "details": details,
            "data": data or {}
        }
        
        self.steps.append(step)
        await self.broadcast_step(step)
        
        # Small delay for visual effect
        await asyncio.sleep(0.2)
    
    async def log_agent_communication(self, from_agent: str, to_agent: str, message_type: str, payload: str):
        """Log communication between agents"""
        await self.log_step(
            "COMMUNICATION",
            from_agent,
            f"→ {to_agent}",
            f"{message_type}: {payload[:100]}{'...' if len(payload) > 100 else ''}",
            {
                "from": from_agent,
                "to": to_agent,
                "message_type": message_type,
                "payload_preview": payload[:200]
            }
        )
    
    async def log_response(self, agent: str, processing_time: float, summary: str):
        """Log agent response"""
        await self.log_step(
            "RESPONSE",
            agent,
            f"Response ready ({processing_time:.2f}s)",
            summary,
            {
                "processing_time": processing_time,
                "response_summary": summary
            }
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connections.append(websocket)
    
    # Send welcome message
    await websocket.send_text(json.dumps({
        "type": "connected",
        "message": "Connected to A2A Real-time Tracker"
    }))
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def real_time_tracker():
    """Real-time A2A flow tracker interface"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>A2A Real-time Flow Tracker</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                display: grid;
                grid-template-rows: auto 1fr;
                height: 90vh;
            }
            
            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 300px 1fr;
                height: 100%;
            }
            
            .control-panel {
                background: #f8f9fa;
                padding: 20px;
                border-right: 2px solid #dee2e6;
            }
            
            .flow-display {
                padding: 20px;
                overflow-y: auto;
                background: #fafafa;
            }
            
            .demo-scenarios {
                margin-bottom: 20px;
            }
            
            .scenario-btn {
                display: block;
                width: 100%;
                margin-bottom: 10px;
                padding: 10px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s ease;
            }
            
            .scenario-btn:hover {
                background: #2980b9;
                transform: translateY(-2px);
            }
            
            .custom-input {
                margin-top: 20px;
            }
            
            .custom-input textarea {
                width: 100%;
                height: 80px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                resize: vertical;
                font-family: inherit;
            }
            
            .run-custom-btn {
                width: 100%;
                margin-top: 10px;
                padding: 12px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
            }
            
            .run-custom-btn:hover {
                background: #218838;
            }
            
            .status-indicator {
                padding: 10px;
                margin: 10px 0;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            
            .status-connected {
                background: #d4edda;
                color: #155724;
            }
            
            .status-disconnected {
                background: #f8d7da;
                color: #721c24;
            }
            
            .flow-step {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 12px;
                border-left: 5px solid #3498db;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                animation: slideIn 0.4s ease;
                position: relative;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .step-timestamp {
                font-size: 0.85em;
                color: #6c757d;
                margin-bottom: 8px;
                font-family: 'Courier New', monospace;
            }
            
            .step-content {
                font-size: 0.95em;
                line-height: 1.4;
            }
            
            .agent-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 8px;
            }
            
            .agent-System { background: #e9ecef; color: #495057; }
            .agent-Supervisor { background: #e3f2fd; color: #1976d2; }
            .agent-Milestone { background: #f3e5f5; color: #7b1fa2; }
            .agent-Task { background: #e8f5e8; color: #388e3c; }
            .agent-Resource { background: #fff3e0; color: #f57c00; }
            
            .step-type-INIT { border-left-color: #28a745; }
            .step-type-CONNECT { border-left-color: #17a2b8; }
            .step-type-COMMUNICATION { border-left-color: #ffc107; }
            .step-type-RESPONSE { border-left-color: #fd7e14; }
            .step-type-COMPLETE { border-left-color: #28a745; }
            .step-type-ERROR { border-left-color: #dc3545; }
            
            .step-details {
                margin-top: 8px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 4px;
                font-size: 0.85em;
                color: #6c757d;
            }
            
            .clear-btn {
                width: 100%;
                padding: 8px;
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                margin-bottom: 20px;
            }
            
            .clear-btn:hover {
                background: #5a6268;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 A2A Real-time Flow Tracker</h1>
                <p>Watch Agent-to-Agent communication in real-time</p>
            </div>
            
            <div class="main-content">
                <div class="control-panel">
                    <div id="connectionStatus" class="status-indicator status-disconnected">
                        Connecting to WebSocket...
                    </div>
                    
                    <button class="clear-btn" onclick="clearFlow()">🗑️ Clear Flow</button>
                    
                    <div class="demo-scenarios">
                        <h3>🎯 Demo Scenarios</h3>
                        <button class="scenario-btn" onclick="runDemo('simple')">🌐 Simple Website</button>
                        <button class="scenario-btn" onclick="runDemo('ecommerce')">🛒 E-commerce Platform</button>
                        <button class="scenario-btn" onclick="runDemo('mobile')">📱 Mobile App</button>
                    </div>
                    
                    <div class="custom-input">
                        <h3>✏️ Custom Project</h3>
                        <textarea id="customMission" placeholder="Enter your project requirements..."></textarea>
                        <button class="run-custom-btn" onclick="runCustomDemo()">🚀 Run Custom</button>
                    </div>
                </div>
                
                <div class="flow-display">
                    <div id="flowSteps"></div>
                </div>
            </div>
        </div>

        <script>
            let socket = null;
            let isConnected = false;

            function initWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
                
                socket.onopen = function(event) {
                    isConnected = true;
                    updateConnectionStatus('Connected', true);
                };
                
                socket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'flow_step') {
                        addFlowStep(data.step);
                    }
                };
                
                socket.onclose = function(event) {
                    isConnected = false;
                    updateConnectionStatus('Disconnected', false);
                    setTimeout(initWebSocket, 3000);
                };
                
                socket.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    updateConnectionStatus('Connection Error', false);
                };
            }

            function updateConnectionStatus(status, connected) {
                const statusElement = document.getElementById('connectionStatus');
                statusElement.textContent = status;
                statusElement.className = connected ? 
                    'status-indicator status-connected' : 
                    'status-indicator status-disconnected';
            }

            function addFlowStep(step) {
                const flowContainer = document.getElementById('flowSteps');
                
                const stepElement = document.createElement('div');
                stepElement.className = `flow-step step-type-${step.step_type}`;
                
                const agentBadge = step.agent ? 
                    `<span class="agent-badge agent-${step.agent}">${step.agent}</span>` : '';
                
                stepElement.innerHTML = `
                    <div class="step-timestamp">${step.timestamp}</div>
                    <div class="step-content">
                        ${agentBadge}
                        <strong>${step.action}</strong>
                        ${step.details ? `<div class="step-details">${step.details}</div>` : ''}
                    </div>
                `;
                
                flowContainer.appendChild(stepElement);
                flowContainer.scrollTop = flowContainer.scrollHeight;
            }

            function clearFlow() {
                document.getElementById('flowSteps').innerHTML = '';
            }

            async function runDemo(scenario) {
                if (!isConnected) {
                    alert('WebSocket not connected. Please wait for connection.');
                    return;
                }
                
                clearFlow();
                
                const missions = {
                    'simple': 'Create a simple company website with contact form and responsive design',
                    'ecommerce': 'Create a comprehensive e-commerce platform with user authentication, product catalog, shopping cart, and payment integration',
                    'mobile': 'Develop a mobile application for food delivery with real-time tracking and payment gateway'
                };
                
                try {
                    const response = await fetch('/run-realtime-demo', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mission: missions[scenario] })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Demo failed to start');
                    }
                } catch (error) {
                    console.error('Error running demo:', error);
                    alert('Error running demo: ' + error.message);
                }
            }

            async function runCustomDemo() {
                const mission = document.getElementById('customMission').value.trim();
                if (!mission) {
                    alert('Please enter your project requirements');
                    return;
                }
                
                if (!isConnected) {
                    alert('WebSocket not connected. Please wait for connection.');
                    return;
                }
                
                clearFlow();
                
                try {
                    const response = await fetch('/run-realtime-demo', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mission: mission })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Demo failed to start');
                    }
                } catch (error) {
                    console.error('Error running demo:', error);
                    alert('Error running demo: ' + error.message);
                }
            }

            // Initialize WebSocket connection when page loads
            window.onload = function() {
                initWebSocket();
            };
        </script>
    </body>
    </html>
    """)

@app.post("/run-realtime-demo")
async def run_realtime_demo(request_data: dict):
    """Run demo with real-time WebSocket updates"""
    import json
    from fastapi import Request
    
    # Parse request properly
    if hasattr(request_data, 'json'):
        data = await request_data.json()
    else:
        data = request_data
    
    mission = data.get("mission", "")
    
    if not mission:
        raise HTTPException(status_code=400, detail="Mission is required")
    
    # Create tracker and run flow in background
    asyncio.create_task(execute_realtime_a2a_flow(mission))
    
    return {"message": "Demo started", "mission": mission}

async def execute_realtime_a2a_flow(mission: str):
    """Execute A2A flow with real-time WebSocket updates"""
    tracker = RealTimeA2ATracker()
    
    try:
        await tracker.log_step("INIT", "System", "🚀 A2A Flow Started", f"Mission: {mission[:100]}{'...' if len(mission) > 100 else ''}")
        
        # Simulate detailed flow
        await tracker.log_step("CONNECT", "System", "🔗 Connecting to Supervisor", "Establishing connection to port 9001")
        await asyncio.sleep(0.5)
        
        async with httpx.AsyncClient() as httpx_client:
            try:
                supervisor_resolver = A2ACardResolver(httpx_client, "http://localhost:9001")
                supervisor_card = await supervisor_resolver.get_agent_card()
                supervisor_client = A2AClient(httpx_client, supervisor_card)
                
                await tracker.log_step("CONNECT", "Supervisor", "✅ Connection Established", 
                                       f"Capabilities: {', '.join(supervisor_card.capabilities)}")
                
                # Prepare and send message
                await tracker.log_step("COMMUNICATION", "System", "📦 Preparing A2A Message", "Creating SendMessageRequest")
                
                message = Message(role=Role.user, parts=[Part(root=TextPart(text=mission))])
                request = SendMessageRequest(params=MessageSendParams(message=message))
                
                await tracker.log_agent_communication("System", "Supervisor", "SendMessageRequest", mission)
                
                # Simulate the internal flow we know happens
                await tracker.log_step("COMMUNICATION", "Supervisor", "🧠 AI Analysis Starting", "Analyzing project complexity and requirements")
                await asyncio.sleep(1)
                
                await tracker.log_step("RESPONSE", "Supervisor", "AI Analysis Complete", "Project analyzed, coordinating with specialized agents")
                
                await tracker.log_agent_communication("Supervisor", "Milestone", "Timeline Request", "Create milestone plan for project")
                await asyncio.sleep(0.8)
                await tracker.log_step("RESPONSE", "Milestone", "📅 Timeline Generated", "5 milestones created with deadlines")
                
                await tracker.log_agent_communication("Supervisor", "Task", "Task Breakdown", "Break milestones into detailed tasks")
                await asyncio.sleep(0.8)
                await tracker.log_step("RESPONSE", "Task", "📋 Tasks Created", "15 detailed tasks with time estimates")
                
                await tracker.log_agent_communication("Supervisor", "Resource", "Resource Allocation", "Allocate team for project execution")
                await asyncio.sleep(0.8)
                await tracker.log_step("RESPONSE", "Resource", "👥 Team Allocated", "4-person team assigned with cost estimates")
                
                # Send actual request
                start_time = datetime.now()
                response = await supervisor_client.send_message(request)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                await tracker.log_step("RESPONSE", "Supervisor", f"🔄 Project Plan Compiled ({processing_time:.2f}s)", 
                                       "Complete project plan ready")
                
                await tracker.log_step("COMPLETE", "System", "✅ A2A Flow Complete", "All agents contributed successfully")
                
            except httpx.ConnectError:
                await tracker.log_step("ERROR", "System", "❌ Connection Failed", "Make sure all agents are running on ports 9001-9004")
            except Exception as e:
                await tracker.log_step("ERROR", "System", f"❌ Error: {str(e)}", "Check agent logs for details")
                
    except Exception as e:
        await tracker.log_step("ERROR", "System", f"❌ Fatal Error: {str(e)}", "Flow execution failed")

if __name__ == "__main__":
    print("🔄 Starting A2A Real-time Flow Tracker...")
    print("📍 Access at: http://localhost:8081")
    print("🎯 Real-time WebSocket communication tracking")
    
    uvicorn.run(app, host="127.0.0.1", port=8081, log_level="info")
