# A2A Protocol API Documentation

## Overview

This document describes all available APIs in the A2A Task Management System. Each agent exposes standard A2A protocol endpoints.

## 🌐 Agent Endpoints

### All Agents (Ports 9001-9004)

- **Supervisor Agent**: `http://localhost:9001`
- **Milestone Agent**: `http://localhost:9002`
- **Task Agent**: `http://localhost:9003`
- **Resource Agent**: `http://localhost:9004`

## 📋 Standard A2A Endpoints

### 1. Agent Card Discovery

```http
GET /.well-known/agent.json
```

**Purpose**: Get agent capabilities and metadata

**Response Example**:

```json
{
  "name": "Supervisor Agent",
  "version": "1.0.0",
  "description": "Supervisor agent that receives missions and divides work",
  "agent_type": "supervisor",
  "capabilities": [
    "mission_analysis",
    "work_division",
    "project_coordination",
    "delegation"
  ],
  "endpoints": {
    "base_url": "http://localhost:9001",
    "send_message": "http://localhost:9001/api/send_message"
  },
  "contact": {
    "email": "supervisor@taskmanagement.com"
  }
}
```

### 2. Send Message (Core A2A Communication)

```http
POST /api/send_message
```

**Purpose**: Send A2A protocol messages between agents

**Request Body**:

```json
{
  "id": "uuid-string",
  "params": {
    "message": {
      "role": "user",
      "messageId": "uuid-string",
      "parts": [
        {
          "root": {
            "text": "Your message content here"
          }
        }
      ],
      "timestamp": "2025-01-11T10:30:00Z"
    }
  }
}
```

**Response**:

```json
{
  "id": "response-uuid",
  "response": {
    "role": "assistant",
    "messageId": "response-message-id",
    "parts": [
      {
        "root": {
          "text": "Agent response content"
        }
      }
    ],
    "timestamp": "2025-01-11T10:30:05Z"
  },
  "milestones": [...],        // Optional: from Milestone Agent
  "task_breakdown": [...],    // Optional: from Task Agent
  "resource_allocation": {...} // Optional: from Resource Agent
}
```

## 🎯 Agent-Specific Functions

### Supervisor Agent (Port 9001)

**Function**: `analyze_mission()`

- **Input**: Project mission/requirements
- **Output**: Complete project plan with all agent results
- **AI Features**: Smart project analysis if AI API keys configured

**Capabilities**:

- Mission analysis and complexity assessment
- Coordination with other agents
- Final project plan compilation

### Milestone Agent (Port 9002)

**Function**: `create_milestone_plan()`

- **Input**: Project requirements and analysis
- **Output**: Timeline with milestones and deadlines
- **AI Features**: Smart milestone generation with realistic timelines

**Capabilities**:

- Timeline planning
- Milestone creation
- Deadline estimation
- Project phasing

### Task Agent (Port 9003)

**Function**: `analyze_and_breakdown_tasks()`

- **Input**: Milestone plan
- **Output**: Detailed task list with time estimates
- **AI Features**: Intelligent task complexity estimation

**Capabilities**:

- Task breakdown
- Time estimation
- Dependency analysis
- Skill identification

### Resource Agent (Port 9004)

**Function**: `allocate_resources()`

- **Input**: Task breakdown with skill requirements
- **Output**: Team allocation and resource plan
- **AI Features**: Smart team composition recommendations

**Capabilities**:

- Team allocation
- Resource planning
- Skill matching
- Workload balancing
- Capacity planning

## 🔍 Testing API Functions

### 1. Test Individual Agent

```bash
# Test agent connectivity
python main.py test-agents
```

### 2. Test Complete Workflow

```bash
# Test full A2A protocol workflow
python main.py
```

### 3. Manual API Testing with curl

**Get Agent Card**:

```bash
curl -X GET http://localhost:9001/.well-known/agent.json
```

**Send Message**:

```bash
curl -X POST http://localhost:9001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "message": {
        "role": "user",
        "parts": [{"root": {"text": "Create a web application"}}]
      }
    }
  }'
```

## 🧠 AI-Enhanced Functions (When API Keys Configured)

### Smart Project Analysis

- **Function**: `ai_service.analyze_project_requirements()`
- **Input**: Mission text
- **Output**: Detailed analysis with complexity, technologies, risks
- **Provider**: Google Gemini 2.0 Flash

### Intelligent Milestone Generation

- **Function**: `ai_service.generate_smart_milestones()`
- **Input**: Mission + analysis
- **Output**: Realistic milestones with deliverables

### Task Complexity Estimation

- **Function**: `ai_service.estimate_task_complexity()`
- **Input**: Task description + context
- **Output**: Time estimates, difficulty, required skills

## 📊 Response Data Models

### MilestoneData

```json
{
  "name": "string",
  "description": "string",
  "deadline": "YYYY-MM-DD",
  "tasks": [...],
  "priority": "low|medium|high|urgent"
}
```

### TaskData

```json
{
  "title": "string",
  "description": "string",
  "priority": "low|medium|high|urgent",
  "estimated_hours": 16.0,
  "dependencies": ["task1", "task2"],
  "skills_required": ["skill1", "skill2"]
}
```

### ResourceAllocation

```json
{
  "teams": [
    {
      "name": "Development Team",
      "role": "Primary development",
      "members": [...],
      "lead": "Team Lead Name"
    }
  ],
  "total_members": 5,
  "estimated_cost": 150000,
  "timeline": {...},
  "recommendations": [...]
}
```

## 🚀 Usage Examples

### Example 1: Simple Web App

```bash
# Input mission
"Create a simple blog website with user authentication"

# API Flow:
1. POST /api/send_message to Supervisor (9001)
2. Supervisor → Milestone Agent (9002)
3. Supervisor → Task Agent (9003)
4. Supervisor → Resource Agent (9004)
5. Get comprehensive project plan
```

### Example 2: Complex E-commerce Platform

```bash
# Input mission
"Create enterprise e-commerce platform with 10k concurrent users"

# AI-Enhanced Response:
- Complexity: ENTERPRISE
- Duration: 16 weeks
- Team: 8 members
- Technologies: React, Node.js, PostgreSQL, Redis, Docker
- Budget: $200,000+
```

## 🔧 Error Handling

### Common HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid message format)
- `500`: Internal Server Error (agent processing failed)
- `503`: Service Unavailable (agent not running)

### Error Response Format

```json
{
  "detail": "Error description",
  "type": "error_type"
}
```

## 🎯 API Integration Tips

1. **Always check agent availability** with `GET /.well-known/agent.json`
2. **Use proper message format** following A2A protocol
3. **Handle timeouts** (default 30 seconds)
4. **Implement retry logic** for failed requests
5. **Parse structured responses** (milestones, tasks, resources)

## 📞 Support

For API issues:

1. Check if all 4 agents are running on ports 9001-9004
2. Verify message format matches A2A protocol
3. Check logs for detailed error information
4. Test with `python main.py test-agents` first
