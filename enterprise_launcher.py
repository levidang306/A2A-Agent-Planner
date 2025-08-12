"""
Enterprise A2A System Launcher
Demonstrates clean architecture with dependency injection and enterprise patterns
"""
import asyncio
import logging
import signal
from typing import List
from pathlib import Path

from src.config.settings import get_config
from src.infrastructure.di_container import get_container, reset_container
from src.agents.task_agent_enterprise import TaskAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.milestone_agent import MilestoneAgent
from src.agents.resource_agent import ResourceAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('a2a_system.log')
    ]
)

logger = logging.getLogger(__name__)


class A2ASystemLauncher:
    """Enterprise system launcher with proper lifecycle management"""
    
    def __init__(self):
        self.config = get_config()
        self.container = get_container()
        self.agents: List = []
        self.running = False
    
    async def initialize_system(self):
        """Initialize the A2A system with all components"""
        logger.info("Initializing A2A Enterprise System")
        
        try:
            # Health check for all services
            health_status = self.container.health_check()
            logger.info(f"Service health check: {health_status}")
            
            # Configure container based on environment
            if self.config.environment == "production":
                self.container.configure_for_production()
            else:
                # Development or testing
                pass
            
            # Initialize agents with dependency injection
            self.agents = [
                SupervisorAgent(),  # Uses existing implementation
                MilestoneAgent(),   # Uses existing implementation
                TaskAgent(),        # Uses new enterprise implementation
                ResourceAgent()     # Uses existing implementation
            ]
            
            logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            raise
    
    async def start_system(self):
        """Start all system components"""
        logger.info("Starting A2A Enterprise System")
        
        try:
            # Start all agents concurrently
            agent_tasks = []
            for agent in self.agents:
                task = asyncio.create_task(
                    agent.start_server(),
                    name=f"{agent.__class__.__name__}_server"
                )
                agent_tasks.append(task)
            
            self.running = True
            logger.info("All agents started successfully")
            
            # Wait for all agents to run
            await asyncio.gather(*agent_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"System startup failed: {e}")
            await self.shutdown_system()
            raise
    
    async def shutdown_system(self):
        """Graceful system shutdown"""
        logger.info("Shutting down A2A Enterprise System")
        
        self.running = False
        
        # Shutdown agents
        for agent in self.agents:
            try:
                if hasattr(agent, 'stop_server'):
                    await agent.stop_server()
                else:
                    # For agents that don't have explicit stop method
                    logger.info(f"Agent {agent.__class__.__name__} stopped")
            except Exception as e:
                logger.error(f"Error stopping agent {agent.__class__.__name__}: {e}")
        
        logger.info("System shutdown complete")
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        return {
            "running": self.running,
            "environment": self.config.environment,
            "agents": [
                {
                    "name": agent.__class__.__name__,
                    "port": getattr(agent, 'port', 'unknown'),
                    "status": "running" if self.running else "stopped"
                }
                for agent in self.agents
            ],
            "configuration": {
                "debug": self.config.debug,
                "log_level": self.config.log_level,
                "trello_enabled": self.config.trello.enabled,
                "github_enabled": self.config.github.enabled,
                "ai_provider": self.config.ai_service.provider
            }
        }


class DemoScenario:
    """Demonstration of enterprise A2A system capabilities"""
    
    def __init__(self, launcher: A2ASystemLauncher):
        self.launcher = launcher
        self.config = get_config()
    
    async def run_demo_workflow(self):
        """Run a demonstration workflow showing enterprise features"""
        logger.info("Starting Enterprise A2A Demo Workflow")
        
        try:
            # Demo project description
            project_description = """
            Build an enterprise e-commerce platform with the following requirements:
            
            1. User authentication and authorization system
            2. Product catalog with search and filtering
            3. Shopping cart and checkout process
            4. Payment integration (Stripe/PayPal)
            5. Order management and tracking
            6. Admin dashboard for inventory management
            7. Mobile-responsive design
            8. API for mobile app integration
            9. Email notifications system
            10. Analytics and reporting dashboard
            
            The system should be scalable, secure, and maintainable.
            Target timeline: 3 months
            Team size: 5 developers
            """
            
            # Simulate A2A workflow
            logger.info("Simulating Supervisor -> Milestone -> Task -> Resource workflow")
            
            # Step 1: Supervisor receives mission
            logger.info("Step 1: Supervisor Agent receives project mission")
            
            # Step 2: Milestone breakdown (would be actual A2A call in real scenario)
            logger.info("Step 2: Milestone Agent creates project milestones")
            
            # Step 3: Task breakdown using enterprise TaskAgent
            logger.info("Step 3: Enterprise Task Agent breaks down milestones into tasks")
            
            # Step 4: Resource allocation
            logger.info("Step 4: Resource Agent allocates team members to tasks")
            
            # Step 5: Show final results
            logger.info("Step 5: Integration with external project management systems")
            
            # Display system status
            status = self.launcher.get_system_status()
            logger.info(f"System Status: {status}")
            
            logger.info("Demo workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Demo workflow failed: {e}")
            raise


async def signal_handler(launcher: A2ASystemLauncher):
    """Handle shutdown signals gracefully"""
    logger.info("Shutdown signal received")
    await launcher.shutdown_system()


async def main():
    """Main entry point for enterprise A2A system"""
    launcher = A2ASystemLauncher()
    
    try:
        # Setup signal handlers for graceful shutdown
        for sig in [signal.SIGINT, signal.SIGTERM]:
            if hasattr(signal, sig.name):
                asyncio.get_event_loop().add_signal_handler(
                    sig, lambda: asyncio.create_task(signal_handler(launcher))
                )
        
        # Initialize and start system
        await launcher.initialize_system()
        
        # Run demo scenario (optional)
        demo = DemoScenario(launcher)
        demo_task = asyncio.create_task(demo.run_demo_workflow())
        
        # Start system
        system_task = asyncio.create_task(launcher.start_system())
        
        # Wait for demo to complete, then let system run
        await demo_task
        
        logger.info("Demo completed. System is running. Press Ctrl+C to stop.")
        await system_task
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await launcher.shutdown_system()


if __name__ == "__main__":
    # Reset container for clean startup
    reset_container()
    
    # Run the enterprise system
    asyncio.run(main())
