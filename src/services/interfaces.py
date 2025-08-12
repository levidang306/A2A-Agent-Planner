"""
Service interfaces for A2A system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..a2a.types import TaskData


class IProjectManagementService(ABC):
    """Interface for project management services (Trello, GitHub, etc.)"""
    
    @abstractmethod
    async def create_project(self, project_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Create a new project/board"""
        pass
    
    @abstractmethod
    async def create_task(self, project_id: str, task: TaskData) -> Optional[Dict[str, Any]]:
        """Create a task/card in the project"""
        pass
    
    @abstractmethod
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing task"""
        pass
    
    @abstractmethod
    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks in a project"""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if the service is enabled and configured"""
        pass


class ITaskAnalysisService(ABC):
    """Interface for task analysis services"""
    
    @abstractmethod
    async def analyze_milestone(self, milestone_content: str) -> List[TaskData]:
        """Analyze milestone and break down into tasks"""
        pass
    
    @abstractmethod
    async def estimate_effort(self, task_description: str) -> int:
        """Estimate effort for a task in hours"""
        pass
    
    @abstractmethod
    async def identify_dependencies(self, tasks: List[TaskData]) -> List[TaskData]:
        """Identify dependencies between tasks"""
        pass


class IResourceAllocationService(ABC):
    """Interface for resource allocation services"""
    
    @abstractmethod
    async def allocate_resources(self, tasks: List[TaskData]) -> Dict[str, Any]:
        """Allocate resources to tasks"""
        pass
    
    @abstractmethod
    async def check_availability(self, resource_id: str, start_date: str, end_date: str) -> bool:
        """Check resource availability"""
        pass


class ITimelineService(ABC):
    """Interface for timeline generation services"""
    
    @abstractmethod
    async def generate_timeline(self, milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate project timeline from milestones"""
        pass
    
    @abstractmethod
    async def update_timeline(self, timeline_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing timeline"""
        pass
