"""Milestone Agent - Creates timeline and milestone planning"""
from typing import List, Dict, Any
import uuid
import os
from datetime import datetime, timedelta
from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType, MilestoneData, Priority
)
from ..a2a.ai_service import ai_service
from .base_agent import BaseAgent


class MilestoneAgent(BaseAgent):
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.getenv('MILESTONE_PORT', '9002'))
        super().__init__("Milestone", AgentType.milestone, port)
        
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Milestone Agent",
            version="1.0.0",
            description="Milestone agent that creates timeline planning and milestone breakdowns",
            agent_type=AgentType.milestone,
            capabilities=[
                "timeline_planning",
                "milestone_creation",
                "deadline_estimation",
                "project_phasing"
            ],
            endpoints={
                "base_url": f"http://localhost:{self.port}",
                "send_message": f"http://localhost:{self.port}/api/send_message"
            },
            contact={
                "email": "milestone@taskmanagement.com"
            }
        )
    
    async def process_message(self, request: SendMessageRequest) -> MessageResponse:
        """Process milestone planning request"""
        message = request.params.message
        content = message.parts[0].root.text
        
        # Extract project information
        project_info = self.extract_project_info(content)
        
        # Create milestone plan
        milestones = await self.create_milestone_plan(project_info)
        
        # Generate response
        response_text = self.format_milestone_response(milestones)
        
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(response_text),
            milestones=milestones
        )
    
    def extract_project_info(self, content: str) -> Dict[str, Any]:
        """Extract project information from the request"""
        # Simple extraction - in a real implementation, this could use NLP
        lines = content.lower().split('\n')
        
        project_info = {
            "complexity": "medium",
            "estimated_weeks": 8,
            "has_research": any("research" in line or "analysis" in line for line in lines),
            "has_development": any("develop" in line or "build" in line or "create" in line for line in lines),
            "has_testing": any("test" in line or "quality" in line for line in lines),
            "has_deployment": any("deploy" in line or "launch" in line for line in lines)
        }
        
        return project_info
    
    async def create_milestone_plan(self, project_info: Dict[str, Any]) -> List[MilestoneData]:
        """Create AI-powered milestone breakdown"""
        milestones = []
        current_date = datetime.now()
        
        # Try to use AI for smarter milestone planning
        try:
            if ai_service.enable_ai:
                # Extract mission from project_info if available
                mission = project_info.get('original_mission', 'Project milestone planning')
                ai_milestones = await ai_service.generate_smart_milestones(mission, project_info)
                
                if ai_milestones:
                    for i, ai_milestone in enumerate(ai_milestones):
                        weeks_offset = sum(m.get('duration_weeks', 2) for m in ai_milestones[:i])
                        deadline = (current_date + timedelta(weeks=weeks_offset + ai_milestone.get('duration_weeks', 2)))
                        
                        milestones.append(MilestoneData(
                            name=ai_milestone.get('name', f'Milestone {i+1}'),
                            description=f"{ai_milestone.get('description', '')} | Deliverables: {', '.join(ai_milestone.get('deliverables', []))}",
                            deadline=deadline.strftime("%Y-%m-%d"),
                            priority=Priority.high if ai_milestone.get('critical_path', False) else Priority.medium
                        ))
                    
                    return milestones
        except Exception as e:
            print(f"⚠️ AI milestone generation failed, using fallback: {e}")
        
        # Fallback to original logic
        if project_info.get("has_research", True):
            milestones.append(MilestoneData(
                name="Planning & Research",
                description="AI-enhanced project initiation, requirements gathering, and research phase",
                deadline=(current_date + timedelta(weeks=2)).strftime("%Y-%m-%d"),
                priority=Priority.high
            ))
        
        milestones.append(MilestoneData(
            name="Design & Architecture",
            description="System design, architecture planning, and technical specifications",
            deadline=(current_date + timedelta(weeks=4)).strftime("%Y-%m-%d"),
            priority=Priority.high
        ))
        
        if project_info.get("has_development", True):
            milestones.append(MilestoneData(
                name="Development Phase",
                description="Core development and implementation of features",
                deadline=(current_date + timedelta(weeks=6)).strftime("%Y-%m-%d"),
                priority=Priority.medium
            ))
        
        if project_info.get("has_testing", True):
            milestones.append(MilestoneData(
                name="Testing & Quality Assurance",
                description="Testing, bug fixes, and quality assurance",
                deadline=(current_date + timedelta(weeks=7)).strftime("%Y-%m-%d"),
                priority=Priority.medium
            ))
        
        if project_info.get("has_deployment", True):
            milestones.append(MilestoneData(
                name="Deployment & Launch",
                description="Deployment, launch preparation, and go-live",
                deadline=(current_date + timedelta(weeks=8)).strftime("%Y-%m-%d"),
                priority=Priority.high
            ))
        
        return milestones
    
    def format_milestone_response(self, milestones: List[MilestoneData]) -> str:
        """Format milestone plan as readable text"""
        response = "[MILESTONES] MILESTONE PLAN:\n\n"
        
        for i, milestone in enumerate(milestones, 1):
            response += f"[M{i}] {milestone.name}\n"
            response += f"     [DESC] {milestone.description}\n"
            response += f"     [DEADLINE] {milestone.deadline}\n"
            response += f"     [PRIORITY] {milestone.priority.value.upper()}\n\n"
        
        response += f"[SUMMARY] Total Duration: {len(milestones) * 2} weeks\n"
        response += "[STATUS] Milestone planning complete - ready for task breakdown"
        
        return response


if __name__ == "__main__":
    agent = MilestoneAgent()
    agent.run()
