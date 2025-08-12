"""
Factory for creating service instances
"""
import logging
from typing import List, Dict, Any
from .interfaces import IProjectManagementService
from .project_services import TrelloProjectService, GitHubProjectService, LocalProjectService
from ..config.settings import AppConfig, get_config

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Factory for creating service instances"""
    
    def __init__(self, config: AppConfig = None):
        self.config = config or get_config()
        self._services_cache: Dict[str, Any] = {}
    
    def create_project_management_services(self) -> List[IProjectManagementService]:
        """Create all enabled project management services"""
        services = []
        
        # Create Trello service if enabled
        if self.config.trello.enabled:
            trello_service = self._create_trello_service()
            if trello_service:
                services.append(trello_service)
        
        # Always include local service as fallback
        local_service = self._create_local_service()
        services.append(local_service)
        
        return services
    
    def _create_trello_service(self) -> TrelloProjectService:
        """Create Trello service instance"""
        if 'trello_service' not in self._services_cache:
            try:
                # Import here to avoid circular dependencies
                from ..tools.trello_integration import TrelloIntegration
                
                trello_client = TrelloIntegration(
                    api_key=self.config.trello.api_key,
                    api_secret=self.config.trello.api_secret
                )
                
                self._services_cache['trello_service'] = TrelloProjectService(
                    config=self.config.trello,
                    trello_client=trello_client
                )
            except Exception as e:
                logger.error(f"Failed to create Trello service: {e}")
                return None
        
        return self._services_cache.get('trello_service')
    
    def _create_local_service(self) -> LocalProjectService:
        """Create local project service instance"""
        if 'local_service' not in self._services_cache:
            self._services_cache['local_service'] = LocalProjectService()
        
        return self._services_cache['local_service']
    
    def get_ai_service(self):
        """Get AI service instance"""
        if 'ai_service' not in self._services_cache:
            try:
                from ..a2a.ai_service import AIService
                self._services_cache['ai_service'] = AIService()
            except Exception as e:
                logger.error(f"Failed to create AI service: {e}")
                return None
        
        return self._services_cache.get('ai_service')


# Global factory instance
service_factory = ServiceFactory()


def get_service_factory() -> ServiceFactory:
    """Get global service factory instance"""
    return service_factory
