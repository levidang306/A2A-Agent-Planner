"""
Dependency Injection Container for A2A System
"""
import logging
from typing import Dict, Any, TypeVar, Type, Optional, Callable
from ..config.settings import get_config, AppConfig
from ..services.factory import ServiceFactory
from ..services.interfaces import IProjectManagementService
from ..domain.repositories import IProjectRepository, ITaskRepository, IMilestoneRepository, ITeamMemberRepository
from ..infrastructure.repositories import (
    InMemoryProjectRepository, 
    InMemoryTaskRepository, 
    InMemoryMilestoneRepository, 
    InMemoryTeamMemberRepository
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._initialize_default_services()
    
    def _initialize_default_services(self):
        """Initialize default service registrations"""
        
        # Configuration
        self.register_singleton(AppConfig, lambda: get_config())
        
        # Service Factory
        self.register_singleton(ServiceFactory, lambda: ServiceFactory(self.get(AppConfig)))
        
        # Repositories (as singletons for in-memory implementations)
        self.register_singleton(IProjectRepository, lambda: InMemoryProjectRepository())
        self.register_singleton(ITaskRepository, lambda: InMemoryTaskRepository())
        self.register_singleton(IMilestoneRepository, lambda: InMemoryMilestoneRepository())
        self.register_singleton(ITeamMemberRepository, lambda: InMemoryTeamMemberRepository())
        
        # Register project management services factory
        self.register_factory(
            "project_management_services",
            lambda: self.get(ServiceFactory).create_project_management_services()
        )
        
        logger.info("DIContainer initialized with default services")
    
    def register_singleton(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a singleton service"""
        key = self._get_service_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered singleton: {key}")
    
    def register_factory(self, service_name: str, factory: Callable[[], Any]) -> None:
        """Register a factory function"""
        self._factories[service_name] = factory
        logger.debug(f"Registered factory: {service_name}")
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a specific instance"""
        key = self._get_service_key(service_type)
        self._services[key] = instance
        logger.debug(f"Registered instance: {key}")
    
    def get(self, service_type: Type[T]) -> T:
        """Get service instance by type"""
        key = self._get_service_key(service_type)
        return self._get_service(key)
    
    def get_by_name(self, service_name: str) -> Any:
        """Get service instance by name"""
        return self._get_service(service_name)
    
    def _get_service(self, key: str) -> Any:
        """Internal method to get service instance"""
        
        # Check if already instantiated singleton
        if key in self._singletons:
            return self._singletons[key]
        
        # Check if direct instance is registered
        if key in self._services:
            return self._services[key]
        
        # Check if factory is available
        if key in self._factories:
            instance = self._factories[key]()
            
            # Store as singleton if it's a type-based registration
            if '.' in key:  # Type-based keys contain module path
                self._singletons[key] = instance
            
            return instance
        
        raise ValueError(f"Service not registered: {key}")
    
    def _get_service_key(self, service_type: Type) -> str:
        """Generate service key from type"""
        return f"{service_type.__module__}.{service_type.__name__}"
    
    def configure_for_testing(self):
        """Configure container for testing with mock services"""
        logger.info("Configuring DIContainer for testing")
        
        # Register mock implementations here if needed
        # Example:
        # self.register_singleton(IProjectRepository, lambda: MockProjectRepository())
    
    def configure_for_production(self):
        """Configure container for production with real implementations"""
        logger.info("Configuring DIContainer for production")
        
        # Register production implementations
        # Example:
        # self.register_singleton(IProjectRepository, lambda: DatabaseProjectRepository())
    
    def health_check(self) -> Dict[str, str]:
        """Check health of registered services"""
        health_status = {}
        
        for service_key in self._factories.keys():
            try:
                self._get_service(service_key)
                health_status[service_key] = "healthy"
            except Exception as e:
                health_status[service_key] = f"unhealthy: {str(e)}"
                logger.error(f"Health check failed for {service_key}: {e}")
        
        return health_status


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get global dependency injection container"""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container():
    """Reset global container (useful for testing)"""
    global _container
    _container = None


# Convenience functions
def get_service(service_type: Type[T]) -> T:
    """Get service from global container"""
    return get_container().get(service_type)


def get_service_by_name(service_name: str) -> Any:
    """Get service by name from global container"""
    return get_container().get_by_name(service_name)
