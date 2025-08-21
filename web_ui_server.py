"""
🌐 A2A Web UI Server - Interactive testing interface
====================================================
FastAPI server với HTML UI để test A2A system dễ dàng
"""

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

app = FastAPI(title="A2A Testing UI", description="Web interface for testing A2A Task Management System")

# Mount static files for a2a_projects folder
app.mount("/projects", StaticFiles(directory="a2a_projects"), name="projects")

# Demo scenarios
DEMO_SCENARIOS = {
    "simple_website": {
        "title": "Simple Company Website",
        "description": "Basic company website with contact form",
        "mission": """Create a simple company website project within 4 weeks with:
- Homepage with company info
- About us page
- Services page  
- Contact form
- Responsive design
- SEO optimization

Project timeline: 4 weeks
Expected launch: End of month"""
    },
    "ecommerce_platform": {
        "title": "E-commerce Platform", 
        "description": "Full-featured online store",
        "mission": """Create a comprehensive e-commerce platform project within 12 weeks with:
- User registration and authentication
- Product catalog with search and filters
- Shopping cart and checkout process
- Payment integration (Stripe, PayPal)
- Order management system
- Admin panel for inventory management
- Customer reviews and ratings
- Email notifications
- Mobile-responsive design
- Handle 1,000 concurrent users

Project timeline: 12 weeks
Expected beta release: Week 8
Expected full launch: Week 12"""
    },
    "mobile_app": {
        "title": "Food Delivery Mobile App",
        "description": "Cross-platform mobile application",
        "mission": """Develop a food delivery mobile app project within 16 weeks with:
- User registration and profile management
- Restaurant listings with menus
- Real-time order tracking
- GPS integration for delivery
- Push notifications
- Payment gateway integration
- Rating and review system
- Admin dashboard for restaurants
- iOS and Android support
- Offline functionality for basic features

Project timeline: 16 weeks
Expected MVP: Week 10
Expected beta testing: Week 12
Expected app store launch: Week 16"""
    },
    "enterprise_system": {
        "title": "Enterprise ERP System",
        "description": "Complex business management system",
        "mission": """Build an enterprise resource planning ERP system project within 24 weeks with:
- Multi-tenant architecture
- User management with role-based access
- Financial management modules
- Inventory and supply chain management
- HR management system
- Reporting and analytics dashboard
- API for third-party integrations
- Advanced security features
- Scalable to 10,000+ users
- Compliance with industry standards (SOX, GDPR)
- Real-time data synchronization
- Audit trails and logging

Project timeline: 24 weeks (6 months)
Expected alpha release: Week 12
Expected beta release: Week 18
Expected production release: Week 24"""
    },
    "ai_platform": {
        "title": "AI Machine Learning Platform",
        "description": "Machine learning and AI services platform",
        "mission": """Create an AI-powered machine learning platform project within 20 weeks with:
- Machine learning model training interface
- Data preprocessing and visualization tools
- Model deployment and inference APIs
- A/B testing framework for models
- Real-time monitoring and alerting
- Auto-scaling infrastructure
- Integration with popular ML frameworks
- Data privacy and security compliance
- Multi-language SDK support
- Performance optimization tools
- Cost management and billing system

Project timeline: 20 weeks
Expected core platform: Week 12
Expected beta release: Week 16
Expected production launch: Week 20"""
    },
    "blockchain_dapp": {
        "title": "DeFi Blockchain Application",
        "description": "Decentralized application on blockchain",
        "mission": """Develop a decentralized finance DeFi blockchain application project within 18 weeks with:
- Smart contracts for lending and borrowing
- Wallet integration (MetaMask, WalletConnect)
- Liquidity pool management
- Yield farming mechanisms
- Governance token system
- Multi-chain support (Ethereum, Polygon)
- Security audits and testing
- Real-time price feeds integration
- Mobile wallet compatibility
- Gas optimization strategies
- Decentralized identity verification

Project timeline: 18 weeks
Expected testnet deployment: Week 8
Expected security audit: Week 12
Expected mainnet launch: Week 18"""
    },
    "iot_system": {
        "title": "Smart IoT Monitoring System",
        "description": "Internet of Things monitoring platform",
        "mission": """Build a smart IoT monitoring and control system project within 14 weeks with:
- Device registration and management
- Real-time sensor data collection
- Data visualization dashboards
- Alert and notification system
- Remote device control capabilities
- Edge computing integration
- Time-series database optimization
- Machine learning for predictive maintenance
- API for third-party device integration
- Security protocols for device communication
- Scalable architecture for millions of devices

Project timeline: 14 weeks
Expected device integration: Week 6
Expected dashboard release: Week 10
Expected production deployment: Week 14"""
    },
    "custom": {
        "title": "Custom Project",
        "description": "Enter your own project requirements",
        "mission": ""
    }
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page with demo scenarios"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>A2A Task Management - Demo Testing</title>
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
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .status-bar {{
                background: #f8f9fa;
                padding: 15px 30px;
                border-bottom: 1px solid #dee2e6;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .agent-status {{
                display: flex;
                gap: 15px;
            }}
            
            .agent {{
                display: flex;
                align-items: center;
                gap: 5px;
                padding: 5px 10px;
                border-radius: 15px;
                background: #e9ecef;
                font-size: 0.9em;
            }}
            
            .agent.online {{
                background: #d4edda;
                color: #155724;
            }}
            
            .agent.offline {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #6c757d;
            }}
            
            .status-dot.online {{
                background: #28a745;
            }}
            
            .status-dot.offline {{
                background: #dc3545;
            }}
            
            .content {{
                padding: 30px;
            }}
            
            .demo-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .demo-card {{
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
                transition: all 0.3s ease;
                cursor: pointer;
                background: #f8f9fa;
            }}
            
            .demo-card:hover {{
                border-color: #3498db;
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(52, 152, 219, 0.2);
            }}
            
            .demo-card h3 {{
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1.3em;
            }}
            
            .demo-card p {{
                color: #6c757d;
                margin-bottom: 15px;
                line-height: 1.5;
            }}
            
            .demo-card .mission-preview {{
                background: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 0.9em;
                color: #495057;
                border-left: 4px solid #3498db;
                max-height: 100px;
                overflow: hidden;
            }}
            
            .custom-input {{
                margin-top: 20px;
                padding: 20px;
                border: 2px dashed #dee2e6;
                border-radius: 15px;
                background: #f8f9fa;
            }}
            
            .custom-input textarea {{
                width: 100%;
                min-height: 120px;
                padding: 15px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-family: inherit;
                resize: vertical;
            }}
            
            .btn {{
                background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.3s ease;
                margin-top: 15px;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
            }}
            
            .btn:disabled {{
                background: #6c757d;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
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
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .result {{
                margin-top: 30px;
                padding: 20px;
                border-radius: 15px;
                background: #f8f9fa;
                border-left: 5px solid #28a745;
                display: none;
            }}
            
            .result.show {{
                display: block;
            }}
            
            .result pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                max-height: 500px;
                overflow-y: auto;
            }}
            
            .quick-actions {{
                margin-top: 20px;
                text-align: center;
            }}
            
            .quick-actions button {{
                margin: 0 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 A2A Task Management System</h1>
                <p>Interactive Demo Testing Interface</p>
                <div style="margin-top: 15px;">
                    <a href="/projects-browser" style="color: #fff; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; text-decoration: none; font-weight: 500; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                        🗂️ Browse Generated Projects
                    </a>
                </div>
            </div>
            
            <div class="status-bar">
                <div class="agent-status" id="agentStatus">
                    <div class="agent" id="supervisor">
                        <div class="status-dot"></div>
                        Supervisor (9001)
                    </div>
                    <div class="agent" id="milestone">
                        <div class="status-dot"></div>
                        Milestone (9002)
                    </div>
                    <div class="agent" id="task">
                        <div class="status-dot"></div>
                        Task (9003)
                    </div>
                    <div class="agent" id="resource">
                        <div class="status-dot"></div>
                        Resource (9004)
                    </div>
                </div>
                <button class="btn" onclick="checkAgentStatus()">🔄 Check Status</button>
            </div>
            
            <div class="content">
                <h2>🎯 Demo Scenarios</h2>
                <p>Choose a demo scenario to test the A2A system, or create your own custom project:</p>
                
                <div class="demo-grid">
                    {generate_demo_cards()}
                </div>
                
                <div class="custom-input">
                    <h3>✏️ Custom Project</h3>
                    <textarea id="customMission" placeholder="Enter your custom project requirements here...

Example:
Create a social media platform with user profiles, posts, real-time chat, and content moderation features. The platform should support 50,000 active users and include mobile apps for iOS and Android."></textarea>
                    <button class="btn" onclick="runCustomDemo()">🚀 Run Custom Demo</button>
                </div>
                
                <div class="quick-actions">
                    <button class="btn" onclick="testAgentConnections()">🔗 Test Agent Connections</button>
                    <button class="btn" onclick="clearResults()">🗑️ Clear Results</button>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Processing through A2A agent network...</p>
                </div>
                
                <div class="result" id="result">
                    <h3>📊 A2A System Response</h3>
                    <pre id="resultContent"></pre>
                </div>
            </div>
        </div>

        <script>
            let agentStatus = {{
                supervisor: false,
                milestone: false,
                task: false,
                resource: false
            }};

            async function checkAgentStatus() {{
                const agents = [
                    {{name: 'supervisor', port: 9001}},
                    {{name: 'milestone', port: 9002}},
                    {{name: 'task', port: 9003}},
                    {{name: 'resource', port: 9004}}
                ];

                for (const agent of agents) {{
                    try {{
                        const response = await fetch(`/check-agent/${{agent.port}}`);
                        if (response.ok) {{
                            agentStatus[agent.name] = true;
                            updateAgentStatusUI(agent.name, true);
                        }} else {{
                            const errorData = await response.json();
                            console.warn(`Agent ${{agent.name}} error:`, errorData);
                            agentStatus[agent.name] = false;
                            updateAgentStatusUI(agent.name, false);
                        }}
                    }} catch (e) {{
                        console.error(`Failed to check agent ${{agent.name}}:`, e);
                        agentStatus[agent.name] = false;
                        updateAgentStatusUI(agent.name, false);
                    }}
                }}
                
                // Show overall status
                const onlineCount = Object.values(agentStatus).filter(status => status).length;
                const totalCount = Object.keys(agentStatus).length;
                
                if (onlineCount === totalCount) {{
                    console.log('✅ All agents are online');
                }} else {{
                    console.warn(`⚠️ Only ${{onlineCount}}/${{totalCount}} agents are online`);
                }}
            }}

            function updateAgentStatusUI(agentName, isOnline) {{
                const element = document.getElementById(agentName);
                const dot = element.querySelector('.status-dot');
                
                if (isOnline) {{
                    element.classList.add('online');
                    element.classList.remove('offline');
                    dot.classList.add('online');
                    dot.classList.remove('offline');
                }} else {{
                    element.classList.add('offline');
                    element.classList.remove('online');
                    dot.classList.add('offline');
                    dot.classList.remove('online');
                }}
            }}

            async function runDemo(scenarioKey) {{
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                loading.classList.add('show');
                result.classList.remove('show');
                
                try {{
                    const response = await fetch('/run-demo', {{
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
                        // Handle server errors
                        const errorMsg = `❌ SERVER ERROR (${{response.status}}):\\n\\n${{data.detail || 'Unknown error'}}\\n\\n[HELP] Check that all A2A agents are running and try again.`;
                        resultContent.textContent = errorMsg;
                        result.classList.add('show');
                    }}
                }} catch (error) {{
                    // Handle network errors
                    const errorMsg = `❌ CONNECTION ERROR:\\n\\nFailed to connect to the server.\\nError: ${{error.message}}\\n\\n[HELP] Make sure the web server is running on port 8080.`;
                    resultContent.textContent = errorMsg;
                    result.classList.add('show');
                    console.error('Network error:', error);
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
                
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                loading.classList.add('show');
                result.classList.remove('show');
                
                try {{
                    const response = await fetch('/run-custom-demo', {{
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
                        // Handle server errors
                        const errorMsg = `❌ SERVER ERROR (${{response.status}}):\\n\\n${{data.detail || 'Unknown error'}}\\n\\n[INPUT] Your mission: ${{customMission}}\\n\\n[HELP] Check that all A2A agents are running and try again.`;
                        resultContent.textContent = errorMsg;
                        result.classList.add('show');
                    }}
                }} catch (error) {{
                    // Handle network errors
                    const errorMsg = `❌ CONNECTION ERROR:\\n\\nFailed to connect to the server.\\nError: ${{error.message}}\\n\\n[INPUT] Your mission: ${{customMission}}\\n\\n[HELP] Make sure the web server is running on port 8080.`;
                    resultContent.textContent = errorMsg;
                    result.classList.add('show');
                    console.error('Network error:', error);
                }} finally {{
                    loading.classList.remove('show');
                }}
            }}

            async function testAgentConnections() {{
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                loading.classList.add('show');
                result.classList.remove('show');
                
                try {{
                    const response = await fetch('/test-agents');
                    
                    if (response.ok) {{
                        const data = await response.json();
                        resultContent.textContent = data.result;
                        result.classList.add('show');
                    }} else {{
                        const errorData = await response.json();
                        const errorMsg = `❌ AGENT TEST ERROR (${{response.status}}):\\n\\n${{errorData.detail || 'Unknown error'}}\\n\\n[HELP] Failed to test agent connections.`;
                        resultContent.textContent = errorMsg;
                        result.classList.add('show');
                    }}
                }} catch (error) {{
                    const errorMsg = `❌ CONNECTION ERROR:\\n\\nFailed to test agent connections.\\nError: ${{error.message}}\\n\\n[HELP] Make sure the web server is running on port 8080.`;
                    resultContent.textContent = errorMsg;
                    result.classList.add('show');
                    console.error('Network error:', error);
                }} finally {{
                    loading.classList.remove('show');
                }}
            }}

            function clearResults() {{
                const result = document.getElementById('result');
                result.classList.remove('show');
            }}

            // Check agent status on page load
            window.onload = function() {{
                checkAgentStatus();
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def generate_demo_cards():
    """Generate HTML for demo scenario cards"""
    cards_html = ""
    for key, scenario in DEMO_SCENARIOS.items():
        if key != "custom":  # Skip custom as it's handled separately
            preview = scenario["mission"][:200] + "..." if len(scenario["mission"]) > 200 else scenario["mission"]
            # Add appropriate icon based on project type
            if "website" in key:
                icon = "🌐"
            elif "ecommerce" in key:
                icon = "🛒"
            elif "mobile" in key:
                icon = "📱"
            elif "enterprise" in key:
                icon = "🏢"
            elif "ai" in key:
                icon = "🤖"
            elif "blockchain" in key:
                icon = "⛓️"
            elif "iot" in key:
                icon = "🌐"
            else:
                icon = "📋"
                
            cards_html += f"""
            <div class="demo-card" onclick="runDemo('{key}')">
                <h3>{icon} {scenario["title"]}</h3>
                <p>{scenario["description"]}</p>
                <div class="mission-preview">{preview}</div>
                <button class="btn">🚀 Run Demo</button>
            </div>
            """
    return cards_html

@app.get("/check-agent/{port}")
async def check_agent(port: int):
    """Check if an agent is running on the specified port"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://localhost:{port}/.well-known/agent.json")
            return {"status": "online", "agent_info": response.json()}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Agent on port {port} is not running")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Agent on port {port} is not responding (timeout)")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Agent returned HTTP {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/run-demo")
async def run_demo(request: Request):
    """Run a predefined demo scenario"""
    try:
        data = await request.json()
        scenario_key = data.get("scenario")
        
        if scenario_key not in DEMO_SCENARIOS:
            raise HTTPException(status_code=400, detail="Invalid scenario")
        
        mission = DEMO_SCENARIOS[scenario_key]["mission"]
        result = await execute_a2a_flow(mission)
        
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        # Return error in result format instead of raising HTTP exception
        error_result = f"""❌ DEMO EXECUTION ERROR:

[ERROR] {str(e)}
[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[HELP] This error occurred while trying to execute the demo scenario.
[HELP] Please check that all A2A agents are running and try again."""
        return {"result": error_result}

@app.post("/run-custom-demo")
async def run_custom_demo(request: Request):
    """Run a custom demo with user-provided mission"""
    try:
        data = await request.json()
        mission = data.get("mission", "").strip()
        
        if not mission:
            raise HTTPException(status_code=400, detail="Mission cannot be empty")
        
        result = await execute_a2a_flow(mission)
        
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
    except Exception as e:
        # Return error in result format instead of raising HTTP exception
        error_result = f"""❌ CUSTOM DEMO ERROR:

[ERROR] {str(e)}
[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
[INPUT] Mission: {data.get('mission', 'N/A') if 'data' in locals() else 'N/A'}

[HELP] This error occurred while trying to execute your custom mission.
[HELP] Please check that all A2A agents are running and try again."""
        return {"result": error_result}

@app.get("/test-agents")
async def test_agents():
    """Test individual agent connections"""
    agents = [
        ("Supervisor", "http://localhost:9001"),
        ("Milestone", "http://localhost:9002"),
        ("Task", "http://localhost:9003"),
        ("Resource", "http://localhost:9004")
    ]
    
    result = "[AGENT] CONNECTIVITY TEST\\n\\n"
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as httpx_client:
        for agent_name, agent_url in agents:
            try:
                resolver = A2ACardResolver(httpx_client, agent_url)
                card = await resolver.get_agent_card()
                result += f"[SUCCESS] {agent_name} Agent - {card.description}\\n"
                result += f"          Capabilities: {', '.join(card.capabilities)}\\n\\n"
            except Exception as e:
                result += f"[ERROR] {agent_name} Agent - Connection failed: {str(e)}\\n\\n"
    
    return {"result": result}

@app.get("/projects")
async def list_projects():
    """List all available project folders in a2a_projects directory"""
    try:
        projects_dir = "a2a_projects"
        if not os.path.exists(projects_dir):
            return {"projects": [], "message": "No projects directory found"}
        
        projects = []
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                # Check if it has project files
                project_info = {
                    "name": item,
                    "path": f"/projects/{item}",
                    "files": []
                }
                
                # List files in the project directory
                try:
                    for file in os.listdir(item_path):
                        if file.endswith(('.html', '.md', '.json', '.csv')):
                            project_info["files"].append({
                                "name": file,
                                "url": f"/projects/{item}/{file}",
                                "type": file.split('.')[-1].upper()
                            })
                except PermissionError:
                    continue
                    
                if project_info["files"]:  # Only include if it has viewable files
                    projects.append(project_info)
        
        return {"projects": projects, "count": len(projects)}
    except Exception as e:
        return {"error": str(e), "projects": []}

@app.get("/projects-browser", response_class=HTMLResponse)
async def projects_browser():
    """HTML page to browse generated projects"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>A2A Generated Projects Browser</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
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
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            
            .projects-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            
            .project-card {
                border: 1px solid #e1e1e1;
                border-radius: 10px;
                padding: 20px;
                background: #f9f9f9;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .project-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }
            
            .project-name {
                font-size: 1.3em;
                font-weight: bold;
                color: #333;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }
            
            .project-files {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .file-link {
                display: flex;
                align-items: center;
                padding: 8px 12px;
                background: white;
                border-radius: 5px;
                text-decoration: none;
                color: #333;
                transition: background 0.2s;
                border: 1px solid #e1e1e1;
            }
            
            .file-link:hover {
                background: #f0f0f0;
                border-color: #667eea;
            }
            
            .file-type {
                background: #667eea;
                color: white;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 0.8em;
                margin-right: 10px;
                min-width: 45px;
                text-align: center;
            }
            
            .file-type.html { background: #e74c3c; }
            .file-type.md { background: #3498db; }
            .file-type.json { background: #f39c12; }
            .file-type.csv { background: #27ae60; }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            
            .no-projects {
                text-align: center;
                padding: 40px;
                color: #666;
                background: #f9f9f9;
                border-radius: 10px;
                margin-top: 30px;
            }
            
            .refresh-btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                margin-top: 20px;
                transition: transform 0.2s;
            }
            
            .refresh-btn:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗂️ A2A Generated Projects</h1>
                <p>Browse all projects generated by the A2A Task Management System</p>
                <button class="refresh-btn" onclick="loadProjects()">🔄 Refresh Projects</button>
            </div>
            
            <div id="loading" class="loading">
                <h3>Loading projects...</h3>
            </div>
            
            <div id="projects-container" class="projects-grid" style="display: none;">
            </div>
            
            <div id="no-projects" class="no-projects" style="display: none;">
                <h3>No projects found</h3>
                <p>Run some demos first to generate project files!</p>
                <p><a href="/" style="color: #667eea;">← Back to A2A Demo Interface</a></p>
            </div>
        </div>
        
        <script>
            async function loadProjects() {
                const loading = document.getElementById('loading');
                const container = document.getElementById('projects-container');
                const noProjects = document.getElementById('no-projects');
                
                loading.style.display = 'block';
                container.style.display = 'none';
                noProjects.style.display = 'none';
                
                try {
                    const response = await fetch('/projects');
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    
                    if (data.projects && data.projects.length > 0) {
                        container.innerHTML = '';
                        data.projects.forEach(project => {
                            const projectCard = createProjectCard(project);
                            container.appendChild(projectCard);
                        });
                        container.style.display = 'grid';
                    } else {
                        noProjects.style.display = 'block';
                    }
                } catch (error) {
                    loading.style.display = 'none';
                    noProjects.innerHTML = '<h3>Error loading projects</h3><p>' + error.message + '</p>';
                    noProjects.style.display = 'block';
                }
            }
            
            function createProjectCard(project) {
                const card = document.createElement('div');
                card.className = 'project-card';
                
                const name = document.createElement('div');
                name.className = 'project-name';
                name.textContent = project.name;
                
                const files = document.createElement('div');
                files.className = 'project-files';
                
                project.files.forEach(file => {
                    const link = document.createElement('a');
                    link.className = 'file-link';
                    link.href = file.url;
                    link.target = '_blank';
                    
                    const type = document.createElement('span');
                    type.className = `file-type ${file.type.toLowerCase()}`;
                    type.textContent = file.type;
                    
                    const fileName = document.createElement('span');
                    fileName.textContent = file.name;
                    
                    link.appendChild(type);
                    link.appendChild(fileName);
                    files.appendChild(link);
                });
                
                card.appendChild(name);
                card.appendChild(files);
                return card;
            }
            
            // Load projects on page load
            loadProjects();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

async def check_all_agents_status(httpx_client, log_step, log_error):
    """Check status of all agents before proceeding"""
    agents = [
        ("Milestone", "http://localhost:9002"),
        ("Task", "http://localhost:9003"),
        ("Resource", "http://localhost:9004")
    ]
    
    agent_status = {}
    log_step("🔍 CHECK", "Verifying all agents are available...")
    
    for agent_name, agent_url in agents:
        try:
            resolver = A2ACardResolver(httpx_client, agent_url)
            await resolver.get_agent_card()
            agent_status[agent_name.lower()] = True
            log_step("✅ VERIFY", f"{agent_name} Agent is online")
        except Exception as e:
            agent_status[agent_name.lower()] = False
            log_error("VERIFY", f"{agent_name} Agent is offline: {str(e)}")
    
    return agent_status

def generate_error_response(flow_log, error_message, error_type):
    """Generate formatted error response with flow log"""
    result = "❌ A2A PROTOCOL ERROR LOG:\\n"
    result += "=" * 50 + "\\n\\n"
    
    for log_entry in flow_log:
        result += log_entry + "\\n"
    
    result += "\\n" + "=" * 50 + "\\n"
    result += f"🚨 ERROR DETAILS:\\n\\n"
    result += f"[ERROR_TYPE] {error_type}\\n"
    result += f"[ERROR_MSG] {error_message}\\n\\n"
    
    # Add troubleshooting tips based on error type
    if error_type == "supervisor":
        result += "[SOLUTION] Start the Supervisor Agent:\\n"
        result += "           python -m src.agents.supervisor_agent\\n\\n"
    elif error_type == "timeout":
        result += "[SOLUTION] The agent may be overloaded. Try again in a few seconds.\\n\\n"
    elif error_type == "http":
        result += "[SOLUTION] Check agent logs for HTTP errors.\\n\\n"
    elif error_type == "send":
        result += "[SOLUTION] Check message format and agent compatibility.\\n\\n"
    
    result += "[HELP] Make sure all agents are running:\\n"
    result += "[HELP]    python -m src.agents.supervisor_agent  # Port 9001\\n"
    result += "[HELP]    python -m src.agents.milestone_agent   # Port 9002\\n"
    result += "[HELP]    python -m src.agents.task_agent        # Port 9003\\n"
    result += "[HELP]    python -m src.agents.resource_agent    # Port 9004\\n\\n"
    result += f"[⏰ TIMESTAMP] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return result

async def execute_a2a_flow(mission: str) -> str:
    """Execute the complete A2A flow with the given mission"""
    flow_log = []
    
    def log_step(step, description, details=""):
        timestamp = datetime.now().strftime('%H:%M:%S')
        flow_log.append(f"[{timestamp}] {step}: {description}")
        if details:
            flow_log.append(f"         {details}")
    
    def log_error(step, error_msg, details=""):
        timestamp = datetime.now().strftime('%H:%M:%S')
        flow_log.append(f"[{timestamp}] ❌ {step}: {error_msg}")
        if details:
            flow_log.append(f"         {details}")
    
    try:
        log_step("🎯 INIT", "Starting A2A Protocol Flow")
        log_step("📝 INPUT", f"Mission received: {mission[:100]}{'...' if len(mission) > 100 else ''}")
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as httpx_client:
            # Connect to Supervisor Agent
            log_step("🔗 CONNECT", "Connecting to Supervisor Agent (Port 9001)")
            
            try:
                supervisor_resolver = A2ACardResolver(
                    httpx_client=httpx_client,
                    base_url="http://localhost:9001"
                )
                
                supervisor_card = await supervisor_resolver.get_agent_card()
                supervisor_client = A2AClient(httpx_client, supervisor_card)
                
                log_step("✅ CONNECTED", f"Supervisor Agent: {supervisor_card.description}")
                log_step("🎯 CAPABILITIES", f"Supervisor can: {', '.join(supervisor_card.capabilities)}")
                
            except httpx.ConnectError:
                log_error("CONNECT", "Supervisor Agent not available (Port 9001)")
                return generate_error_response(flow_log, "Supervisor Agent is not running", "supervisor")
            except Exception as e:
                log_error("CONNECT", f"Failed to connect to Supervisor Agent: {str(e)}")
                return generate_error_response(flow_log, f"Supervisor connection error: {str(e)}", "supervisor")
            
            # Create message
            log_step("📦 PREPARE", "Creating A2A message format")
            try:
                message = Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(text=mission))]
                )
                
                request = SendMessageRequest(
                    params=MessageSendParams(message=message)
                )
                
                log_step("🚀 SEND", "Sending mission to Supervisor Agent via A2A protocol")
                log_step("⏳ PROCESS", "Supervisor analyzing mission and coordinating with other agents...")
                
                # Check other agents availability before proceeding
                agent_status = await check_all_agents_status(httpx_client, log_step, log_error)
                
                # This will trigger the full A2A flow internally
                response = await supervisor_client.send_message(request)
                
                # Check if response contains Trello information
                response_text = response.response.parts[0].root.text
                if "[TRELLO]" in response_text:
                    if "Board Created:" in response_text:
                        log_step("🔗 TRELLO", "Trello board and cards created successfully")
                    elif "Integration Failed:" in response_text:
                        log_step("❌ TRELLO", "Trello integration failed - check credentials")
                    elif "Not configured" in response_text:
                        log_step("⚠️ TRELLO", "Trello integration not configured")
                else:
                    log_step("⚠️ TRELLO", "No Trello integration information found")
                
                log_step("📊 INTERNAL", "Supervisor → Milestone Agent (Port 9002) for timeline planning")
                log_step("📊 INTERNAL", "Supervisor → Task Agent (Port 9003) for task breakdown + Trello integration")  
                log_step("📊 INTERNAL", "Supervisor → Resource Agent (Port 9004) for team allocation")
                log_step("🔄 COMPILE", "Supervisor compiling complete project plan with Trello results")
                log_step("✅ COMPLETE", "A2A Protocol flow finished successfully")
                
            except httpx.TimeoutException:
                log_error("TIMEOUT", "Request timed out - Agent may be overloaded")
                return generate_error_response(flow_log, "Request timeout - Please try again", "timeout")
            except httpx.HTTPStatusError as e:
                log_error("HTTP_ERROR", f"HTTP {e.response.status_code}: {e.response.text}")
                return generate_error_response(flow_log, f"HTTP error {e.response.status_code}", "http")
            except Exception as e:
                log_error("SEND", f"Failed to send message: {str(e)}")
                return generate_error_response(flow_log, f"Message sending failed: {str(e)}", "send")
            
            # Format result with flow log
            result = "🔄 A2A PROTOCOL FLOW LOG:\\n"
            result += "=" * 50 + "\\n\\n"
            
            for log_entry in flow_log:
                result += log_entry + "\\n"
            
            result += "\\n" + "=" * 50 + "\\n"
            result += f"📋 FINAL PROJECT PLAN:\\n\\n"
            result += f"[INPUT] MISSION:\\n{mission}\\n\\n"
            result += response.response.parts[0].root.text
            
            # Add summary statistics
            if response.milestones:
                result += f"\\n\\n[📊 RESULTS] Generated {len(response.milestones)} milestones"
                
            if response.task_breakdown:
                result += f"\\n[📊 RESULTS] Generated {len(response.task_breakdown)} detailed tasks"
                
            if response.resource_allocation:
                total_members = response.resource_allocation.get('total_members', 0)
                estimated_cost = response.resource_allocation.get('estimated_cost', 0)
                result += f"\\n[📊 RESULTS] Allocated {total_members} team members"
                result += f"\\n[📊 RESULTS] Estimated cost: ${estimated_cost:,}"
            
            result += f"\\n\\n[⏰ TIMESTAMP] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
    except httpx.ConnectError as e:
        log_error("CONNECTION", f"Cannot connect to agents: {str(e)}")
        return generate_error_response(flow_log, "Agents not available - Connection refused", "connection")
    except httpx.TimeoutException as e:
        log_error("TIMEOUT", f"Request timeout: {str(e)}")
        return generate_error_response(flow_log, "Request timeout - Agents may be overloaded", "timeout")
    except httpx.HTTPStatusError as e:
        log_error("HTTP", f"HTTP error {e.response.status_code}: {e.response.text}")
        return generate_error_response(flow_log, f"HTTP {e.response.status_code} error", "http")
    except KeyError as e:
        log_error("DATA", f"Missing required data: {str(e)}")
        return generate_error_response(flow_log, f"Data format error: {str(e)}", "data")
    except json.JSONDecodeError as e:
        log_error("JSON", f"Invalid JSON response: {str(e)}")
        return generate_error_response(flow_log, "Invalid response format from agent", "json")
    except Exception as e:
        log_error("SYSTEM", f"Unexpected error: {str(e)}")
        return generate_error_response(flow_log, f"System error: {str(e)}", "system")

if __name__ == "__main__":
    print("🌐 Starting A2A Web UI Server...")
    print("📍 Access at: http://localhost:8080")
    print("🎯 Demo scenarios available")
    print("🔧 Make sure A2A agents are running on ports 9001-9004")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        log_level="info"
    )
