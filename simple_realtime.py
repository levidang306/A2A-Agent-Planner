"""
🌐 Simple A2A Real-time Tracker
===============================
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime
import uvicorn
import httpx

app = FastAPI()

# Store active WebSocket connections
connections = []

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>A2A Real-time Tracker</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f0f8ff; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
        }
        .status { 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 5px; 
            font-weight: bold;
        }
        .connected { 
            background: #90EE90; 
            color: #006400; 
        }
        .disconnected { 
            background: #FFB6C1; 
            color: #8B0000; 
        }
        .flow-area {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            min-height: 300px;
            margin: 20px 0;
        }
        .demo-controls {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        input, button {
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        button {
            background: #4CAF50;
            color: white;
            cursor: pointer;
        }
        button:hover { background: #45a049; }
        .flow-item {
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #4CAF50;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 A2A Real-time Flow Tracker</h1>
        
        <div id="status" class="status disconnected">
            WebSocket: Disconnected
        </div>
        
        <div class="demo-controls">
            <h3>🚀 Run A2A Demo</h3>
            <input type="text" id="missionInput" placeholder="Enter mission..." 
                   value="Create a mobile app for task management">
            <button onclick="runDemo()">Start Demo</button>
            <button onclick="clearFlow()">Clear</button>
        </div>
        
        <div class="flow-area">
            <h3>📊 Real-time A2A Flow</h3>
            <div id="flowContainer"></div>
        </div>
    </div>

    <script>
        let ws = null;
        
        function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8082/ws');
                
                ws.onopen = function() {
                    document.getElementById('status').innerHTML = 'WebSocket: Connected';
                    document.getElementById('status').className = 'status connected';
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addFlowItem(data);
                };
                
                ws.onclose = function() {
                    document.getElementById('status').innerHTML = 'WebSocket: Disconnected';
                    document.getElementById('status').className = 'status disconnected';
                    console.log('WebSocket disconnected');
                    // Try to reconnect after 3 seconds
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            } catch (error) {
                console.error('Failed to connect:', error);
                setTimeout(connectWebSocket, 3000);
            }
        }
        
        function addFlowItem(data) {
            const container = document.getElementById('flowContainer');
            const item = document.createElement('div');
            item.className = 'flow-item';
            item.innerHTML = `
                <div><strong>${data.step || 'Step'}</strong></div>
                <div>${data.message || data.details || 'No message'}</div>
                <div class="timestamp">${new Date().toLocaleTimeString()}</div>
            `;
            container.appendChild(item);
            container.scrollTop = container.scrollHeight;
        }
        
        function runDemo() {
            const mission = document.getElementById('missionInput').value;
            if (!mission) {
                alert('Please enter a mission');
                return;
            }
            
            fetch('/run-demo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mission: mission })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Demo started:', data);
                addFlowItem({ step: 'Demo Started', message: `Mission: ${mission}` });
            })
            .catch(error => {
                console.error('Error:', error);
                addFlowItem({ step: 'Error', message: 'Failed to start demo' });
            });
        }
        
        function clearFlow() {
            document.getElementById('flowContainer').innerHTML = '';
        }
        
        // Connect on page load
        connectWebSocket();
    </script>
</body>
</html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    print(f"WebSocket connected. Total connections: {len(connections)}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "step": "Connected",
            "message": "Real-time tracker ready",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(connections)}")

@app.post("/run-demo")
async def run_demo(request_data: dict):
    """Run A2A demo with real-time updates"""
    mission = request_data.get("mission", "")
    
    if not mission:
        return {"error": "Mission is required"}
    
    # Start demo in background
    asyncio.create_task(simulate_a2a_flow(mission))
    
    return {"message": "Demo started", "mission": mission}

async def simulate_a2a_flow(mission: str):
    """Simulate A2A flow with real-time updates"""
    
    await broadcast_message({
        "step": "1. Supervisor Agent",
        "message": f"Received mission: {mission}",
        "details": "Processing and dividing work..."
    })
    await asyncio.sleep(2)
    
    await broadcast_message({
        "step": "2. Milestone Agent",
        "message": "Creating timeline and milestones",
        "details": "Breaking down project into phases..."
    })
    await asyncio.sleep(2)
    
    await broadcast_message({
        "step": "3. Task Agent",
        "message": "Generating detailed tasks",
        "details": "Creating actionable tasks with estimates..."
    })
    await asyncio.sleep(2)
    
    await broadcast_message({
        "step": "4. Resource Agent",
        "message": "Allocating team and resources",
        "details": "Matching skills to requirements..."
    })
    await asyncio.sleep(2)
    
    await broadcast_message({
        "step": "✅ Complete",
        "message": "A2A workflow completed successfully!",
        "details": f"Mission '{mission}' has been fully planned and organized."
    })

async def broadcast_message(message: dict):
    """Send message to all connected WebSocket clients"""
    if not connections:
        return
    
    message["timestamp"] = datetime.now().isoformat()
    
    # Send to all connections
    disconnected = []
    for websocket in connections:
        try:
            await websocket.send_json(message)
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in connections:
            connections.remove(ws)

if __name__ == "__main__":
    print("🌐 Starting Simple A2A Real-time Tracker on http://localhost:8082")
    uvicorn.run(app, host="127.0.0.1", port=8082)
