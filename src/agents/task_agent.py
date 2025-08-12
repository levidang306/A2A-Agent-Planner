"""Task Agent - Breaks down milestones into detailed tasks with estimates"""
from typing import List, Dict, Any, Optional
import uuid
import os
import logging
from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType, TaskData, Priority
)
from .base_agent import BaseAgent
from ..tools.trello_integration import TrelloIntegration

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.getenv('TASK_PORT', '9003'))
        super().__init__("Task", AgentType.task, port)
        
        # Initialize Trello integration
        self.trello_api_key = os.getenv('API_KEY_TRELLO')
        self.trello_api_token = os.getenv('API_TOKEN_TRELLO')
        print(f"[INIT] Trello API Key: {'Configured' if self.trello_api_key else 'Missing'}")
        print(f"[INIT] Trello API Token: {'Configured' if self.trello_api_token else 'Missing'}")
        self.trello_enabled = bool(self.trello_api_key and self.trello_api_token)
        
        if self.trello_enabled:
            self.trello = TrelloIntegration(self.trello_api_key, self.trello_api_token)
            logger.info("Task Agent initialized with Trello integration")
            print("[INIT] ✅ Trello integration enabled")
        else:
            self.trello = None
            logger.warning("Task Agent initialized without Trello integration (missing credentials)")
            print("[INIT] ❌ Trello integration disabled - missing credentials")
        
        # Store current project board ID for task creation
        self.current_board_id = None
        self.task_lists = {}
        
    def get_agent_card(self) -> AgentCard:
        capabilities = [
            "task_breakdown",
            "time_estimation",
            "dependency_analysis",
            "skill_identification"
        ]
        
        # Add Trello capabilities if enabled
        if self.trello_enabled:
            capabilities.extend([
                "trello_board_creation",
                "trello_task_cards",
                "trello_list_management",
                "automatic_task_tracking"
            ])
        
        return AgentCard(
            name="Task Agent",
            version="2.0.0",
            description="Enhanced task agent with Trello integration for task breakdown and management",
            agent_type=AgentType.task,
            capabilities=capabilities,
            endpoints={
                "base_url": f"http://localhost:{self.port}",
                "send_message": f"http://localhost:{self.port}/api/send_message"
            },
            contact={
                "email": "task@taskmanagement.com"
            }
        )
    
    async def process_message(self, request: SendMessageRequest) -> MessageResponse:
        """Process task breakdown request and create Trello cards"""
        print("[TASK] ======= PROCESSING MESSAGE =======")
        
        message = request.params.message
        content = message.parts[0].root.text
        milestone_data = getattr(request.params, 'milestone_data', None)
        
        print(f"[TASK] Content received: {content[:100]}...")
        print(f"[TASK] Trello enabled: {self.trello_enabled}")
        
        logger.info("Processing task breakdown request")
        
        # Analyze content for task breakdown
        task_breakdown = self.analyze_and_breakdown_tasks(content, milestone_data)
        print(f"[TASK] Generated {len(task_breakdown)} tasks")
        
        # Create Trello board and cards if enabled
        trello_results = None
        print(f"[TASK] Analyzing content for task breakdown: {content[:50]}...")
        
        if self.trello_enabled:
            print("[TASK] 🔄 Starting Trello integration...")
            trello_results = await self.create_trello_project(content, task_breakdown)
            print(f"[TASK] Trello results: {trello_results}")
        else:
            print("[TASK] ❌ Trello integration disabled")
            
        print(f"[TASK] Trello content: {content}")
        print(f"[TASK] Trello task_breakdown: {len(task_breakdown)} tasks")
        print(f"[TASK] Trello results: {trello_results}")
        # Generate response with Trello integration info
        response_text = self.format_task_response(task_breakdown, trello_results)
        
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(response_text),
            task_breakdown=task_breakdown
        )
    
    def analyze_and_breakdown_tasks(self, content: str, milestone_data=None) -> List[TaskData]:
        """Analyze content and break down into specific tasks"""
        tasks = []
        
        # Extract task categories from content
        content_lower = content.lower()
        
        # Planning & Research Tasks
        if "planning" in content_lower or "research" in content_lower:
            tasks.extend(self.get_planning_tasks())
        
        # Design Tasks
        if "design" in content_lower or "architecture" in content_lower:
            tasks.extend(self.get_design_tasks())
        
        # Development Tasks
        if "development" in content_lower or "implementation" in content_lower:
            tasks.extend(self.get_development_tasks())
        
        # Testing Tasks
        if "testing" in content_lower or "qa" in content_lower:
            tasks.extend(self.get_testing_tasks())
        
        # Deployment Tasks
        if "deployment" in content_lower or "launch" in content_lower:
            tasks.extend(self.get_deployment_tasks())
        
        return tasks
    
    def get_planning_tasks(self) -> List[TaskData]:
        """Generate planning and research tasks"""
        return [
            TaskData(
                title="Requirements Gathering",
                description="Collect and document project requirements from stakeholders",
                priority=Priority.high,
                estimated_hours=16.0,
                skills_required=["business_analysis", "communication"],
                dependencies=[]
            ),
            TaskData(
                title="Market Research",
                description="Research market trends, competitors, and user needs",
                priority=Priority.medium,
                estimated_hours=12.0,
                skills_required=["research", "analysis"],
                dependencies=[]
            ),
            TaskData(
                title="Technical Feasibility Study",
                description="Assess technical requirements and constraints",
                priority=Priority.high,
                estimated_hours=8.0,
                skills_required=["technical_analysis", "architecture"],
                dependencies=["Requirements Gathering"]
            )
        ]
    
    def get_design_tasks(self) -> List[TaskData]:
        """Generate design and architecture tasks"""
        return [
            TaskData(
                title="System Architecture Design",
                description="Design overall system architecture and component interactions",
                priority=Priority.high,
                estimated_hours=24.0,
                skills_required=["system_design", "architecture"],
                dependencies=["Technical Feasibility Study"]
            ),
            TaskData(
                title="Database Design",
                description="Design database schema and data models",
                priority=Priority.high,
                estimated_hours=16.0,
                skills_required=["database_design", "data_modeling"],
                dependencies=["System Architecture Design"]
            ),
            TaskData(
                title="UI/UX Design",
                description="Create user interface mockups and user experience flows",
                priority=Priority.medium,
                estimated_hours=20.0,
                skills_required=["ui_design", "ux_design"],
                dependencies=["Requirements Gathering"]
            )
        ]
    
    def get_development_tasks(self) -> List[TaskData]:
        """Generate development tasks"""
        return [
            TaskData(
                title="Backend API Development",
                description="Develop core backend APIs and business logic",
                priority=Priority.high,
                estimated_hours=40.0,
                skills_required=["backend_development", "api_design"],
                dependencies=["Database Design", "System Architecture Design"]
            ),
            TaskData(
                title="Frontend Development",
                description="Implement user interface and frontend functionality",
                priority=Priority.high,
                estimated_hours=32.0,
                skills_required=["frontend_development", "javascript"],
                dependencies=["UI/UX Design", "Backend API Development"]
            ),
            TaskData(
                title="Database Implementation",
                description="Set up database and implement data access layer",
                priority=Priority.medium,
                estimated_hours=16.0,
                skills_required=["database_administration", "sql"],
                dependencies=["Database Design"]
            )
        ]
    
    def get_testing_tasks(self) -> List[TaskData]:
        """Generate testing tasks"""
        return [
            TaskData(
                title="Unit Testing",
                description="Write and execute unit tests for all components",
                priority=Priority.high,
                estimated_hours=24.0,
                skills_required=["testing", "test_automation"],
                dependencies=["Backend API Development", "Frontend Development"]
            ),
            TaskData(
                title="Integration Testing",
                description="Test integration between different system components",
                priority=Priority.high,
                estimated_hours=16.0,
                skills_required=["integration_testing", "testing"],
                dependencies=["Unit Testing"]
            ),
            TaskData(
                title="User Acceptance Testing",
                description="Conduct UAT with stakeholders and end users",
                priority=Priority.medium,
                estimated_hours=12.0,
                skills_required=["uat_coordination", "communication"],
                dependencies=["Integration Testing"]
            )
        ]
    
    def get_deployment_tasks(self) -> List[TaskData]:
        """Generate deployment tasks"""
        return [
            TaskData(
                title="Production Environment Setup",
                description="Set up production infrastructure and deployment pipeline",
                priority=Priority.high,
                estimated_hours=16.0,
                skills_required=["devops", "infrastructure"],
                dependencies=["Integration Testing"]
            ),
            TaskData(
                title="Deployment & Go-Live",
                description="Deploy application to production and monitor launch",
                priority=Priority.urgent,
                estimated_hours=8.0,
                skills_required=["deployment", "monitoring"],
                dependencies=["Production Environment Setup", "User Acceptance Testing"]
            ),
            TaskData(
                title="Post-Launch Support",
                description="Monitor system performance and provide immediate support",
                priority=Priority.high,
                estimated_hours=16.0,
                skills_required=["support", "monitoring"],
                dependencies=["Deployment & Go-Live"]
            )
        ]
    
    async def create_trello_project(self, project_description: str, tasks: List[TaskData]) -> Optional[Dict[str, Any]]:
        """Create Trello board and cards for the project"""
        if not self.trello:
            return None
        
        try:
            logger.info("Creating Trello board for task management")
            
            # Create project board
            project_name = f"A2A Project - {project_description[:50]}..."
            board_id = self.trello.create_board(project_name)
            
            if not board_id:
                logger.error("Failed to create Trello board")
                return {"error": "Failed to create Trello board"}
            
            self.current_board_id = board_id
            
            # Get default lists on the board
            lists = self.trello.get_lists_on_board(board_id)
            if not lists:
                logger.error("Failed to get board lists")
                return {"error": "Failed to get board lists"}
            
            # Map lists by name for task organization
            list_mapping = {}
            for lst in lists:
                list_mapping[lst['name']] = lst['id']
            
            # Default Trello board has "To Do", "Doing", "Done" lists
            default_list_id = lists[0]['id']  # Use first list as default
            
            # Create cards for each task
            created_cards = []
            for task in tasks:
                # Determine appropriate list based on task priority
                target_list_id = self._get_target_list_id(task, list_mapping, default_list_id)
                
                # Create task description with details
                card_description = f"""
**Description:** {task.description}

**Estimated Hours:** {task.estimated_hours}
**Priority:** {task.priority.value.upper()}
**Skills Required:** {', '.join(task.skills_required)}

**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}

*Generated by A2A Task Agent*
                """.strip()
                
                # Create the card
                card_id = self.trello.create_card(
                    list_id=target_list_id,
                    card_name=task.title,
                    description=card_description
                )
                
                if card_id:
                    created_cards.append({
                        "task_title": task.title,
                        "card_id": card_id,
                        "estimated_hours": task.estimated_hours,
                        "priority": task.priority.value
                    })
                    logger.info(f"Created Trello card for task: {task.title}")
                else:
                    logger.warning(f"Failed to create Trello card for task: {task.title}")
            
            trello_results = {
                "board_id": board_id,
                "board_name": project_name,
                "board_url": f"https://trello.com/b/{board_id}",
                "cards_created": len(created_cards),
                "total_tasks": len(tasks),
                "created_cards": created_cards,
                "lists_available": [{"name": lst['name'], "id": lst['id']} for lst in lists]
            }
            
            logger.info(f"Successfully created Trello project with {len(created_cards)} task cards")
            return trello_results
            
        except Exception as e:
            logger.error(f"Error creating Trello project: {e}")
            return {"error": f"Trello integration failed: {str(e)}"}
    
    def _get_target_list_id(self, task: TaskData, list_mapping: Dict[str, str], default_list_id: str) -> str:
        """Determine which Trello list to place the task card in"""
        # Place high priority tasks in "To Do" list (assuming it exists)
        if task.priority == Priority.urgent or task.priority == Priority.high:
            return list_mapping.get("To Do", default_list_id)
        else:
            # Medium/low priority tasks go to default list
            return default_list_id
    
    def format_task_response(self, tasks: List[TaskData], trello_results: Optional[Dict[str, Any]] = None) -> str:
        """Format task breakdown as readable text"""
        if not tasks:
            return "[WARNING] No specific tasks identified from the provided milestones."
        
        response = "[TASKS] DETAILED TASK BREAKDOWN:\n\n"
        
        # Add Trello integration results if available
        if trello_results and "error" not in trello_results:
            response += f"[TRELLO] Board Created: {trello_results.get('board_name', 'N/A')}\n"
            response += f"[TRELLO] Board URL: {trello_results.get('board_url', 'N/A')}\n"
            response += f"[TRELLO] Cards Created: {trello_results.get('cards_created', 0)}/{trello_results.get('total_tasks', 0)}\n\n"
        elif trello_results and "error" in trello_results:
            response += f"[TRELLO] Integration Failed: {trello_results['error']}\n\n"
        
        total_hours = 0
        for i, task in enumerate(tasks, 1):
            response += f"[T{i}] {task.title}\n"
            response += f"     [DESC] {task.description}\n"
            response += f"     [TIME] Estimated: {task.estimated_hours} hours\n"
            response += f"     [PRIORITY] {task.priority.value.upper()}\n"
            response += f"     [SKILLS] {', '.join(task.skills_required)}\n"
            
            if task.dependencies:
                response += f"     [DEPS] Dependencies: {', '.join(task.dependencies)}\n"
            
            response += "\n"
            total_hours += task.estimated_hours or 0
        
        response += f"[SUMMARY] Total Estimated Hours: {total_hours}\n"
        response += f"[SUMMARY] Estimated Weeks: {total_hours / 40:.1f} (assuming 40 hours/week)\n"
        response += "[STATUS] Task breakdown complete - ready for resource allocation"
        
        return response


if __name__ == "__main__":
    agent = TaskAgent()
    agent.run()
