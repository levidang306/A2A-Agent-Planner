"""
Configuration management for A2A system
"""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    database: str = "a2a_system"


@dataclass
class TrelloConfig:
    """Trello integration configuration"""
    api_key: str = ""
    api_secret: str = ""
    enabled: bool = False


@dataclass
class GitHubConfig:
    """GitHub integration configuration"""
    token: str = ""
    enabled: bool = False


@dataclass
class AgentConfig:
    """Individual agent configuration"""
    name: str
    port: int
    host: str = "localhost"
    timeout: int = 30


@dataclass
class AIServiceConfig:
    """AI service configuration"""
    provider: str = "gemini"
    api_key: str = ""
    model: str = "gemini-pro"
    max_tokens: int = 4096


@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    
    # Service configurations
    database: DatabaseConfig
    trello: TrelloConfig
    github: GitHubConfig
    ai_service: AIServiceConfig
    
    # Agent configurations
    supervisor_agent: AgentConfig
    milestone_agent: AgentConfig
    task_agent: AgentConfig
    resource_agent: AgentConfig


class ConfigurationManager:
    """Centralized configuration management"""
    
    _instance: Optional['ConfigurationManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls) -> 'ConfigurationManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_config(self, config_path: Optional[str] = None) -> AppConfig:
        """Load configuration from environment variables and .env file"""
        if self._config is not None:
            return self._config
        
        # Load from .env file if it exists
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / ".env"
        
        if Path(config_path).exists():
            self._load_env_file(config_path)
        
        # Create configuration from environment variables
        self._config = AppConfig(
            debug=self._get_bool_env("DEBUG", False),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            environment=os.getenv("ENVIRONMENT", "development"),
            
            database=DatabaseConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                username=os.getenv("DB_USERNAME", ""),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "a2a_system")
            ),
            
            trello=TrelloConfig(
                api_key=os.getenv("API_KEY_TRELLO", ""),
                api_secret=os.getenv("API_SECRET_TRELLO", ""),
                enabled=bool(os.getenv("API_KEY_TRELLO"))
            ),
            
            github=GitHubConfig(
                token=os.getenv("GITHUB_TOKEN", ""),
                enabled=bool(os.getenv("GITHUB_TOKEN"))
            ),
            
            ai_service=AIServiceConfig(
                provider=os.getenv("AI_PROVIDER", "gemini"),
                api_key=os.getenv("GEMINI_API_KEY", ""),
                model=os.getenv("AI_MODEL", "gemini-pro"),
                max_tokens=int(os.getenv("AI_MAX_TOKENS", "4096"))
            ),
            
            supervisor_agent=AgentConfig(
                name="supervisor",
                port=int(os.getenv("SUPERVISOR_PORT", "9001"))
            ),
            
            milestone_agent=AgentConfig(
                name="milestone",
                port=int(os.getenv("MILESTONE_PORT", "9002"))
            ),
            
            task_agent=AgentConfig(
                name="task",
                port=int(os.getenv("TASK_PORT", "9003"))
            ),
            
            resource_agent=AgentConfig(
                name="resource",
                port=int(os.getenv("RESOURCE_PORT", "9004"))
            )
        )
        
        return self._config
    
    def get_config(self) -> AppConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def _load_env_file(self, file_path: str) -> None:
        """Load environment variables from .env file"""
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception:
            pass  # Ignore file reading errors
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable"""
        value = os.getenv(key, "").lower()
        return value in ("true", "1", "yes", "on") if value else default


# Global configuration instance
config_manager = ConfigurationManager()


def get_config() -> AppConfig:
    """Get application configuration"""
    return config_manager.get_config()
