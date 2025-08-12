"""A2A Protocol Types and Models"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageType(str, Enum):
    send_message = "send_message"
    task_assignment = "task_assignment"
    milestone_request = "milestone_request"
    resource_allocation = "resource_allocation"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class AgentType(str, Enum):
    supervisor = "supervisor"
    milestone = "milestone"
    task = "task"
    resource = "resource"


class TextPart(BaseModel):
    text: str


class Part(BaseModel):
    root: TextPart


class Message(BaseModel):
    role: Role
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parts: List[Part]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskData(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.medium
    estimated_hours: Optional[float] = None
    dependencies: List[str] = Field(default_factory=list)
    skills_required: List[str] = Field(default_factory=list)


class MilestoneData(BaseModel):
    name: str
    description: str
    deadline: Optional[str] = None
    tasks: List[TaskData] = Field(default_factory=list)
    priority: Priority = Priority.medium


class ResourceRequest(BaseModel):
    skills_needed: List[str]
    team_size: int
    duration_weeks: float
    priority: Priority = Priority.medium


class MessageSendParams(BaseModel):
    message: Message
    task_data: Optional[TaskData] = None
    milestone_data: Optional[MilestoneData] = None
    resource_request: Optional[ResourceRequest] = None


class SendMessageRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    params: MessageSendParams


class MessageResponse(BaseModel):
    id: str
    response: Message
    task_breakdown: Optional[List[TaskData]] = None
    milestones: Optional[List[MilestoneData]] = None
    resource_allocation: Optional[Dict[str, Any]] = None


class AgentCard(BaseModel):
    name: str
    version: str
    description: str
    agent_type: AgentType
    capabilities: List[str]
    endpoints: Dict[str, str]
    contact: Dict[str, str]


class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
