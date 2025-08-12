"""A2A Protocol Types and Models"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from pydantic import field_validator
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

    # Accept plain strings as TextPart directly
    @field_validator('text', mode='before')
    @classmethod
    def _coerce_text(cls, v):
        # If the incoming payload was shaped like {"root": "..."} at the TextPart level
        # or a plain string was provided, normalize it to the expected 'text' string
        if isinstance(v, dict):
            # Legacy/incorrect shape: {"root": "..."}
            if 'root' in v and isinstance(v['root'], str):
                return v['root']
            # Already correct shape
            if 'text' in v and isinstance(v['text'], str):
                return v['text']
        return v


class Part(BaseModel):
    root: TextPart

    # Coerce legacy shapes for 'root' to TextPart
    @field_validator('root', mode='before')
    @classmethod
    def _coerce_root(cls, v):
        # Allow passing plain string for root
        if isinstance(v, str):
            return { 'text': v }
        # Legacy nested shape: { 'root': '...' }
        if isinstance(v, dict) and 'text' not in v and 'root' in v and isinstance(v['root'], str):
            return { 'text': v['root'] }
        return v


class Message(BaseModel):
    role: Role
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parts: List[Part]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Accept legacy list shapes where parts items might be strings or dicts with root as string
    @field_validator('parts', mode='before')
    @classmethod
    def _coerce_parts(cls, v):
        if isinstance(v, list):
            normalized = []
            for item in v:
                # If item already looks like Part
                if isinstance(item, dict) and 'root' in item:
                    normalized.append(item)
                elif isinstance(item, str):
                    normalized.append({ 'root': item })
                else:
                    normalized.append(item)
            return normalized
        return v


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

    @field_validator('message', mode='before')
    @classmethod
    def _coerce_message(cls, v):
        # Allow raw dicts with minimal structure to be coerced into Message
        # Expect at least role and parts or a single text string
        if isinstance(v, dict):
            if 'parts' in v and isinstance(v['parts'], list):
                return v
            if 'text' in v and isinstance(v['text'], str):
                return { 'role': v.get('role', 'user'), 'parts': [{ 'root': v['text'] }] }
        return v


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
