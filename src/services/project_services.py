"""
Concrete implementations of project management services
"""
import logging
from typing import Dict, Any, List, Optional
from .interfaces import IProjectManagementService
from ..a2a.types import TaskData
from ..config.settings import TrelloConfig, GitHubConfig

logger = logging.getLogger(__name__)


class TrelloProjectService(IProjectManagementService):
    """Trello implementation of project management service"""
    
    def __init__(self, config: TrelloConfig, trello_client=None):
        self.config = config
        self.client = trello_client
        self._enabled = config.enabled and bool(config.api_key)
    
    async def create_project(self, project_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Create a new Trello board"""
        if not self.is_enabled():
            return None
        
        try:
            board_id = self.client.create_board(project_name)
            if board_id:
                return {
                    "id": board_id,
                    "name": project_name,
                    "url": f"https://trello.com/b/{board_id}",
                    "type": "trello_board"
                }
        except Exception as e:
            logger.error(f"Failed to create Trello board: {e}")
        
        return None
    
    async def create_task(self, project_id: str, task: TaskData) -> Optional[Dict[str, Any]]:
        """Create a Trello card for the task"""
        if not self.is_enabled():
            return None
        
        try:
            # Get board lists
            lists = self.client.get_lists_on_board(project_id)
            if not lists:
                return None
            
            # Use first list as default
            list_id = lists[0]['id']
            
            # Create card description
            description = f"""
**Description:** {task.description}
**Estimated Hours:** {task.estimated_hours}
**Priority:** {task.priority.value.upper()}
**Skills Required:** {', '.join(task.skills_required)}
**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}
            """.strip()
            
            card_id = self.client.create_card(
                list_id=list_id,
                card_name=task.title,
                description=description
            )
            
            if card_id:
                return {
                    "id": card_id,
                    "title": task.title,
                    "list_id": list_id,
                    "type": "trello_card"
                }
        except Exception as e:
            logger.error(f"Failed to create Trello card: {e}")
        
        return None
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a Trello card"""
        # Implementation would depend on Trello client capabilities
        return False
    
    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all cards from Trello board"""
        if not self.is_enabled():
            return []
        
        try:
            # Implementation would get all cards from board
            return []
        except Exception as e:
            logger.error(f"Failed to get Trello tasks: {e}")
            return []
    
    def is_enabled(self) -> bool:
        """Check if Trello service is enabled"""
        return self._enabled and self.client is not None


class GitHubProjectService(IProjectManagementService):
    """GitHub implementation of project management service"""
    
    def __init__(self, config: GitHubConfig, github_client=None):
        self.config = config
        self.client = github_client
        self._enabled = config.enabled and bool(config.token)
    
    async def create_project(self, project_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Create a new GitHub repository or project"""
        if not self.is_enabled():
            return None
        
        try:
            # Implementation would create GitHub repository or project
            return {
                "id": "github_project_id",
                "name": project_name,
                "url": f"https://github.com/user/{project_name}",
                "type": "github_project"
            }
        except Exception as e:
            logger.error(f"Failed to create GitHub project: {e}")
        
        return None
    
    async def create_task(self, project_id: str, task: TaskData) -> Optional[Dict[str, Any]]:
        """Create a GitHub issue for the task"""
        if not self.is_enabled():
            return None
        
        try:
            # Implementation would create GitHub issue
            return {
                "id": "github_issue_id",
                "title": task.title,
                "number": 1,
                "type": "github_issue"
            }
        except Exception as e:
            logger.error(f"Failed to create GitHub issue: {e}")
        
        return None
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a GitHub issue"""
        return False
    
    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all issues from GitHub repository"""
        if not self.is_enabled():
            return []
        
        return []
    
    def is_enabled(self) -> bool:
        """Check if GitHub service is enabled"""
        return self._enabled and self.client is not None


class LocalProjectService(IProjectManagementService):
    """Local file-based project management service"""
    
    def __init__(self, output_dir: str = "a2a_projects"):
        self.output_dir = output_dir
        self._enabled = True
    
    async def create_project(self, project_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Create local project files"""
        try:
            # Implementation would create local files
            return {
                "id": project_name.replace(" ", "_"),
                "name": project_name,
                "path": f"{self.output_dir}/{project_name}",
                "type": "local_project"
            }
        except Exception as e:
            logger.error(f"Failed to create local project: {e}")
        
        return None
    
    async def create_task(self, project_id: str, task: TaskData) -> Optional[Dict[str, Any]]:
        """Add task to local CSV file"""
        try:
            # Implementation would append to CSV file
            return {
                "id": f"task_{len(str(task.title))}",
                "title": task.title,
                "type": "local_task"
            }
        except Exception as e:
            logger.error(f"Failed to create local task: {e}")
        
        return None
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task in local files"""
        return True
    
    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Read tasks from local CSV file"""
        return []
    
    def is_enabled(self) -> bool:
        """Local service is always enabled"""
        return True
