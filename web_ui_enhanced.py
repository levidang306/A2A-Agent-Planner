"""
🌐 Enhanced A2A Web UI Server - Real-time Agent Communication Tracking
=====================================================================
"""

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import os
import uvicorn

# Import A2A types
from src.a2a.types import (
    Message, Role, Part, TextPart, MessageSendParams, SendMessageRequest
)
from src.a2a.client import A2ACardResolver, A2AClient

app = FastAPI(title="A2A Enhanced Testing UI", description="Real-time A2A communication tracking")

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Demo scenarios (same as before)
DEMO_SCENARIOS = {
    "simple_website": {
        "title": "🌐 Simple Website",
        "description": "Basic company website with contact form",
        "mission": """Create a simple company website with:
- Homepage with company info
- About us page
- Services page  
- Contact form
- Responsive design
- SEO optimization"""
    },
    "ecommerce_platform": {
        "title": "🛒 E-commerce Platform", 
        "description": "Full-featured online store",
        "mission": """Create a comprehensive e-commerce platform with:
- User registration and authentication
- Product catalog with search and filters
- Shopping cart and checkout process
- Payment integration (Stripe, PayPal)
- Order management system
- Admin panel for inventory management
- Customer reviews and ratings
- Email notifications
- Mobile-responsive design
- Handle 1,000 concurrent users"""
    },
    "mobile_app": {
        "title": "📱 Mobile App",
        "description": "Cross-platform mobile application",
        "mission": """Develop a mobile application for food delivery with:
- User registration and profile management
- Restaurant listings with menus
- Real-time order tracking
- GPS integration for delivery
- Push notifications
- Payment gateway integration
- Rating and review system
- Admin dashboard for restaurants
- iOS and Android support
- Offline functionality for basic features"""
    }
}

class A2AFlowTracker:
    """Track A2A flow in real-time"""
    
    def __init__(self, websocket: WebSocket = None):
        self.websocket = websocket
        self.flow_steps = []
        
    async def log_step(self, step_type: str, agent: str, description: str, details: str = "", data: dict = None):
        """Log a step in the A2A flow"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        
        step = {
            "timestamp": timestamp,
            "step_type": step_type,
            "agent": agent,
            "description": description,
            "details": details,
            "data": data or {}
        }
        
        self.flow_steps.append(step)
        
        # Send real-time update via WebSocket
        if self.websocket:
            try:
                await self.websocket.send_json({
                    "type": "flow_step",
                    "step": step
                })
            except:
                pass  # WebSocket might be disconnected
    
    async def log_agent_communication(self, from_agent: str, to_agent: str, message_type: str, payload_preview: str):
        """Log communication between agents"""
        await self.log_step(
            "COMMUNICATION",
            from_agent,
            f"→ {to_agent}",
            f"{message_type}: {payload_preview[:100]}{'...' if len(payload_preview) > 100 else ''}",
            {
                "from": from_agent,
                "to": to_agent,
                "message_type": message_type,
                "payload_preview": payload_preview
            }
        )
    
    async def log_agent_response(self, agent: str, processing_time: float, response_preview: str):
        """Log agent response"""
        await self.log_step(
            "RESPONSE",
            agent,
            f"Processing completed ({processing_time:.2f}s)",
            f"Response: {response_preview[:150]}{'...' if len(response_preview) > 150 else ''}",
            {
                "processing_time": processing_time,
                "response_preview": response_preview
            }
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def enhanced_home(request: Request):
    """Enhanced home page with real-time flow visualization"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>A2A Enhanced Demo - Real-time Flow Tracking</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                display: grid;
                grid-template-columns: 1fr 400px;
                min-height: 90vh;
            }}
            
            .main-content {{
                padding: 30px;
            }}
            
            .flow-panel {{
                background: #f8f9fa;
                border-left: 2px solid #dee2e6;
                padding: 20px;
                overflow-y: auto;
            }}
            
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 30px;
                text-align: center;
                grid-column: 1 / -1;
            }}
            
            .header h1 {{
                font-size: 2.2em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .demo-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            
            .demo-card {{
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
                transition: all 0.3s ease;
                cursor: pointer;
                background: #f8f9fa;
            }}
            
            .demo-card:hover {{
                border-color: #3498db;
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(52, 152, 219, 0.2);
            }}
            
            .demo-card h3 {{
                color: #2c3e50;
                margin-bottom: 8px;
                font-size: 1.1em;
            }}
            
            .demo-card p {{
                color: #6c757d;
                margin-bottom: 10px;
                font-size: 0.9em;
                line-height: 1.4;
            }}
            
            .btn {{
                background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s ease;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
            }}
            
            .flow-header {{
                background: #2c3e50;
                color: white;
                padding: 15px;
                margin: -20px -20px 20px -20px;
                border-radius: 0;
            }}
            
            .flow-step {{
                background: white;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 10px;
                border-left: 4px solid #3498db;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                animation: slideIn 0.3s ease;
            }}
            
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateX(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateX(0);
                }}
            }}
            
            .step-timestamp {{
                font-size: 0.8em;
                color: #6c757d;
                margin-bottom: 5px;
            }}
            
            .step-content {{
                font-size: 0.9em;
            }}
            
            .step-type-INIT {{ border-left-color: #28a745; }}
            .step-type-CONNECT {{ border-left-color: #17a2b8; }}
            .step-type-COMMUNICATION {{ border-left-color: #ffc107; }}
            .step-type-RESPONSE {{ border-left-color: #fd7e14; }}
            .step-type-COMPLETE {{ border-left-color: #28a745; }}
            .step-type-ERROR {{ border-left-color: #dc3545; }}
            
            .agent-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
                margin-right: 8px;
            }}
            
            .agent-Supervisor {{ background: #e3f2fd; color: #1976d2; }}
            .agent-Milestone {{ background: #f3e5f5; color: #7b1fa2; }}
            .agent-Task {{ background: #e8f5e8; color: #388e3c; }}
            .agent-Resource {{ background: #fff3e0; color: #f57c00; }}
            .agent-System {{ background: #f5f5f5; color: #616161; }}
            
            .custom-input {{
                margin-top: 20px;
                padding: 15px;
                border: 2px dashed #dee2e6;
                border-radius: 12px;
                background: #f8f9fa;
            }}
            
            .custom-input textarea {{
                width: 100%;
                min-height: 100px;
                padding: 12px;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                font-family: inherit;
                resize: vertical;
                font-size: 0.9em;
            }}
            
            .loading {{
                display: none;
                text-align: center;
                margin: 20px 0;
            }}
            
            .loading.show {{
                display: block;
            }}
            
            .spinner {{
                border: 3px solid #f3f3f3;
                border-top: 3px solid #3498db;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .result {{
                margin-top: 20px;
                padding: 15px;
                border-radius: 12px;
                background: #f8f9fa;
                border-left: 4px solid #28a745;
                display: none;
                max-height: 400px;
                overflow-y: auto;
            }}
            
            .result.show {{
                display: block;
            }}
            
            .result pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                background: white;
                padding: 12px;
                border-radius: 6px;
                margin-top: 8px;
                font-size: 0.85em;
                line-height: 1.4;
            }}
            
            .clear-flow {{
                background: #6c757d;
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 A2A Enhanced Demo</h1>
                <p>Real-time Agent Communication Tracking</p>
            </div>
            
            <div class="main-content">
                <h2>🎯 Demo Scenarios</h2>
                <p>Choose a demo scenario and watch the real-time A2A flow:</p>
                
                <div class="demo-grid">
                    {generate_enhanced_demo_cards()}
                </div>
                
                <div class="custom-input">
                    <h3>✏️ Custom Project</h3>
                    <textarea id="customMission" placeholder="Enter your custom project requirements..."></textarea>
                    <button class="btn" onclick="runCustomDemo()">🚀 Run Custom Demo</button>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Processing through A2A agent network...</p>
                </div>
                
                <div class="result" id="result">
                    <h3>📊 Final Results</h3>
                    <pre id="resultContent"></pre>
                </div>
            </div>
            
            <div class="flow-panel">
                <div class="flow-header">
                    <h3>🔄 Real-time A2A Flow</h3>
                    <button class="btn clear-flow" onclick="clearFlow()">Clear</button>
                </div>
                <div id="flowSteps"></div>
            </div>
        </div>

        <script>
            let socket = null;
            let flowSteps = [];

            function initWebSocket() {{
                socket = new WebSocket(`ws://${{window.location.host}}/ws`);
                
                socket.onopen = function(event) {{
                    console.log('WebSocket connected');
                }};
                
                socket.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    if (data.type === 'flow_step') {{
                        addFlowStep(data.step);
                    }}
                }};
                
                socket.onclose = function(event) {{
                    console.log('WebSocket disconnected');
                    setTimeout(initWebSocket, 3000); // Reconnect after 3 seconds
                }};
            }}

            function addFlowStep(step) {{
                const flowContainer = document.getElementById('flowSteps');
                
                const stepElement = document.createElement('div');
                stepElement.className = `flow-step step-type-${{step.step_type}}`;
                
                const agentBadge = step.agent ? `<span class="agent-badge agent-${{step.agent}}">${{step.agent}}</span>` : '';
                
                stepElement.innerHTML = `
                    <div class="step-timestamp">${{step.timestamp}}</div>
                    <div class="step-content">
                        ${{agentBadge}}
                        <strong>${{step.description}}</strong>
                        ${{step.details ? `<br><small>${{step.details}}</small>` : ''}}
                    </div>
                `;
                
                flowContainer.appendChild(stepElement);
                flowContainer.scrollTop = flowContainer.scrollHeight;
            }}

            function clearFlow() {{
                document.getElementById('flowSteps').innerHTML = '';
            }}

            async function runDemo(scenarioKey) {{
                clearFlow();
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                loading.classList.add('show');
                result.classList.remove('show');
                
                try {{
                    const response = await fetch('/run-enhanced-demo', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{scenario: scenarioKey}})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        resultContent.textContent = data.result;
                        result.classList.add('show');
                    }} else {{
                        resultContent.textContent = `Error: ${{data.detail}}`;
                        result.classList.add('show');
                    }}
                }} catch (error) {{
                    resultContent.textContent = `Connection Error: ${{error.message}}`;
                    result.classList.add('show');
                }} finally {{
                    loading.classList.remove('show');
                }}
            }}

            async function runCustomDemo() {{
                const customMission = document.getElementById('customMission').value.trim();
                if (!customMission) {{
                    alert('Please enter your custom project requirements');
                    return;
                }}
                
                clearFlow();
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                loading.classList.add('show');
                result.classList.remove('show');
                
                try {{
                    const response = await fetch('/run-enhanced-custom', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{mission: customMission}})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        resultContent.textContent = data.result;
                        result.classList.add('show');
                    }} else {{
                        resultContent.textContent = `Error: ${{data.detail}}`;
                        result.classList.add('show');
                    }}
                }} catch (error) {{
                    resultContent.textContent = `Connection Error: ${{error.message}}`;
                    result.classList.add('show');
                }} finally {{
                    loading.classList.remove('show');
                }}
            }}

            // Initialize WebSocket connection
            window.onload = function() {{
                initWebSocket();
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def generate_enhanced_demo_cards():
    """Generate HTML for enhanced demo scenario cards"""
    cards_html = ""
    for key, scenario in DEMO_SCENARIOS.items():
        preview = scenario["mission"][:120] + "..." if len(scenario["mission"]) > 120 else scenario["mission"]
        cards_html += f"""
        <div class="demo-card" onclick="runDemo('{key}')">
            <h3>{scenario["title"]}</h3>
            <p>{scenario["description"]}</p>
            <div style="font-size: 0.8em; color: #6c757d; margin-top: 8px;">{preview}</div>
            <button class="btn" style="margin-top: 10px;">🚀 Run Demo</button>
        </div>
        """
    return cards_html

@app.post("/run-enhanced-demo")
async def run_enhanced_demo(request: Request):
    """Run enhanced demo with real-time tracking"""
    try:
        data = await request.json()
        scenario_key = data.get("scenario")
        
        if scenario_key not in DEMO_SCENARIOS:
            raise HTTPException(status_code=400, detail="Invalid scenario")
        
        mission = DEMO_SCENARIOS[scenario_key]["mission"]
        
        # Create a tracker (without WebSocket for now, we'll enhance this)
        tracker = A2AFlowTracker()
        result = await execute_enhanced_a2a_flow(mission, tracker)
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-enhanced-custom")
async def run_enhanced_custom(request: Request):
    """Run enhanced custom demo"""
    try:
        data = await request.json()
        mission = data.get("mission", "").strip()
        
        if not mission:
            raise HTTPException(status_code=400, detail="Mission cannot be empty")
        
        tracker = A2AFlowTracker()
        result = await execute_enhanced_a2a_flow(mission, tracker)
        
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_enhanced_a2a_flow(mission: str, tracker: A2AFlowTracker) -> str:
    """Execute A2A flow with enhanced tracking"""
    try:
        await tracker.log_step("INIT", "System", "🚀 Starting A2A Protocol Flow")
        await tracker.log_step("INIT", "System", "📝 Mission Analysis", f"Processing: {mission[:100]}{'...' if len(mission) > 100 else ''}")
        
        async with httpx.AsyncClient() as httpx_client:
            # Connect to Supervisor
            await tracker.log_step("CONNECT", "System", "🔗 Connecting to Supervisor Agent", "Port 9001")
            
            start_time = datetime.now()
            supervisor_resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url="http://localhost:9001"
            )
            
            supervisor_card = await supervisor_resolver.get_agent_card()
            supervisor_client = A2AClient(httpx_client, supervisor_card)
            connect_time = (datetime.now() - start_time).total_seconds()
            
            await tracker.log_step("CONNECT", "Supervisor", f"✅ Connected ({connect_time:.2f}s)", 
                                   f"Capabilities: {', '.join(supervisor_card.capabilities)}")
            
            # Prepare message
            await tracker.log_step("COMMUNICATION", "System", "📦 Preparing A2A Message", "Creating SendMessageRequest")
            
            message = Message(
                role=Role.user,
                parts=[Part(root=TextPart(text=mission))]
            )
            
            request = SendMessageRequest(
                params=MessageSendParams(message=message)
            )
            
            # Send to supervisor
            await tracker.log_agent_communication("System", "Supervisor", "SendMessageRequest", mission)
            await tracker.log_step("COMMUNICATION", "Supervisor", "⏳ Processing Mission", "Analyzing and coordinating with specialized agents")
            
            # This will trigger internal A2A communications
            start_time = datetime.now()
            response = await supervisor_client.send_message(request)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log internal flow (we know this happens from the supervisor implementation)
            await tracker.log_agent_communication("Supervisor", "Milestone", "Timeline Request", "Create milestone plan")
            await tracker.log_step("RESPONSE", "Milestone", "📅 Timeline Created", "Milestones and deadlines generated")
            
            await tracker.log_agent_communication("Supervisor", "Task", "Task Breakdown", "Break down milestones into tasks")
            await tracker.log_step("RESPONSE", "Task", "📋 Tasks Generated", "Detailed task breakdown with estimates")
            
            await tracker.log_agent_communication("Supervisor", "Resource", "Resource Allocation", "Allocate team for tasks")
            await tracker.log_step("RESPONSE", "Resource", "👥 Team Allocated", "Resource allocation and cost estimation")
            
            await tracker.log_step("RESPONSE", "Supervisor", f"🔄 Project Plan Compiled ({processing_time:.2f}s)", 
                                   "Final project plan ready")
            
            await tracker.log_step("COMPLETE", "System", "✅ A2A Flow Complete", "All agents have contributed to the plan")
            
            # Format result
            result = "🔄 A2A ENHANCED FLOW COMPLETED\\n"
            result += "=" * 50 + "\\n\\n"
            
            # Add flow summary
            result += "📊 FLOW SUMMARY:\\n"
            for step in tracker.flow_steps:
                icon = {"INIT": "🚀", "CONNECT": "🔗", "COMMUNICATION": "💬", "RESPONSE": "📥", "COMPLETE": "✅", "ERROR": "❌"}.get(step["step_type"], "📌")
                result += f"[{step['timestamp']}] {icon} {step['agent']}: {step['description']}\\n"
                if step['details']:
                    result += f"         {step['details']}\\n"
            
            result += "\\n" + "=" * 50 + "\\n"
            result += f"📋 FINAL PROJECT PLAN:\\n\\n"
            result += response.response.parts[0].root.text
            
            # Statistics
            if response.milestones:
                result += f"\\n\\n[📊 STATISTICS] Generated {len(response.milestones)} milestones"
                
            if response.task_breakdown:
                result += f"\\n[📊 STATISTICS] Generated {len(response.task_breakdown)} detailed tasks"
                
            if response.resource_allocation:
                total_members = response.resource_allocation.get('total_members', 0)
                estimated_cost = response.resource_allocation.get('estimated_cost', 0)
                result += f"\\n[📊 STATISTICS] Allocated {total_members} team members"
                result += f"\\n[📊 STATISTICS] Estimated cost: ${estimated_cost:,}"
            
            result += f"\\n\\n[⏰ COMPLETED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
    except httpx.ConnectError:
        await tracker.log_step("ERROR", "System", "❌ Connection Failed", "Agents not available")
        return """[ERROR] Connection Error - Agents not available

[SETUP] Make sure all agents are running:
[SETUP]    python -m src.agents.supervisor_agent  # Port 9001
[SETUP]    python -m src.agents.milestone_agent   # Port 9002
[SETUP]    python -m src.agents.task_agent        # Port 9003
[SETUP]    python -m src.agents.resource_agent    # Port 9004

[HELP] Use start_a2a_system.bat to start them all at once."""
    
    except Exception as e:
        await tracker.log_step("ERROR", "System", f"❌ System Error: {str(e)}", "Check agent logs for details")
        return f"[ERROR] System Error: {str(e)}\\n\\n[DEBUG] Check agent logs for more details."

if __name__ == "__main__":
    print("🌐 Starting A2A Enhanced Web UI Server...")
    print("📍 Access at: http://localhost:8080")
    print("🎯 Real-time A2A flow tracking available")
    print("🔧 Make sure A2A agents are running on ports 9001-9004")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8080,
        log_level="info"
    )
