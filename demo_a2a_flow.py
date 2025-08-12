"""
🔄 A2A Flow Demo - Minh họa luồng hoạt động thực tế
==================================================

Đây là demo code để hiểu rõ cách A2A protocol hoạt động
"""

import asyncio
import httpx
from datetime import datetime

# Simulate A2A Message Flow
async def demo_a2a_flow():
    """Demo luồng A2A từ đầu đến cuối"""
    
    print("🚀 DEMO A2A PROTOCOL FLOW")
    print("=" * 50)
    
    # Input Mission
    mission = """
    Tạo một ứng dụng e-commerce với các tính năng:
    - Đăng ký/đăng nhập user
    - Danh sách sản phẩm 
    - Giỏ hàng và thanh toán
    - Admin panel quản lý
    - Hỗ trợ 1000 user đồng thời
    """
    
    print(f"📝 INPUT MISSION:")
    print(f"   {mission.strip()}")
    print()
    
    # Step 1: Supervisor Analysis
    print("🎯 STEP 1: SUPERVISOR ANALYSIS")
    print("   → Supervisor nhận mission từ client")
    print("   → Gọi AI service để phân tích")
    print("   → Kết quả AI analysis:")
    
    # Simulate AI Analysis Response
    ai_analysis = {
        "complexity": "complex",
        "estimated_weeks": 10,
        "project_type": "web",
        "recommended_team_size": 4,
        "key_technologies": ["React", "Node.js", "PostgreSQL", "Redis"],
        "required_skills": ["frontend", "backend", "database", "devops"],
        "risk_factors": ["scalability", "payment_security"],
        "budget_category": "medium"
    }
    
    for key, value in ai_analysis.items():
        print(f"     • {key}: {value}")
    print()
    
    # Step 2: Milestone Agent
    print("📅 STEP 2: MILESTONE PLANNING")
    print("   → Supervisor gửi request đến Milestone Agent")
    print("   → URL: POST http://localhost:9002/api/send_message")
    print("   → Message: 'Create milestone plan + AI Analysis'")
    print("   → Milestone Agent response:")
    
    milestones = [
        {"name": "Planning & Research", "deadline": "2025-02-01", "weeks": 2},
        {"name": "System Design", "deadline": "2025-02-15", "weeks": 2},
        {"name": "Backend Development", "deadline": "2025-03-15", "weeks": 4},
        {"name": "Frontend Development", "deadline": "2025-03-29", "weeks": 2},
        {"name": "Testing & Launch", "deadline": "2025-04-12", "weeks": 2}
    ]
    
    for i, milestone in enumerate(milestones, 1):
        print(f"     M{i}. {milestone['name']} (Deadline: {milestone['deadline']})")
    print()
    
    # Step 3: Task Agent  
    print("📋 STEP 3: TASK BREAKDOWN")
    print("   → Supervisor gửi milestones đến Task Agent")
    print("   → URL: POST http://localhost:9003/api/send_message")
    print("   → Task Agent phân tích và tạo detailed tasks:")
    
    tasks = [
        {"title": "Requirements Gathering", "hours": 16, "skills": ["business_analysis"]},
        {"title": "Database Design", "hours": 20, "skills": ["database_design"]},
        {"title": "Backend API Development", "hours": 40, "skills": ["backend_development"]},
        {"title": "Frontend UI Development", "hours": 32, "skills": ["frontend_development"]},
        {"title": "Payment Integration", "hours": 24, "skills": ["payment_systems"]},
        {"title": "Testing & QA", "hours": 20, "skills": ["testing"]},
        {"title": "Deployment Setup", "hours": 12, "skills": ["devops"]}
    ]
    
    total_hours = 0
    for i, task in enumerate(tasks, 1):
        print(f"     T{i}. {task['title']} ({task['hours']}h) - {', '.join(task['skills'])}")
        total_hours += task['hours']
    
    print(f"     → Total: {total_hours} hours ({total_hours/40:.1f} weeks)")
    print()
    
    # Step 4: Resource Agent
    print("👥 STEP 4: RESOURCE ALLOCATION")
    print("   → Supervisor gửi task breakdown đến Resource Agent")
    print("   → URL: POST http://localhost:9004/api/send_message")
    print("   → Resource Agent phân bổ team:")
    
    team_allocation = {
        "teams": [
            {
                "name": "Core Development Team",
                "members": [
                    {"name": "Alice (Senior)", "skills": ["backend", "architecture"]},
                    {"name": "Bob (Mid)", "skills": ["frontend", "react"]},
                    {"name": "Carol (Mid)", "skills": ["database", "sql"]}
                ]
            },
            {
                "name": "QA & DevOps Team", 
                "members": [
                    {"name": "David (Specialist)", "skills": ["testing", "automation"]},
                    {"name": "Eva (Specialist)", "skills": ["devops", "deployment"]}
                ]
            }
        ],
        "total_cost": 85000,
        "duration": "10 weeks"
    }
    
    for team in team_allocation["teams"]:
        print(f"     🏗️ {team['name']}:")
        for member in team["members"]:
            print(f"        • {member['name']} - {', '.join(member['skills'])}")
    
    print(f"     💰 Estimated Cost: ${team_allocation['total_cost']:,}")
    print(f"     ⏱️ Duration: {team_allocation['duration']}")
    print()
    
    # Step 5: Final Response
    print("📊 STEP 5: FINAL PROJECT PLAN")
    print("   → Supervisor tổng hợp tất cả responses")
    print("   → Tạo comprehensive project plan")
    print("   → Trả response về client với:")
    print("     • AI Analysis results")
    print("     • Milestone timeline")  
    print("     • Detailed task breakdown")
    print("     • Team allocation plan")
    print()
    
    print("✅ A2A FLOW COMPLETE!")
    print("   Client nhận được complete project plan từ 4 specialized agents")


# Demo Message Format
def demo_message_format():
    """Demo format của A2A messages"""
    
    print("\n🔗 A2A MESSAGE FORMAT DEMO")
    print("=" * 50)
    
    # Request Message
    request_message = {
        "id": "msg-123",
        "params": {
            "message": {
                "role": "user",
                "messageId": "user-msg-456", 
                "parts": [
                    {
                        "root": {
                            "text": "Create milestone plan for e-commerce project"
                        }
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    }
    
    print("📤 REQUEST FORMAT (Client → Agent):")
    print("```json")
    import json
    print(json.dumps(request_message, indent=2))
    print("```")
    
    # Response Message
    response_message = {
        "id": "response-789",
        "response": {
            "role": "assistant",
            "messageId": "agent-response-101",
            "parts": [
                {
                    "root": {
                        "text": "[MILESTONES] Created 5 milestones for e-commerce project..."
                    }
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        },
        "milestones": [
            {
                "name": "Planning Phase",
                "deadline": "2025-02-01",
                "priority": "high"
            }
        ]
    }
    
    print("\n📥 RESPONSE FORMAT (Agent → Client):")
    print("```json") 
    print(json.dumps(response_message, indent=2))
    print("```")


# Demo Agent Discovery
async def demo_agent_discovery():
    """Demo cách agents discover nhau"""
    
    print("\n🔍 AGENT DISCOVERY DEMO")
    print("=" * 50)
    
    agents = [
        ("Supervisor", "http://localhost:9001"),
        ("Milestone", "http://localhost:9002"),
        ("Task", "http://localhost:9003"), 
        ("Resource", "http://localhost:9004")
    ]
    
    print("🎯 Agent Discovery Process:")
    print("   1. Agent startup → Register endpoints")
    print("   2. Other agents → Query /.well-known/agent.json")
    print("   3. Discover capabilities and endpoints")
    print()
    
    for agent_name, url in agents:
        print(f"🤖 {agent_name} Agent:")
        print(f"   URL: {url}")
        print(f"   Discovery: GET {url}/.well-known/agent.json")
        print(f"   Message: POST {url}/api/send_message")
        print()


# Demo Error Handling  
def demo_error_handling():
    """Demo cách xử lý lỗi trong A2A"""
    
    print("\n⚠️ ERROR HANDLING DEMO")
    print("=" * 50)
    
    scenarios = [
        {
            "error": "Agent không khả dụng",
            "handling": "Timeout → Retry → Fallback logic"
        },
        {
            "error": "AI API key invalid", 
            "handling": "AI service fails → Use rule-based analysis"
        },
        {
            "error": "Invalid message format",
            "handling": "Pydantic validation → Return 400 error"
        },
        {
            "error": "Agent processing error",
            "handling": "Try-catch → Return 500 with details"
        }
    ]
    
    for scenario in scenarios:
        print(f"❌ {scenario['error']}")
        print(f"   → {scenario['handling']}")
        print()


if __name__ == "__main__":
    print("🚀 A2A PROTOCOL FLOW DEMO")
    print("========================")
    
    # Run async demo
    asyncio.run(demo_a2a_flow())
    
    # Show message formats
    demo_message_format()
    
    # Show discovery process
    asyncio.run(demo_agent_discovery())
    
    # Show error handling
    demo_error_handling()
    
    print("\n📚 Để hiểu rõ hơn:")
    print("   1. Đọc A2A_FLOW_GUIDE.md để hiểu chi tiết")
    print("   2. Chạy 'python main.py test-agents' để test") 
    print("   3. Chạy 'python main.py' để test complete flow")
    print("   4. Check API_DOCUMENTATION.md cho API details")
