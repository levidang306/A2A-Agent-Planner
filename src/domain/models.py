"""
Domain models for A2A system
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from ..a2a.types import TaskData, Priority


class ProjectStatus(Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass
class Project:
    """Domain model for a project"""
    id: str
    name: str
    description: str
    status: ProjectStatus = ProjectStatus.PLANNING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Project metadata
    milestones: List['Milestone'] = field(default_factory=list)
    tasks: List['Task'] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    
    # External integrations
    trello_board_id: Optional[str] = None
    github_repo_url: Optional[str] = None
    local_project_path: Optional[str] = None
    
    def add_milestone(self, milestone: 'Milestone') -> None:
        """Add milestone to project"""
        self.milestones.append(milestone)
        self.updated_at = datetime.now()
    
    def add_task(self, task: 'Task') -> None:
        """Add task to project"""
        self.tasks.append(task)
        self.updated_at = datetime.now()
    
    def get_total_estimated_hours(self) -> int:
        """Calculate total estimated hours for all tasks"""
        return sum(task.estimated_hours for task in self.tasks)
    
    def get_completion_percentage(self) -> float:
        """Calculate project completion percentage"""
        if not self.tasks:
            return 0.0
        
        completed_tasks = len([t for t in self.tasks if t.status == TaskStatus.DONE])
        return (completed_tasks / len(self.tasks)) * 100


@dataclass
class Milestone:
    """Domain model for a project milestone"""
    id: str
    project_id: str
    title: str
    description: str
    due_date: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    created_at: datetime = field(default_factory=datetime.now)
    
    # Milestone relationships
    tasks: List['Task'] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def add_task(self, task: 'Task') -> None:
        """Add task to milestone"""
        self.tasks.append(task)
        task.milestone_id = self.id


@dataclass
class Task:
    """Enhanced domain model for a task"""
    id: str
    project_id: str
    milestone_id: Optional[str]
    title: str
    description: str
    estimated_hours: int
    priority: Priority
    status: TaskStatus = TaskStatus.TODO
    
    # Task metadata
    skills_required: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # External integrations
    trello_card_id: Optional[str] = None
    github_issue_number: Optional[int] = None
    
    @classmethod
    def from_task_data(cls, task_data: TaskData, project_id: str, task_id: str) -> 'Task':
        """Create Task from TaskData"""
        return cls(
            id=task_id,
            project_id=project_id,
            milestone_id=None,
            title=task_data.title,
            description=task_data.description,
            estimated_hours=task_data.estimated_hours,
            priority=task_data.priority,
            skills_required=task_data.skills_required,
            dependencies=task_data.dependencies
        )
    
    def to_task_data(self) -> TaskData:
        """Convert to TaskData for agent communication"""
        return TaskData(
            title=self.title,
            description=self.description,
            estimated_hours=self.estimated_hours,
            priority=self.priority,
            skills_required=self.skills_required,
            dependencies=self.dependencies
        )
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status"""
        self.status = new_status
        self.updated_at = datetime.now()


@dataclass
class TeamMember:
    """Domain model for team member"""
    id: str
    name: str
    email: str
    skills: List[str] = field(default_factory=list)
    availability: float = 1.0  # 1.0 = full time, 0.5 = part time
    hourly_rate: Optional[float] = None
    
    # Assignment tracking
    assigned_tasks: List[str] = field(default_factory=list)
    current_workload: int = 0  # hours per week
    
    def can_take_task(self, task: Task, max_workload: int = 40) -> bool:
        """Check if team member can take on a task"""
        # Check skills
        required_skills = set(task.skills_required)
        member_skills = set(self.skills)
        
        if not required_skills.issubset(member_skills):
            return False
        
        # Check workload
        if self.current_workload + task.estimated_hours > max_workload:
            return False
        
        return True
    
    def assign_task(self, task: Task) -> None:
        """Assign task to team member"""
        self.assigned_tasks.append(task.id)
        self.current_workload += task.estimated_hours
        task.assigned_to = self.id
