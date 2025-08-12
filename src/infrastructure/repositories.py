"""
In-memory repository implementations
"""
import uuid
from typing import List, Optional, Dict, Any
from ..domain.repositories import IProjectRepository, ITaskRepository, IMilestoneRepository, ITeamMemberRepository
from ..domain.models import Project, Task, Milestone, TeamMember


class InMemoryProjectRepository(IProjectRepository):
    """In-memory implementation of project repository"""
    
    def __init__(self):
        self._projects: Dict[str, Project] = {}
    
    async def create(self, project: Project) -> Project:
        """Create a new project"""
        if not project.id:
            project.id = str(uuid.uuid4())
        
        self._projects[project.id] = project
        return project
    
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self._projects.get(project_id)
    
    async def get_all(self) -> List[Project]:
        """Get all projects"""
        return list(self._projects.values())
    
    async def update(self, project: Project) -> Project:
        """Update existing project"""
        if project.id in self._projects:
            self._projects[project.id] = project
        return project
    
    async def delete(self, project_id: str) -> bool:
        """Delete project"""
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False


class InMemoryTaskRepository(ITaskRepository):
    """In-memory implementation of task repository"""
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
    
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        if not task.id:
            task.id = str(uuid.uuid4())
        
        self._tasks[task.id] = task
        return task
    
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self._tasks.get(task_id)
    
    async def get_by_project_id(self, project_id: str) -> List[Task]:
        """Get all tasks for a project"""
        return [task for task in self._tasks.values() if task.project_id == project_id]
    
    async def get_by_milestone_id(self, milestone_id: str) -> List[Task]:
        """Get all tasks for a milestone"""
        return [task for task in self._tasks.values() if task.milestone_id == milestone_id]
    
    async def update(self, task: Task) -> Task:
        """Update existing task"""
        if task.id in self._tasks:
            self._tasks[task.id] = task
        return task
    
    async def delete(self, task_id: str) -> bool:
        """Delete task"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


class InMemoryMilestoneRepository(IMilestoneRepository):
    """In-memory implementation of milestone repository"""
    
    def __init__(self):
        self._milestones: Dict[str, Milestone] = {}
    
    async def create(self, milestone: Milestone) -> Milestone:
        """Create a new milestone"""
        if not milestone.id:
            milestone.id = str(uuid.uuid4())
        
        self._milestones[milestone.id] = milestone
        return milestone
    
    async def get_by_id(self, milestone_id: str) -> Optional[Milestone]:
        """Get milestone by ID"""
        return self._milestones.get(milestone_id)
    
    async def get_by_project_id(self, project_id: str) -> List[Milestone]:
        """Get all milestones for a project"""
        return [milestone for milestone in self._milestones.values() if milestone.project_id == project_id]
    
    async def update(self, milestone: Milestone) -> Milestone:
        """Update existing milestone"""
        if milestone.id in self._milestones:
            self._milestones[milestone.id] = milestone
        return milestone
    
    async def delete(self, milestone_id: str) -> bool:
        """Delete milestone"""
        if milestone_id in self._milestones:
            del self._milestones[milestone_id]
            return True
        return False


class InMemoryTeamMemberRepository(ITeamMemberRepository):
    """In-memory implementation of team member repository"""
    
    def __init__(self):
        self._members: Dict[str, TeamMember] = {}
    
    async def create(self, member: TeamMember) -> TeamMember:
        """Create a new team member"""
        if not member.id:
            member.id = str(uuid.uuid4())
        
        self._members[member.id] = member
        return member
    
    async def get_by_id(self, member_id: str) -> Optional[TeamMember]:
        """Get team member by ID"""
        return self._members.get(member_id)
    
    async def get_all(self) -> List[TeamMember]:
        """Get all team members"""
        return list(self._members.values())
    
    async def get_by_skills(self, skills: List[str]) -> List[TeamMember]:
        """Get team members with specific skills"""
        result = []
        required_skills = set(skills)
        
        for member in self._members.values():
            member_skills = set(member.skills)
            if required_skills.issubset(member_skills):
                result.append(member)
        
        return result
    
    async def update(self, member: TeamMember) -> TeamMember:
        """Update existing team member"""
        if member.id in self._members:
            self._members[member.id] = member
        return member
    
    async def delete(self, member_id: str) -> bool:
        """Delete team member"""
        if member_id in self._members:
            del self._members[member_id]
            return True
        return False
