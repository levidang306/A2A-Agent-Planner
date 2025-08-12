# A2A Task Management System

A distributed Agent-to-Agent (A2A) protocol implementation for task management with specialized agents for project planning, task breakdown, and resource allocation.

## Project Architecture

The system consists of 4 specialized agents that communicate via the A2A protocol:

- **Supervisor Agent** (Port 9001): Receives missions and coordinates other agents
- **Milestone Agent** (Port 9002): Creates timeline planning and milestone breakdowns
- **Task Agent** (Port 9003): Breaks down milestones into detailed tasks with estimates
- **Resource Agent** (Port 9004): Handles team allocation and resource management

## Quick Start

### 1. Install Dependencies

```powershell
# Create and activate virtual environment (if not already done)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 2. Start All Agents

**Option A: Using VS Code Task (Recommended)**

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run "Tasks: Run Task"
3. Select "Run All A2A Agents"

**Option B: Manual Terminal Commands**
Open 4 separate terminal windows and run:

```powershell
# Terminal 1 - Supervisor Agent
python -m src.agents.supervisor_agent

# Terminal 2 - Milestone Agent
python -m src.agents.milestone_agent

# Terminal 3 - Task Agent
python -m src.agents.task_agent

# Terminal 4 - Resource Agent
python -m src.agents.resource_agent
```

### 3. Test the System

Once all agents are running, test the complete workflow:

```powershell
# Test full system with sample mission
python main.py

# Or test individual agent connections
python main.py test-agents
```

## How It Works

1. **Input**: Send a project mission/requirement to the Supervisor Agent
2. **Milestone Planning**: Supervisor forwards to Milestone Agent for timeline creation
3. **Task Breakdown**: Milestone results go to Task Agent for detailed task creation
4. **Resource Allocation**: Task results go to Resource Agent for team assignment
5. **Output**: Supervisor compiles all results into a comprehensive project plan

## Example Usage

The system can handle complex project requirements like:

```
Create a comprehensive e-commerce platform that allows users to browse products,
add items to cart, process payments, and manage orders. The platform should include
an admin panel for inventory management, user management, and analytics dashboard.
```

And will output:

- 📅 Milestone timeline with deadlines
- 📋 Detailed task breakdown with time estimates
- 👥 Team allocation with required skills
- 💰 Budget and resource estimates

## Agent Endpoints

Each agent exposes these A2A protocol endpoints:

- `GET /.well-known/agent.json` - Agent card with capabilities
- `POST /a2a/send-message` - Send A2A protocol messages
- `GET /health` - Health check endpoint

## Troubleshooting

**Port Conflicts**: If ports 9001-9004 are in use, edit the agent files to change ports

**Connection Errors**: Ensure all 4 agents are running before testing

**Import Errors**: Make sure dependencies are installed: `pip install -r requirements.txt`

## Source Folder Structure

```
📁 A2A Task Management System/
├── 📁 .github/
│   └── copilot-instructions.md         # Copilot workspace instructions
├── 📁 a2a_projects/                    # Generated project outputs
│   ├── 📁 A2A Generated E-commerce App/
│   │   ├── GANTT_CHART.html
│   │   ├── MILESTONES.md
│   │   ├── PROJECT_DATA.json
│   │   ├── PROJECT_OVERVIEW.md
│   │   ├── README.md
│   │   ├── TASKS.csv
│   │   └── TEAM.json
│   └── 📁 E-commerce Mobile App/
│       └── [Similar structure...]
├── 📁 src/                             # Source code
│   ├── 📁 a2a/                         # A2A Protocol Implementation
│   │   ├── ai_service.py               # AI service integration (Gemini)
│   │   ├── client.py                   # A2A communication client
│   │   ├── types.py                    # Message types and data models
│   │   └── __pycache__/
│   ├── 📁 agents/                      # Agent Implementations
│   │   ├── base_agent.py               # Base agent class with common functionality
│   │   ├── milestone_agent.py          # Timeline planning and milestone creation
│   │   ├── resource_agent.py           # Team allocation and resource management
│   │   ├── supervisor_agent.py         # Mission coordination and AI analysis
│   │   ├── supervisor_agent_backup.py  # Backup version
│   │   ├── supervisor_agent_clean.py   # Clean version
│   │   ├── task_agent.py               # Task breakdown and estimation
│   │   ├── task_agent_enterprise.py    # Enterprise version with DI patterns
│   │   └── __pycache__/
│   ├── 📁 config/                      # Configuration Management
│   │   ├── __init__.py
│   │   └── settings.py                 # Environment-based configuration
│   ├── 📁 domain/                      # Domain Models & Business Logic
│   │   ├── __init__.py
│   │   ├── models.py                   # Core business entities
│   │   └── repositories.py             # Repository interfaces
│   ├── 📁 infrastructure/              # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── di_container.py             # Dependency injection container
│   │   └── repositories.py             # Repository implementations
│   ├── 📁 services/                    # Service Layer
│   │   ├── __init__.py
│   │   ├── application_services.py     # Business logic services
│   │   ├── factory.py                  # Service factory
│   │   ├── interfaces.py               # Service contracts
│   │   └── project_services.py         # Project management services
│   └── 📁 tools/                       # Integration Tools
│       ├── __init__.py
│       ├── github_integration.py       # GitHub Issues integration
│       ├── local_project_manager.py    # Local file generation
│       ├── real_trello_integration.py  # Trello API integration
│       ├── team_manager.py             # Team management utilities
│       ├── timeline_generator.py       # Timeline and Gantt chart generation
│       ├── trello_integration.py       # Trello board/card management
│       └── __pycache__/
├── 📄 .env                             # Environment variables
├── 📄 A2A_FLOW_GUIDE.md               # A2A workflow documentation
├── 📄 AI_SETUP.md                     # AI service setup guide
├── 📄 API_DOCUMENTATION.md            # API documentation
├── 📄 ENTERPRISE_ARCHITECTURE.md      # Enterprise patterns documentation
├── 📄 README.md                       # This file
├── 📄 demo_a2a_flow.py                # A2A workflow demonstration
├── 📄 demo_github_integration.py      # GitHub integration demo
├── 📄 enterprise_launcher.py          # Enterprise system launcher
├── 📄 launcher.py                     # System launcher
├── 📄 main.py                         # Main entry point
├── 📄 realtime_tracker.py             # Real-time project tracking
├── 📄 requirements.txt                # Python dependencies
├── 📄 simple_realtime.py              # Simple real-time interface
├── 📄 test_gemini.py                  # Gemini AI testing
├── 📄 test_local_project_manager.py   # Local project manager tests
├── 📄 web_ui_enhanced.py              # Enhanced web interface
├── 📄 web_ui_server.py                # Web UI server
└── 📄 web_ui_tools_integrated.py      # Web UI with tool integration
```

### 🏗️ Architecture Layers

#### **Core A2A Protocol (`src/a2a/`)**

- **`types.py`**: Data models, message types, enums (Priority, MessageType, etc.)
- **`client.py`**: HTTP-based A2A communication client
- **`ai_service.py`**: AI service integration for content analysis

#### **Agent Layer (`src/agents/`)**

- **`base_agent.py`**: FastAPI-based agent foundation with health checks
- **`supervisor_agent.py`**: Mission analysis and workflow coordination
- **`milestone_agent.py`**: Project timeline and milestone planning
- **`task_agent.py`**: Task breakdown with Trello integration
- **`task_agent_enterprise.py`**: Enterprise version with DI patterns
- **`resource_agent.py`**: Team allocation and resource management

#### **Domain Layer (`src/domain/`)**

- **`models.py`**: Core business entities (Project, Task, Milestone, TeamMember)
- **`repositories.py`**: Repository pattern interfaces

#### **Service Layer (`src/services/`)**

- **`interfaces.py`**: Service contracts and abstractions
- **`application_services.py`**: Business logic orchestration
- **`project_services.py`**: Multi-platform project management
- **`factory.py`**: Service creation and dependency injection

#### **Infrastructure (`src/infrastructure/`)**

- **`repositories.py`**: In-memory and database repository implementations
- **`di_container.py`**: Dependency injection container

#### **Integration Tools (`src/tools/`)**

- **`github_integration.py`**: GitHub Issues and project boards
- **`trello_integration.py`**: Trello board and card management
- **`local_project_manager.py`**: Local file generation (CSV, HTML, JSON)
- **`timeline_generator.py`**: Gantt charts and timeline visualization
- **`team_manager.py`**: Team composition and skill management

#### **Configuration (`src/config/`)**

- **`settings.py`**: Environment-based configuration management

### 🚀 Entry Points

- **`main.py`**: Standard A2A workflow execution
- **`enterprise_launcher.py`**: Enterprise system with all patterns
- **`launcher.py`**: Simple system launcher
- **`web_ui_server.py`**: Web-based interface
- **`realtime_tracker.py`**: Real-time project monitoring

### 📊 Generated Outputs (`a2a_projects/`)\*\*

Each project generates:

- **`PROJECT_OVERVIEW.md`**: Executive summary
- **`MILESTONES.md`**: Timeline and milestone details
- **`TASKS.csv`**: Detailed task breakdown
- **`TEAM.json`**: Team allocation and skills
- **`GANTT_CHART.html`**: Interactive timeline visualization
- **`PROJECT_DATA.json`**: Machine-readable project data

## Development

To add new capabilities:

1. **Agents**: Modify logic in `src/agents/`
2. **Message Types**: Update `src/a2a/types.py`
3. **Communication**: Extend `src/a2a/client.py`
4. **Integrations**: Add new tools in `src/tools/`
5. **Business Logic**: Update services in `src/services/`

For enterprise patterns and detailed architecture, see `ENTERPRISE_ARCHITECTURE.md`
