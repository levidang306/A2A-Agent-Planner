"""Base Agent Class"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import structlog
from fastapi import FastAPI, HTTPException
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType
)
from ..a2a.client import A2AClient, A2ACardResolver

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    def __init__(self, name: str, agent_type: AgentType, port: int):
        self.name = name
        self.agent_type = agent_type
        self.port = port
        self.app = FastAPI(title=f"{name} Agent")
        self.clients: Dict[str, A2AClient] = {}
        
        # Load configuration from environment
        self.timeout = int(os.getenv('AGENT_TIMEOUT', '30'))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            return self.get_agent_card()
            
        @self.app.post("/api/send_message")
        async def send_message(request: SendMessageRequest):
            try:
                response = await self.process_message(request)
                return response
            except Exception as e:
                logger.error("Error processing message", error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
    
    @abstractmethod
    def get_agent_card(self) -> AgentCard:
        """Return agent card information"""
        pass
    
    @abstractmethod
    async def process_message(self, request: SendMessageRequest) -> MessageResponse:
        """Process incoming message and return response"""
        pass
    
    async def get_client(self, agent_url: str) -> A2AClient:
        """Get or create A2A client for another agent"""
        if agent_url not in self.clients:
            async with httpx.AsyncClient() as http_client:
                resolver = A2ACardResolver(http_client, agent_url)
                agent_card = await resolver.get_agent_card()
                
                # Create persistent client
                persistent_client = httpx.AsyncClient(timeout=30.0)
                self.clients[agent_url] = A2AClient(persistent_client, agent_card)
        
        return self.clients[agent_url]
    
    async def send_to_agent(self, agent_url: str, request: SendMessageRequest) -> MessageResponse:
        """Send message to another agent"""
        client = await self.get_client(agent_url)
        return await client.send_message(request)
    
    def create_message(self, content: str, role: Role = Role.assistant) -> Message:
        """Helper to create a message"""
        return Message(
            role=role,
            parts=[Part(root=TextPart(text=content))],
            timestamp=datetime.utcnow().isoformat()
        )
    
    def run(self, host: str = "0.0.0.0"):
        """Run the agent server"""
        logger.info(f"Starting {self.name} agent on {host}:{self.port}")
        uvicorn.run(self.app, host=host, port=self.port)
    
    async def cleanup(self):
        """Cleanup resources"""
        for client in self.clients.values():
            await client.httpx_client.aclose()
