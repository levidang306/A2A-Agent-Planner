"""A2A Client for inter-agent communication"""
import httpx
from typing import Optional, Dict, Any
import structlog
from .types import (
    AgentCard, SendMessageRequest, MessageResponse, 
    Message, Role, Part, TextPart, MessageSendParams
)

logger = structlog.get_logger(__name__)


class A2AClient:
    def __init__(self, httpx_client: httpx.AsyncClient, agent_card: AgentCard):
        self.httpx_client = httpx_client
        self.agent_card = agent_card
        self.base_url = agent_card.endpoints.get("base_url", "http://localhost:8000")
        logger.info(f"A2AClient initialized with base_url: {self.base_url} from agent: {agent_card.name}")
        
    async def send_message(self, request: SendMessageRequest) -> MessageResponse:
        """Send a message to this agent"""
        url = f"{self.base_url}/api/send_message"
        logger.info(f"Sending message to {url}")
        
        try:
            response = await self.httpx_client.post(
                url,
                json=request.model_dump(),
                timeout=30.0
            )
            logger.info(f"Received response with status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            return MessageResponse(**data)
            
        except httpx.RequestError as e:
            logger.error("Request failed", error=str(e), url=url, error_type=type(e).__name__)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error", status_code=e.response.status_code, url=url, response_text=e.response.text)
            raise
    
    async def get_agent_info(self) -> AgentCard:
        """Get agent card information"""
        return self.agent_card


class A2ACardResolver:
    def __init__(self, httpx_client: httpx.AsyncClient, base_url: str):
        self.httpx_client = httpx_client
        self.base_url = base_url.rstrip('/')
        
    async def get_agent_card(self, path: str = "/.well-known/agent.json") -> AgentCard:
        """Resolve agent card from the well-known endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            response = await self.httpx_client.get(url, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            return AgentCard(**data)
            
        except httpx.RequestError as e:
            logger.error("Failed to resolve agent card", error=str(e), url=url, error_type=type(e).__name__)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error resolving agent card", status_code=e.response.status_code, url=url, response_text=e.response.text)
            raise
