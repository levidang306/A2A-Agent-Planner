"""
Enterprise-grade Task Agent with proper architecture patterns
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from ..a2a.types import MessageRequest, MessageResponse, TaskData, Priority
from ..config.settings import get_config
from ..services.factory import get_service_factory
from ..services.interfaces import IProjectManagementService
from ..domain.models import Project, Task, ProjectStatus
from ..domain.repositories import IProjectRepository, ITaskRepository
from ..infrastructure.repositories import InMemoryProjectRepository, InMemoryTaskRepository

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    """
    Enterprise Task Agent with clean architecture patterns
    
    Responsibilities:
    - Break down milestones into detailed tasks
    - Estimate task effort and complexity
    - Integrate with multiple project management systems
    - Maintain task data integrity and relationships
    """
    
    def __init__(self, 
                 project_repo: IProjectRepository = None,
                 task_repo: ITaskRepository = None,
                 project_services: List[IProjectManagementService] = None):
        """
        Initialize TaskAgent with dependency injection
        
        Args:
            project_repo: Repository for project data
            task_repo: Repository for task data  
            project_services: List of project management services
        """
        super().__init__()
        
        # Configuration
        self.config = get_config()
        self.service_factory = get_service_factory()
        
        # Repositories (dependency injection)
        self.project_repo = project_repo or InMemoryProjectRepository()
        self.task_repo = task_repo or InMemoryTaskRepository()
        
        # Services (dependency injection)
        self.project_services = project_services or self.service_factory.create_project_management_services()
        self.ai_service = self.service_factory.get_ai_service()
        
        # Agent configuration
        self.port = self.config.task_agent.port
        self.current_project: Optional[Project] = None
        
        logger.info(f"TaskAgent initialized with {len(self.project_services)} project management services")
    
    async def process_message(self, request: MessageRequest) -> MessageResponse:
        """
        Process incoming milestone breakdown request
        
        Args:
            request: A2A message request containing milestone data
            
        Returns:
            MessageResponse with task breakdown and integration results
        """
        try:
            logger.info(f"Processing milestone breakdown request: {request.type}")
            
            # Extract milestone content
            content = request.content
            milestone_data = getattr(request, 'milestone_data', None)
            
            # Create or get project context
            project = await self._get_or_create_project(content)
            
            # Analyze and break down tasks
            task_breakdown = await self._analyze_milestone_tasks(content, milestone_data)
            
            if not task_breakdown:
                return self._create_error_response("Failed to analyze milestone and create tasks")
            
            # Save tasks to repository
            saved_tasks = await self._save_tasks_to_repository(project.id, task_breakdown)
            
            # Integrate with external project management systems
            integration_results = await self._integrate_with_external_systems(project, saved_tasks)
            
            # Generate comprehensive response
            response_text = self._format_comprehensive_response(saved_tasks, integration_results)
            
            return MessageResponse(
                id=str(uuid.uuid4()),
                response=self.create_message(response_text),
                task_breakdown=[task.to_task_data() for task in saved_tasks],
                integration_results=integration_results
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._create_error_response(f"Task analysis failed: {str(e)}")
    
    async def _get_or_create_project(self, content: str) -> Project:
        """Get existing project or create new one from content"""
        
        # Extract project name from content (simplified)
        project_name = f"A2A Project - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Check if current project exists
        if self.current_project is None:
            # Create new project
            project = Project(
                id=str(uuid.uuid4()),
                name=project_name,
                description=content[:200] + "..." if len(content) > 200 else content,
                status=ProjectStatus.PLANNING
            )
            
            # Save to repository
            self.current_project = await self.project_repo.create(project)
            logger.info(f"Created new project: {project.name}")
        
        return self.current_project
    
    async def _analyze_milestone_tasks(self, content: str, milestone_data=None) -> List[Task]:
        """Analyze milestone content and break down into tasks"""
        
        try:
            # Use AI service for task analysis
            if self.ai_service:
                raw_tasks = await self._ai_task_analysis(content)
            else:
                # Fallback to rule-based analysis
                raw_tasks = self._rule_based_task_analysis(content)
            
            # Convert to domain Task objects
            tasks = []
            for i, task_data in enumerate(raw_tasks):
                task = Task(
                    id=str(uuid.uuid4()),
                    project_id=self.current_project.id if self.current_project else "",
                    milestone_id=None,  # Could be set from milestone_data
                    title=task_data.title,
                    description=task_data.description,
                    estimated_hours=task_data.estimated_hours,
                    priority=task_data.priority,
                    skills_required=task_data.skills_required,
                    dependencies=task_data.dependencies
                )
                tasks.append(task)
            
            logger.info(f"Generated {len(tasks)} tasks from milestone analysis")
            return tasks
            
        except Exception as e:
            logger.error(f"Error in task analysis: {e}")
            return []
    
    async def _ai_task_analysis(self, content: str) -> List[TaskData]:
        """Use AI service for intelligent task breakdown"""
        
        prompt = f"""
        Analyze the following milestone/project description and break it down into specific, actionable tasks.
        
        Content: {content}
        
        For each task, provide:
        1. Clear, specific title
        2. Detailed description
        3. Estimated hours (be realistic)
        4. Priority level (urgent/high/medium/low)
        5. Required skills
        6. Dependencies (if any)
        
        Focus on creating tasks that are:
        - Specific and measurable
        - Achievable within estimated timeframe
        - Properly sequenced with dependencies
        - Assigned appropriate skill requirements
        """
        
        try:
            ai_response = await self.ai_service.analyze_content(prompt)
            # Parse AI response into TaskData objects
            return self._parse_ai_task_response(ai_response)
            
        except Exception as e:
            logger.error(f"AI task analysis failed: {e}")
            return self._rule_based_task_analysis(content)
    
    def _rule_based_task_analysis(self, content: str) -> List[TaskData]:
        """Fallback rule-based task analysis"""
        
        # Simple rule-based task generation
        base_tasks = [
            TaskData(
                title="Project Planning and Requirements Analysis",
                description="Define project scope, gather requirements, and create initial project structure",
                estimated_hours=8,
                priority=Priority.high,
                skills_required=["project_management", "business_analysis"],
                dependencies=[]
            ),
            TaskData(
                title="System Design and Architecture",
                description="Design system architecture, database schema, and technical specifications",
                estimated_hours=16,
                priority=Priority.high,
                skills_required=["system_design", "architecture"],
                dependencies=["Project Planning and Requirements Analysis"]
            ),
            TaskData(
                title="Implementation and Development",
                description="Core development work based on the milestone requirements",
                estimated_hours=40,
                priority=Priority.medium,
                skills_required=["programming", "development"],
                dependencies=["System Design and Architecture"]
            ),
            TaskData(
                title="Testing and Quality Assurance",
                description="Comprehensive testing including unit tests, integration tests, and user acceptance testing",
                estimated_hours=16,
                priority=Priority.medium,
                skills_required=["testing", "qa"],
                dependencies=["Implementation and Development"]
            ),
            TaskData(
                title="Documentation and Deployment",
                description="Create user documentation, deployment guides, and deploy to production",
                estimated_hours=8,
                priority=Priority.low,
                skills_required=["documentation", "devops"],
                dependencies=["Testing and Quality Assurance"]
            )
        ]
        
        return base_tasks
    
    def _parse_ai_task_response(self, ai_response: str) -> List[TaskData]:
        """Parse AI response into TaskData objects"""
        # This would contain logic to parse AI response
        # For now, return rule-based tasks
        return self._rule_based_task_analysis("")
    
    async def _save_tasks_to_repository(self, project_id: str, tasks: List[Task]) -> List[Task]:
        """Save tasks to repository and return saved tasks"""
        
        saved_tasks = []
        for task in tasks:
            task.project_id = project_id
            saved_task = await self.task_repo.create(task)
            saved_tasks.append(saved_task)
        
        logger.info(f"Saved {len(saved_tasks)} tasks to repository")
        return saved_tasks
    
    async def _integrate_with_external_systems(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Integrate with all enabled project management systems"""
        
        integration_results = {
            "successful_integrations": [],
            "failed_integrations": [],
            "total_services": len(self.project_services)
        }
        
        for service in self.project_services:
            try:
                if not service.is_enabled():
                    continue
                
                # Create project in external system
                external_project = await service.create_project(
                    project_name=project.name,
                    description=project.description
                )
                
                if external_project:
                    # Create tasks in external system
                    created_tasks = []
                    for task in tasks:
                        external_task = await service.create_task(
                            project_id=external_project['id'],
                            task=task.to_task_data()
                        )
                        if external_task:
                            created_tasks.append(external_task)
                    
                    integration_results["successful_integrations"].append({
                        "service_type": external_project.get('type', 'unknown'),
                        "project": external_project,
                        "tasks_created": len(created_tasks),
                        "total_tasks": len(tasks)
                    })
                    
                    logger.info(f"Successfully integrated with {external_project.get('type')} service")
                
            except Exception as e:
                logger.error(f"Integration failed for service: {e}")
                integration_results["failed_integrations"].append({
                    "service": str(service.__class__.__name__),
                    "error": str(e)
                })
        
        return integration_results
    
    def _format_comprehensive_response(self, tasks: List[Task], integration_results: Dict[str, Any]) -> str:
        """Format comprehensive response with task breakdown and integration results"""
        
        if not tasks:
            return "[WARNING] No tasks generated from milestone analysis."
        
        response_lines = [
            "[TASK AGENT] MILESTONE BREAKDOWN COMPLETE",
            "=" * 50,
            "",
            f"[PROJECT] {self.current_project.name if self.current_project else 'Unknown Project'}",
            f"[SUMMARY] Generated {len(tasks)} tasks",
            f"[SUMMARY] Total Estimated Hours: {sum(task.estimated_hours for task in tasks)}",
            f"[SUMMARY] Estimated Duration: {sum(task.estimated_hours for task in tasks) / 40:.1f} weeks (40h/week)",
            ""
        ]
        
        # Add integration results
        if integration_results["successful_integrations"]:
            response_lines.append("[INTEGRATIONS] Successfully integrated with:")
            for integration in integration_results["successful_integrations"]:
                service_type = integration["service_type"]
                project_info = integration["project"]
                tasks_created = integration["tasks_created"]
                
                response_lines.append(f"  ✓ {service_type.upper()}")
                response_lines.append(f"    - Project: {project_info.get('name', 'N/A')}")
                if 'url' in project_info:
                    response_lines.append(f"    - URL: {project_info['url']}")
                response_lines.append(f"    - Tasks Created: {tasks_created}/{integration['total_tasks']}")
            response_lines.append("")
        
        if integration_results["failed_integrations"]:
            response_lines.append("[INTEGRATIONS] Failed integrations:")
            for failure in integration_results["failed_integrations"]:
                response_lines.append(f"  ✗ {failure['service']}: {failure['error']}")
            response_lines.append("")
        
        # Add detailed task breakdown
        response_lines.extend([
            "[TASKS] DETAILED BREAKDOWN:",
            "-" * 30,
            ""
        ])
        
        for i, task in enumerate(tasks, 1):
            response_lines.extend([
                f"[T{i}] {task.title}",
                f"     [DESC] {task.description}",
                f"     [TIME] {task.estimated_hours} hours",
                f"     [PRIORITY] {task.priority.value.upper()}",
                f"     [SKILLS] {', '.join(task.skills_required)}",
            ])
            
            if task.dependencies:
                response_lines.append(f"     [DEPS] {', '.join(task.dependencies)}")
            
            response_lines.append("")
        
        response_lines.extend([
            "[STATUS] Task breakdown and integration complete",
            "[NEXT] Ready for resource allocation"
        ])
        
        return "\n".join(response_lines)
    
    def _create_error_response(self, error_message: str) -> MessageResponse:
        """Create error response"""
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(f"[ERROR] {error_message}"),
            task_breakdown=[],
            error=error_message
        )
    
    def get_agent_card(self):
        """Get agent card with capabilities"""
        capabilities = [
            "milestone_analysis",
            "task_breakdown", 
            "effort_estimation",
            "dependency_mapping",
            "skill_identification",
            "multi_platform_integration"
        ]
        
        # Add service-specific capabilities
        for service in self.project_services:
            if service.is_enabled():
                service_name = service.__class__.__name__.replace("ProjectService", "").lower()
                capabilities.append(f"{service_name}_integration")
        
        return {
            "name": "TaskAgent",
            "description": "Enterprise task breakdown and project management integration agent",
            "version": "2.0.0",
            "capabilities": capabilities,
            "protocols": ["A2A"],
            "endpoints": {
                "primary": f"http://localhost:{self.port}/message"
            },
            "configuration": {
                "project_services": len(self.project_services),
                "ai_enabled": self.ai_service is not None,
                "repository_type": self.task_repo.__class__.__name__
            }
        }


if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = TaskAgent()
        await agent.start_server()
    
    asyncio.run(main())
