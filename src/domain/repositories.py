"""
Repository pattern for data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .models import Project, Task, Milestone, TeamMember


class IProjectRepository(ABC):
    """Repository interface for projects"""
    
    @abstractmethod
    async def create(self, project: Project) -> Project:
        """Create a new project"""
        pass
    
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Project]:
        """Get all projects"""
        pass
    
    @abstractmethod
    async def update(self, project: Project) -> Project:
        """Update existing project"""
        pass
    
    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        """Delete project"""
        pass


class ITaskRepository(ABC):
    """Repository interface for tasks"""
    
    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        pass
    
    @abstractmethod
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        pass
    
    @abstractmethod
    async def get_by_project_id(self, project_id: str) -> List[Task]:
        """Get all tasks for a project"""
        pass
    
    @abstractmethod
    async def get_by_milestone_id(self, milestone_id: str) -> List[Task]:
        """Get all tasks for a milestone"""
        pass
    
    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Update existing task"""
        pass
    
    @abstractmethod
    async def delete(self, task_id: str) -> bool:
        """Delete task"""
        pass


class IMilestoneRepository(ABC):
    """Repository interface for milestones"""
    
    @abstractmethod
    async def create(self, milestone: Milestone) -> Milestone:
        """Create a new milestone"""
        pass
    
    @abstractmethod
    async def get_by_id(self, milestone_id: str) -> Optional[Milestone]:
        """Get milestone by ID"""
        pass
    
    @abstractmethod
    async def get_by_project_id(self, project_id: str) -> List[Milestone]:
        """Get all milestones for a project"""
        pass
    
    @abstractmethod
    async def update(self, milestone: Milestone) -> Milestone:
        """Update existing milestone"""
        pass
    
    @abstractmethod
    async def delete(self, milestone_id: str) -> bool:
        """Delete milestone"""
        pass


class ITeamMemberRepository(ABC):
    """Repository interface for team members"""
    
    @abstractmethod
    async def create(self, member: TeamMember) -> TeamMember:
        """Create a new team member"""
        pass
    
    @abstractmethod
    async def get_by_id(self, member_id: str) -> Optional[TeamMember]:
        """Get team member by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[TeamMember]:
        """Get all team members"""
        pass
    
    @abstractmethod
    async def get_by_skills(self, skills: List[str]) -> List[TeamMember]:
        """Get team members with specific skills"""
        pass
    
    @abstractmethod
    async def update(self, member: TeamMember) -> TeamMember:
        """Update existing team member"""
        pass
    
    @abstractmethod
    async def delete(self, member_id: str) -> bool:
        """Delete team member"""
        pass
