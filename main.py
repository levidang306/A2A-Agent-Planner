"""Main client to test the A2A Task Management System"""
import asyncio
import httpx
import uuid
from src.a2a.types import (
    Message, Role, Part, TextPart, MessageSendParams, SendMessageRequest
)
from src.a2a.client import A2ACardResolver, A2AClient


async def test_a2a_system():
    """Test the complete A2A task management system"""
    
    # Test mission
    mission = """
    Create a comprehensive e-commerce platform that allows users to browse products, 
    add items to cart, process payments, and manage orders. The platform should include 
    an admin panel for inventory management, user management, and analytics dashboard.
    The system needs to be scalable, secure, and mobile-responsive.
    """
    
    async with httpx.AsyncClient() as httpx_client:
        try:
            # Connect to Supervisor Agent
            print("[CONNECT] Connecting to Supervisor Agent...")
            supervisor_resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url="http://localhost:9001"
            )
            
            supervisor_card = await supervisor_resolver.get_agent_card()
            supervisor_client = A2AClient(httpx_client, supervisor_card)
            
            print(f"[SUCCESS] Connected to: {supervisor_card.name}")
            print(f"[INFO] Capabilities: {', '.join(supervisor_card.capabilities)}")
            
            # Send mission to supervisor
            print(f"\n[SEND] Sending mission to Supervisor Agent...")
            print(f"[INPUT] Mission: {mission[:100]}...")
            
            message = Message(
                role=Role.user,
                parts=[Part(root=TextPart(text=mission))]
            )
            
            request = SendMessageRequest(
                params=MessageSendParams(message=message)
            )
            
            print("\n[PROCESS] Processing mission through A2A agent network...")
            response = await supervisor_client.send_message(request)
            
            print("\n" + "="*80)
            print("[RESPONSE] A2A TASK MANAGEMENT SYSTEM RESPONSE")
            print("="*80)
            print(response.response.parts[0].root.text)
            
            # Display structured data if available
            if response.milestones:
                print(f"\n[RESULT] Generated {len(response.milestones)} milestones")
                
            if response.task_breakdown:
                print(f"[RESULT] Generated {len(response.task_breakdown)} detailed tasks")
                
            if response.resource_allocation:
                total_members = response.resource_allocation.get('total_members', 0)
                estimated_cost = response.resource_allocation.get('estimated_cost', 0)
                print(f"[RESULT] Allocated {total_members} team members")
                print(f"[RESULT] Estimated cost: ${estimated_cost:,}")
            
            print("\n[SUCCESS] Mission successfully processed through A2A protocol!")
            
        except httpx.ConnectError as e:
            print(f"[ERROR] Connection error: {e}")
            print("\n[SETUP] Make sure all agents are running:")
            print("[SETUP]    python -m src.agents.supervisor_agent  # Port 9001")
            print("[SETUP]    python -m src.agents.milestone_agent   # Port 9002") 
            print("[SETUP]    python -m src.agents.task_agent        # Port 9003")
            print("[SETUP]    python -m src.agents.resource_agent    # Port 9004")
            
        except Exception as e:
            print(f"[ERROR] Error: {e}")


async def test_individual_agents():
    """Test individual agents separately"""
    agents = [
        ("Supervisor", "http://localhost:9001"),
        ("Milestone", "http://localhost:9002"),
        ("Task", "http://localhost:9003"),
        ("Resource", "http://localhost:9004")
    ]
    
    print("[TEST] Testing individual agent connections...\n")
    
    async with httpx.AsyncClient() as httpx_client:
        for agent_name, agent_url in agents:
            try:
                resolver = A2ACardResolver(httpx_client, agent_url)
                card = await resolver.get_agent_card()
                print(f"[SUCCESS] {agent_name} Agent - {card.description}")
                
            except Exception as e:
                print(f"[ERROR] {agent_name} Agent - Connection failed: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test-agents":
        asyncio.run(test_individual_agents())
    else:
        asyncio.run(test_a2a_system())
