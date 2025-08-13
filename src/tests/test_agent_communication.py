#!/usr/bin/env python3
"""
Test agent communication
"""
import asyncio
import httpx
import sys
import os

# Add src to path
sys.path.append('src')

async def test_agent_communication():
    print("=" * 60)
    print("TESTING A2A AGENT COMMUNICATION")
    print("=" * 60)
    
    agents = [
        ("Supervisor", "http://localhost:9001"),
        ("Milestone", "http://localhost:9002"),
        ("Task", "http://localhost:9003"),
        ("Resource", "http://localhost:9004")
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, url in agents:
            try:
                print(f"\n🔍 Testing {name} Agent ({url})...")
                
                # Test basic connectivity
                response = await client.get(f"{url}/")
                print(f"   ✅ Basic connection: {response.status_code}")
                
                # Test agent card
                card_response = await client.get(f"{url}/.well-known/agent.json")
                if card_response.status_code == 200:
                    card_data = card_response.json()
                    print(f"   ✅ Agent card: {card_data.get('name')}")
                    print(f"   📋 Capabilities: {len(card_data.get('capabilities', []))} items")
                else:
                    print(f"   ❌ Agent card failed: {card_response.status_code}")
                    
            except httpx.ConnectError:
                print(f"   ❌ {name} Agent not running or not accessible")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING SUPERVISOR → TASK AGENT COMMUNICATION")
    print("=" * 60)
    
    # Test direct communication from Supervisor to Task Agent
    try:
        from src.a2a.types import Message, Role, Part, TextPart, MessageSendParams, SendMessageRequest
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test message to Task Agent
            task_message = {
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [
                            {
                                "root": {
                                    "text": "Create tasks for a simple website project with homepage, about page, and contact form"
                                }
                            }
                        ]
                    }
                }
            }
            
            print("🚀 Sending test message to Task Agent...")
            response = await client.post(
                "http://localhost:9003/api/send_message",
                json=task_message,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", {}).get("parts", [{}])[0].get("root", {}).get("text", "")
                print("✅ Task Agent responded successfully!")
                
                # Check for Trello integration
                if "[TRELLO]" in response_text:
                    print("🔗 Trello integration detected in response")
                    if "Board Created:" in response_text:
                        print("   ✅ Trello board created successfully")
                    elif "Integration Failed:" in response_text:
                        print("   ❌ Trello integration failed")
                    elif "disabled" in response_text.lower():
                        print("   ⚠️ Trello integration disabled")
                else:
                    print("⚠️ No Trello integration information found")
                    
                print(f"\n📝 Response preview: {response_text[:200]}...")
            else:
                print(f"❌ Task Agent communication failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing Task Agent communication: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_communication())
