#!/usr/bin/env python3
"""Test web UI supervisor connection specifically"""

import asyncio
import httpx
from src.a2a.client import A2ACardResolver, A2AClient
from src.a2a.types import SendMessageRequest, MessageSendParams, Message, Role, Part, TextPart

async def test_web_ui_flow():
    """Test the exact same flow as the web UI"""
    
    mission = "Create an e-commerce platform with React frontend and Node.js backend"
    flow_log = []
    
    def log_step(phase, details):
        entry = f"[{phase}] {details}"
        flow_log.append(entry)
        print(entry)
    
    def log_error(phase, details):
        entry = f"[ERROR-{phase}] {details}"
        flow_log.append(entry)
        print(entry)
    
    print("Testing Web UI Flow...")
    
    try:
        log_step("🎯 INIT", "Starting A2A Protocol Flow")
        log_step("📝 INPUT", f"Mission received: {mission[:100]}{'...' if len(mission) > 100 else ''}")
        
        # Use same timeout as web UI
        async with httpx.AsyncClient(timeout=30.0) as httpx_client:
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
                return
            except Exception as e:
                log_error("CONNECT", f"Failed to connect to Supervisor Agent: {str(e)}")
                return
            
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
                
                # Check other agents availability (same as web UI)
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
                
                # This will trigger the full A2A flow internally
                print("\n🔥 CRITICAL: About to send message to supervisor...")
                response = await supervisor_client.send_message(request)
                print("🎉 SUCCESS: Message sent successfully!")
                
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
                
                log_step("✅ COMPLETE", "A2A Protocol flow finished successfully")
                print(f"\nResponse preview: {response_text[:200]}...")
                
            except httpx.TimeoutException as e:
                log_error("TIMEOUT", f"Request timed out: {str(e)}")
            except httpx.HTTPStatusError as e:
                log_error("HTTP_ERROR", f"HTTP {e.response.status_code}: {e.response.text}")
            except Exception as e:
                log_error("SEND", f"Failed to send message: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        log_error("GENERAL", f"Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_web_ui_flow())
