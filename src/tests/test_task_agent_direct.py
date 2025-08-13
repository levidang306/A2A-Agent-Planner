#!/usr/bin/env python3
"""Test the task agent directly with a simple message"""
import asyncio
import httpx
import json
import os
import sys
from dotenv import load_dotenv

# Change to the correct directory
os.chdir(r"d:\AI-research\A2A\agent2agent\a2a_simple\Test")
load_dotenv()

# Add src to path
sys.path.append('src')

from src.a2a.types import Message, Role, Part, TextPart, MessageSendParams, SendMessageRequest

async def test_task_agent():
    """Test task agent directly"""
    print("=" * 60)
    print("TESTING TASK AGENT DIRECTLY")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv('API_KEY_TRELLO')
    api_token = os.getenv('API_TOKEN_TRELLO')
    
    print(f"Trello API Key: {'SET' if api_key else 'NOT SET'}")
    print(f"Trello Token: {'SET' if api_token else 'NOT SET'}")
    
    # Test task agent endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Check if task agent is running
            print(f"\n1. Checking Task Agent status on port 9003...")
            response = await client.get("http://localhost:9003/")
            print(f"   Response: {response.status_code}")
            
            # Get agent card
            print(f"\n2. Getting Task Agent card...")
            card_response = await client.get("http://localhost:9003/.well-known/agent.json")
            if card_response.status_code == 200:
                card_data = card_response.json()
                print(f"   Agent: {card_data.get('name')}")
                print(f"   Capabilities: {card_data.get('capabilities', [])}")
            
            # Send a test message
            print(f"\n3. Sending test message to Task Agent...")
            
            message = Message(
                role=Role.user,
                parts=[Part(root=TextPart(text="Create tasks for e-commerce development with frontend and backend"))]
            )
            
            request_data = SendMessageRequest(
                params=MessageSendParams(message=message)
            )
            
            # Convert to dict for JSON serialization
            request_dict = {
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [
                            {
                                "root": {
                                    "text": "Create tasks for e-commerce development with frontend and backend"
                                }
                            }
                        ]
                    }
                }
            }
            
            print(f"   Sending request to: http://localhost:9003/api/send_message")
            
            response = await client.post(
                "http://localhost:9003/api/send_message",
                json=request_dict,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   Response received! Keys: {list(response_data.keys())}")
                
                # Check if response contains task breakdown
                if 'task_breakdown' in response_data:
                    tasks = response_data['task_breakdown']
                    print(f"   Tasks created: {len(tasks)}")
                    for i, task in enumerate(tasks[:3], 1):  # Show first 3 tasks
                        print(f"     Task {i}: {task.get('title', 'N/A')}")
                
                # Check response text for Trello info
                response_text = response_data.get('response', {}).get('parts', [{}])[0].get('root', {}).get('text', '')
                if 'TRELLO' in response_text.upper():
                    print(f"   ✅ Trello integration detected in response!")
                    # Extract Trello info
                    lines = response_text.split('\n')
                    for line in lines:
                        if 'TRELLO' in line.upper():
                            print(f"     {line.strip()}")
                else:
                    print(f"   ❌ No Trello integration found in response")
                    print(f"   Response preview: {response_text[:200]}...")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Task Agent is not running on port 9003")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_task_agent())
