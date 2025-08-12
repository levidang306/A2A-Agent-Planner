# 🔄 A2A Protocol Flow Guide - Chi tiết luồng hoạt động

## 📖 Tổng quan A2A Protocol

**A2A (Agent-to-Agent)** là giao thức giao tiếp giữa các agent độc lập. Mỗi agent chuyên về một lĩnh vực cụ thể và có thể giao tiếp với nhau thông qua HTTP API.

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Supervisor     │    │   Milestone     │    │     Task        │    │   Resource      │
│   Agent         │    │    Agent        │    │    Agent        │    │    Agent        │
│  (Port 9001)    │    │  (Port 9002)    │    │  (Port 9003)    │    │  (Port 9004)    │
│                 │    │                 │    │                 │    │                 │
│ • Điều phối     │    │ • Lập timeline  │    │ • Chi tiết task │    │ • Phân bổ team  │
│ • Phân tích AI  │    │ • Milestone     │    │ • Ước tính giờ  │    │ • Tìm skill     │
│ • Tổng hợp      │    │ • Deadline      │    │ • Dependencies  │    │ • Chi phí       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       ↑                       ↑                       ↑
         │                       │                       │                       │
         └───────────────────────┼───────────────────────┼───────────────────────┘
                                 │                       │
                                 └───────────────────────┘
```

## 🚀 Flow hoạt động chi tiết

### 🎯 Bước 1: Khởi tạo Mission

```
[CLIENT] → [SUPERVISOR AGENT]
POST /api/send_message
{
  "params": {
    "message": {
      "role": "user",
      "parts": [{"root": {"text": "Tạo platform e-commerce..."}}]
    }
  }
}
```

### 🔍 Bước 2: Phân tích Mission (AI-Powered)

```python
# Trong SupervisorAgent.analyze_mission()
try:
    ai_analysis = await ai_service.analyze_project_requirements(mission)

    # Kết quả AI analysis:
    {
        "complexity": "complex",
        "estimated_weeks": 12,
        "project_type": "web",
        "recommended_team_size": 5,
        "key_technologies": ["React", "Node.js", "PostgreSQL"],
        "required_skills": ["frontend", "backend", "database"],
        "risk_factors": ["scalability", "security"],
        "budget_category": "large"
    }
except:
    # Fallback logic nếu AI không khả dụng
```

### 📅 Bước 3: Tạo Timeline & Milestones

```
[SUPERVISOR] → [MILESTONE AGENT]
POST http://localhost:9002/api/send_message
{
  "params": {
    "message": {
      "text": "Create milestone plan for: [MISSION]\n\nMission Analysis: [AI_ANALYSIS]"
    }
  }
}

# Milestone Agent xử lý:
milestone_agent.create_milestone_plan() →
{
  "milestones": [
    {
      "name": "Planning & Research",
      "deadline": "2025-01-25",
      "duration_weeks": 2
    },
    {
      "name": "Development Phase",
      "deadline": "2025-03-01",
      "duration_weeks": 6
    }
  ]
}
```

### 📋 Bước 4: Chi tiết Task Breakdown

```
[SUPERVISOR] → [TASK AGENT]
POST http://localhost:9003/api/send_message
{
  "params": {
    "message": {
      "text": "Break down milestones into detailed tasks:\n[MILESTONE_RESPONSE]"
    },
    "milestone_data": {...}
  }
}

# Task Agent xử lý:
task_agent.analyze_and_breakdown_tasks() →
{
  "task_breakdown": [
    {
      "title": "Backend API Development",
      "estimated_hours": 40.0,
      "skills_required": ["backend_development", "api_design"],
      "dependencies": ["Database Design"]
    },
    {
      "title": "Frontend Development",
      "estimated_hours": 32.0,
      "skills_required": ["frontend_development", "react"]
    }
  ]
}
```

### 👥 Bước 5: Phân bổ Resource & Team

```
[SUPERVISOR] → [RESOURCE AGENT]
POST http://localhost:9004/api/send_message
{
  "params": {
    "message": {
      "text": "Allocate resources for task breakdown:\n[TASK_RESPONSE]"
    }
  }
}

# Resource Agent xử lý:
resource_agent.allocate_resources() →
{
  "resource_allocation": {
    "teams": [
      {
        "name": "Core Development Team",
        "members": [
          {"name": "Alice Johnson", "skills": ["backend", "architecture"]},
          {"name": "Bob Chen", "skills": ["frontend", "react"]}
        ],
        "lead": "Alice Johnson"
      }
    ],
    "total_members": 5,
    "estimated_cost": 150000
  }
}
```

### 📊 Bước 6: Tổng hợp Project Plan

```python
# Supervisor Agent tổng hợp tất cả
final_response = supervisor.compile_project_plan(
    mission_analysis,    # Từ AI
    milestone_response,  # Từ Milestone Agent
    task_response,      # Từ Task Agent
    resource_response   # Từ Resource Agent
)

# Trả về client
return MessageResponse(
    response=final_response,
    milestones=milestone_response.milestones,
    task_breakdown=task_response.task_breakdown,
    resource_allocation=resource_response.resource_allocation
)
```

## 🔗 Chi tiết Communication Protocol

### A2A Message Format

```json
{
  "id": "uuid",
  "params": {
    "message": {
      "role": "user|assistant|system",
      "messageId": "uuid",
      "parts": [
        {
          "root": {
            "text": "Message content"
          }
        }
      ],
      "timestamp": "ISO-8601"
    },
    "task_data": {...},        // Optional
    "milestone_data": {...},   // Optional
    "resource_request": {...}  // Optional
  }
}
```

### Agent Discovery Protocol

```
GET /.well-known/agent.json
→ Trả về AgentCard với capabilities và endpoints
```

## 🧠 AI Enhancement Flow

### Khi có Google AI API Key:

```
Mission Input
    ↓
[AI Analysis] ← Google Gemini 2.0 Flash
    ↓
Smart Project Requirements
    ↓
[AI Milestones] ← Intelligent Timeline
    ↓
[AI Tasks] ← Complexity Estimation
    ↓
[AI Resources] ← Optimal Team Suggestions
```

### Khi không có AI API Key:

```
Mission Input
    ↓
[Fallback Logic] ← Rule-based Analysis
    ↓
Basic Project Requirements
    ↓
Standard Milestones
    ↓
Template Tasks
    ↓
Default Resources
```

## 🔄 Sequence Diagram

```
Client          Supervisor       Milestone        Task           Resource
  │                 │               │              │                │
  │─────Mission─────│               │              │                │
  │                 │               │              │                │
  │                 │──AI Analysis──│              │                │
  │                 │               │              │                │
  │                 │───Timeline────→│              │                │
  │                 │←──Milestones──│              │                │
  │                 │                              │                │
  │                 │───Task Breakdown─────────────→│                │
  │                 │←──Detailed Tasks─────────────│                │
  │                 │                                               │
  │                 │───Resource Allocation─────────────────────────→│
  │                 │←──Team & Budget───────────────────────────────│
  │                 │                                               │
  │←─Project Plan───│                                               │
```

## 🛠️ Cách test từng bước

### 1. Test Agent Discovery

```bash
curl http://localhost:9001/.well-known/agent.json
curl http://localhost:9002/.well-known/agent.json
curl http://localhost:9003/.well-known/agent.json
curl http://localhost:9004/.well-known/agent.json
```

### 2. Test Individual Agent

```bash
# Test Supervisor only
curl -X POST http://localhost:9001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"params": {"message": {"role": "user", "parts": [{"root": {"text": "Simple web app"}}]}}}'
```

### 3. Test Complete Flow

```bash
python main.py
```

## 🎯 Key Features của A2A Protocol

### 1. **Độc lập (Independence)**

- Mỗi agent chạy trên port riêng
- Có thể restart từng agent mà không ảnh hưởng khác

### 2. **Mở rộng (Scalability)**

- Thêm agent mới dễ dàng
- Modify logic từng agent độc lập

### 3. **Fault Tolerance**

- Nếu 1 agent lỗi, Supervisor có fallback logic
- AI service có fallback khi API không khả dụng

### 4. **Standard Protocol**

- Message format chuẩn
- Discovery mechanism thống nhất
- Error handling nhất quán

## 🔍 Debug Flow

### Check Agent Status:

```bash
# Test connectivity
python main.py test-agents

# Check individual ports
curl http://localhost:9001/health
curl http://localhost:9002/health
curl http://localhost:9003/health
curl http://localhost:9004/health
```

### Log Analysis:

```bash
# Check terminal outputs của từng agent
# Look for [ERROR], [WARNING], [SUCCESS] prefixes
```

## 💡 Best Practices

1. **Luôn start đủ 4 agents** trước khi test
2. **Check AI configuration** trong .env file
3. **Monitor logs** để debug issues
4. **Test individual agents** trước khi test complete flow
5. **Use structured data** thay vì plain text khi có thể

## 🚀 Next Steps

Để mở rộng hệ thống, bạn có thể:

- Thêm **Planning Agent** cho detailed planning
- Thêm **QA Agent** cho testing strategy
- Thêm **DevOps Agent** cho deployment planning
- Implement **Database storage** cho persistence
- Add **Web UI** cho easier interaction

Hiểu flow này chưa? Bạn muốn tôi giải thích chi tiết phần nào?
