"""
Application Service Layer - Business Logic Orchestration
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domain.models import Project, Task, Milestone, TeamMember, ProjectStatus, TaskStatus
from ..domain.repositories import IProjectRepository, ITaskRepository, IMilestoneRepository, ITeamMemberRepository
from ..a2a.types import TaskData, MessageRequest, MessageResponse
from ..services.interfaces import IProjectManagementService
from ..infrastructure.di_container import get_service, get_service_by_name

logger = logging.getLogger(__name__)


class ProjectManagementService:
    """Service for project management operations"""
    
    def __init__(self,
                 project_repo: IProjectRepository = None,
                 task_repo: ITaskRepository = None,
                 milestone_repo: IMilestoneRepository = None,
                 team_repo: ITeamMemberRepository = None):
        
        # Use dependency injection
        self.project_repo = project_repo or get_service(IProjectRepository)
        self.task_repo = task_repo or get_service(ITaskRepository)
        self.milestone_repo = milestone_repo or get_service(IMilestoneRepository)
        self.team_repo = team_repo or get_service(ITeamMemberRepository)
        
        # Get external services
        self.external_services = get_service_by_name("project_management_services")
    
    async def create_project_with_tasks(self, 
                                       project_name: str, 
                                       description: str, 
                                       tasks_data: List[TaskData]) -> Project:
        """Create a complete project with tasks and external integrations"""
        
        try:
            # Create project domain object
            project = Project(
                id=str(uuid.uuid4()),
                name=project_name,
                description=description,
                status=ProjectStatus.PLANNING,
                created_at=datetime.now()
            )
            
            # Save project to repository
            saved_project = await self.project_repo.create(project)
            
            # Create and save tasks
            created_tasks = []
            for task_data in tasks_data:
                task = Task.from_task_data(task_data, saved_project.id, str(uuid.uuid4()))
                saved_task = await self.task_repo.create(task)
                created_tasks.append(saved_task)
            
            # Update project with tasks
            saved_project.tasks = created_tasks
            await self.project_repo.update(saved_project)
            
            # Integrate with external services
            await self._integrate_project_externally(saved_project, created_tasks)
            
            logger.info(f"Created project '{project_name}' with {len(created_tasks)} tasks")
            return saved_project
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    async def _integrate_project_externally(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Integrate project with external services"""
        
        integration_results = {"successful": [], "failed": []}
        
        for service in self.external_services:
            try:
                if not service.is_enabled():
                    continue
                
                # Create project in external service
                external_project = await service.create_project(project.name, project.description)
                if not external_project:
                    continue
                
                # Create tasks in external service
                for task in tasks:
                    external_task = await service.create_task(
                        external_project['id'], 
                        task.to_task_data()
                    )
                    
                    if external_task:
                        # Update task with external reference
                        if external_project.get('type') == 'trello_board':
                            task.trello_card_id = external_task['id']
                        elif external_project.get('type') == 'github_project':
                            task.github_issue_number = external_task.get('number')
                        
                        await self.task_repo.update(task)
                
                integration_results["successful"].append({
                    "service": service.__class__.__name__,
                    "project": external_project
                })
                
            except Exception as e:
                logger.error(f"External integration failed: {e}")
                integration_results["failed"].append({
                    "service": service.__class__.__name__,
                    "error": str(e)
                })
        
        return integration_results
    
    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive project status"""
        
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return None
        
        tasks = await self.task_repo.get_by_project_id(project_id)
        milestones = await self.milestone_repo.get_by_project_id(project_id)
        
        # Calculate metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.DONE])
        total_hours = sum(task.estimated_hours for task in tasks)
        
        return {
            "project": {
                "id": project.id,
                "name": project.name,
                "status": project.status.value,
                "created_at": project.created_at.isoformat()
            },
            "metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "total_estimated_hours": total_hours,
                "estimated_weeks": total_hours / 40
            },
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "estimated_hours": task.estimated_hours,
                    "priority": task.priority.value
                } for task in tasks
            ],
            "milestones": [
                {
                    "id": milestone.id,
                    "title": milestone.title,
                    "status": milestone.status.value
                } for milestone in milestones
            ]
        }


class TaskAnalysisService:
    """Service for task analysis and breakdown"""
    
    def __init__(self):
        self.ai_service = None  # Would be injected
    
    async def analyze_milestone_content(self, content: str, context: Dict[str, Any] = None) -> List[TaskData]:
        """Analyze milestone content and generate task breakdown"""
        
        try:
            # Use AI service if available
            if self.ai_service:
                return await self._ai_based_analysis(content, context)
            else:
                return self._rule_based_analysis(content, context)
                
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            return []
    
    async def _ai_based_analysis(self, content: str, context: Dict[str, Any]) -> List[TaskData]:
        """AI-powered task analysis"""
        # Implementation would use AI service
        return self._rule_based_analysis(content, context)
    
    def _rule_based_analysis(self, content: str, context: Dict[str, Any]) -> List[TaskData]:
        """Rule-based task analysis as fallback"""
        
        # Analyze content for keywords and generate appropriate tasks
        tasks = []
        
        # Web development keywords
        if any(keyword in content.lower() for keyword in ['web', 'website', 'frontend', 'backend']):
            tasks.extend(self._generate_web_dev_tasks())
        
        # Mobile development keywords
        elif any(keyword in content.lower() for keyword in ['mobile', 'app', 'android', 'ios']):
            tasks.extend(self._generate_mobile_dev_tasks())
        
        # Data analysis keywords
        elif any(keyword in content.lower() for keyword in ['data', 'analysis', 'analytics', 'dashboard']):
            tasks.extend(self._generate_data_analysis_tasks())
        
        # Default generic tasks
        else:
            tasks.extend(self._generate_generic_tasks())
        
        return tasks
    
    def _generate_web_dev_tasks(self) -> List[TaskData]:
        """Generate web development specific tasks"""
        return [
            TaskData(
                title="Frontend Setup and Configuration",
                description="Set up development environment, choose framework, configure build tools",
                estimated_hours=8,
                priority="high",
                skills_required=["frontend", "javascript", "html", "css"],
                dependencies=[]
            ),
            TaskData(
                title="Backend API Development",
                description="Design and implement REST API endpoints, database integration",
                estimated_hours=24,
                priority="high",
                skills_required=["backend", "api_development", "database"],
                dependencies=["Frontend Setup and Configuration"]
            ),
            TaskData(
                title="User Interface Implementation",
                description="Implement responsive UI components and user interactions",
                estimated_hours=32,
                priority="medium",
                skills_required=["ui_design", "frontend", "responsive_design"],
                dependencies=["Backend API Development"]
            ),
            TaskData(
                title="Testing and Quality Assurance",
                description="Unit testing, integration testing, end-to-end testing",
                estimated_hours=16,
                priority="medium",
                skills_required=["testing", "qa", "automation"],
                dependencies=["User Interface Implementation"]
            ),
            TaskData(
                title="Deployment and DevOps",
                description="Set up CI/CD pipeline, deploy to production environment",
                estimated_hours=8,
                priority="low",
                skills_required=["devops", "ci_cd", "deployment"],
                dependencies=["Testing and Quality Assurance"]
            )
        ]
    
    def _generate_mobile_dev_tasks(self) -> List[TaskData]:
        """Generate mobile development specific tasks"""
        return [
            TaskData(
                title="Mobile App Architecture Design",
                description="Design app architecture, choose technology stack, plan user flow",
                estimated_hours=12,
                priority="high",
                skills_required=["mobile_development", "architecture", "ui_ux"],
                dependencies=[]
            ),
            TaskData(
                title="Core Features Implementation",
                description="Implement main app features and functionality",
                estimated_hours=40,
                priority="high",
                skills_required=["mobile_development", "programming"],
                dependencies=["Mobile App Architecture Design"]
            ),
            TaskData(
                title="Platform-specific Optimization",
                description="Optimize for iOS/Android platforms, handle platform differences",
                estimated_hours=16,
                priority="medium",
                skills_required=["ios", "android", "optimization"],
                dependencies=["Core Features Implementation"]
            ),
            TaskData(
                title="App Store Preparation",
                description="Prepare app for store submission, create store listings",
                estimated_hours=8,
                priority="low",
                skills_required=["app_store", "marketing"],
                dependencies=["Platform-specific Optimization"]
            )
        ]
    
    def _generate_data_analysis_tasks(self) -> List[TaskData]:
        """Generate data analysis specific tasks"""
        return [
            TaskData(
                title="Data Collection and Preparation",
                description="Gather data sources, clean and prepare data for analysis",
                estimated_hours=16,
                priority="high",
                skills_required=["data_analysis", "data_cleaning", "sql"],
                dependencies=[]
            ),
            TaskData(
                title="Exploratory Data Analysis",
                description="Perform initial data exploration, identify patterns and insights",
                estimated_hours=12,
                priority="medium",
                skills_required=["data_analysis", "statistics", "visualization"],
                dependencies=["Data Collection and Preparation"]
            ),
            TaskData(
                title="Dashboard Development",
                description="Create interactive dashboards and visualizations",
                estimated_hours=20,
                priority="medium",
                skills_required=["dashboard", "visualization", "frontend"],
                dependencies=["Exploratory Data Analysis"]
            ),
            TaskData(
                title="Report Generation and Documentation",
                description="Generate comprehensive reports and documentation",
                estimated_hours=8,
                priority="low",
                skills_required=["documentation", "reporting"],
                dependencies=["Dashboard Development"]
            )
        ]
    
    def _generate_generic_tasks(self) -> List[TaskData]:
        """Generate generic project tasks"""
        return [
            TaskData(
                title="Project Planning and Analysis",
                description="Define project scope, requirements, and create project plan",
                estimated_hours=8,
                priority="high",
                skills_required=["project_management", "analysis"],
                dependencies=[]
            ),
            TaskData(
                title="Design and Architecture",
                description="Create system design, architecture, and technical specifications",
                estimated_hours=16,
                priority="high",
                skills_required=["design", "architecture"],
                dependencies=["Project Planning and Analysis"]
            ),
            TaskData(
                title="Implementation and Development",
                description="Core development work and feature implementation",
                estimated_hours=32,
                priority="medium",
                skills_required=["development", "programming"],
                dependencies=["Design and Architecture"]
            ),
            TaskData(
                title="Testing and Validation",
                description="Comprehensive testing and quality assurance",
                estimated_hours=12,
                priority="medium",
                skills_required=["testing", "qa"],
                dependencies=["Implementation and Development"]
            ),
            TaskData(
                title="Documentation and Delivery",
                description="Create documentation and prepare for delivery",
                estimated_hours=6,
                priority="low",
                skills_required=["documentation"],
                dependencies=["Testing and Validation"]
            )
        ]


class ResourceAllocationService:
    """Service for resource allocation and team management"""
    
    def __init__(self, team_repo: ITeamMemberRepository = None):
        self.team_repo = team_repo or get_service(ITeamMemberRepository)
    
    async def allocate_tasks_to_team(self, tasks: List[Task]) -> Dict[str, Any]:
        """Allocate tasks to available team members"""
        
        team_members = await self.team_repo.get_all()
        allocation_results = {
            "allocations": [],
            "unallocated_tasks": [],
            "team_utilization": {}
        }
        
        for task in tasks:
            # Find suitable team member
            suitable_member = await self._find_suitable_member(task, team_members)
            
            if suitable_member and suitable_member.can_take_task(task):
                suitable_member.assign_task(task)
                await self.team_repo.update(suitable_member)
                
                allocation_results["allocations"].append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "assigned_to": suitable_member.name,
                    "member_id": suitable_member.id
                })
            else:
                allocation_results["unallocated_tasks"].append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "reason": "No suitable team member available"
                })
        
        # Calculate team utilization
        for member in team_members:
            allocation_results["team_utilization"][member.name] = {
                "current_workload": member.current_workload,
                "utilization_percentage": (member.current_workload / 40) * 100,
                "assigned_tasks": len(member.assigned_tasks)
            }
        
        return allocation_results
    
    async def _find_suitable_member(self, task: Task, team_members: List[TeamMember]) -> Optional[TeamMember]:
        """Find the most suitable team member for a task"""
        
        suitable_members = []
        
        for member in team_members:
            if member.can_take_task(task):
                # Calculate skill match score
                required_skills = set(task.skills_required)
                member_skills = set(member.skills)
                skill_match = len(required_skills.intersection(member_skills)) / len(required_skills)
                
                suitable_members.append((member, skill_match))
        
        if not suitable_members:
            return None
        
        # Return member with highest skill match and lowest workload
        suitable_members.sort(key=lambda x: (x[1], -x[0].current_workload), reverse=True)
        return suitable_members[0][0]
