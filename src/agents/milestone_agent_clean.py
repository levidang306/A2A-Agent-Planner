"""Milestone Agent - Creates timeline and milestone planning"""
from typing import List, Dict, Any, Optional
import uuid
import os
import logging
from datetime import datetime, timedelta
from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType, MilestoneData, Priority
)
from ..a2a.ai_service import ai_service
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MilestoneAgent(BaseAgent):
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.getenv('MILESTONE_PORT', '9002'))
        super().__init__("Milestone", AgentType.milestone, port)
        
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Milestone Agent",
            version="1.0.0",
            description="Milestone agent for project timeline planning",
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
        print("[MILESTONE] ======= PROCESSING MESSAGE =======")
        print("[MILESTONE] Received request for milestone planning", request)
        message = request.params.message
        content = message.parts[0].root.text
        
        print(f"[MILESTONE] Content received: {content[:100]}...")
        
        logger.info("Processing milestone planning request")
        
        # Extract project information
        project_info = self.extract_project_info(content)
        print(f"[MILESTONE] Extracted project info: {project_info.get('name', 'Unknown Project')}")
        
        # Create milestone plan
        milestones = await self.create_milestone_plan(project_info)
        print(f"[MILESTONE] Generated {len(milestones)} milestones")
        
        # Generate response
        response_text = self.format_milestone_response(milestones)
        
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(response_text),
            milestones=milestones
        )
    
    def extract_project_info(self, content: str) -> Dict[str, Any]:
        """Extract project information from the request including timeline"""
        import re
        
        lines = content.lower().split('\n')
        
        # Try to extract project name from supervisor analysis
        project_name = "Custom Project"
        project_patterns = [
            r'\[project\]\s*([^\n\r]+)',
            r'project:\s*([^\n\r]+)',
            r'project\s+name:\s*([^\n\r]+)',
            r'create\s+(?:a|an)\s+([^.]+?)(?:with|that|for|project)',
            r'build\s+(?:a|an)\s+([^.]+?)(?:with|that|for|project)',
            r'develop\s+(?:a|an)\s+([^.]+?)(?:with|that|for|project)'
        ]
        
        for pattern in project_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                if len(extracted_name) > 5 and len(extracted_name) < 100:
                    project_name = extracted_name
                    break
        
        # Extract time duration from user input or analysis
        estimated_weeks = 8  # default
        time_patterns = [
            r'(\d+)\s*weeks?',
            r'(\d+)\s*months?',
            r'(\d+)\s*days?',
            r'in\s*(\d+)\s*weeks?',
            r'within\s*(\d+)\s*weeks?',
            r'timeline:\s*(\d+)[-\s]*(\d+)?\s*weeks?',
            r'duration:\s*(\d+)[-\s]*(\d+)?\s*weeks?',
            r'estimated\s+timeline:\s*(\d+)[-\s]*(\d+)?\s*weeks?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, content.lower())
            if match:
                duration = int(match.group(1))
                # If range like "8-12 weeks", take the higher number
                if match.groups()[1:] and match.group(2):
                    duration = int(match.group(2))
                
                if 'month' in pattern:
                    estimated_weeks = duration * 4
                elif 'day' in pattern:
                    estimated_weeks = max(1, duration // 7)
                else:
                    estimated_weeks = duration
                break
        
        # Analyze content for project characteristics
        project_info = {
            "complexity": "medium",
            "estimated_weeks": estimated_weeks,
            "user_specified_duration": estimated_weeks,
            "project_name": project_name,
            "has_research": any("research" in line or "analysis" in line or "phân tích" in line for line in lines),
            "has_development": any("develop" in line or "build" in line or "create" in line or "phát triển" in line or "xây dựng" in line for line in lines),
            "has_testing": any("test" in line or "quality" in line or "kiểm thử" in line for line in lines),
            "has_deployment": any("deploy" in line or "launch" in line or "triển khai" in line for line in lines),
            "original_mission": content,
            "mission": content
        }
        
        # Detect complexity from analysis
        if "[COMPLEXITY]" in content:
            complexity_match = re.search(r'\[COMPLEXITY\]\s*([^\n\r]+)', content, re.IGNORECASE)
            if complexity_match:
                complexity = complexity_match.group(1).strip().lower()
                project_info["complexity"] = complexity
        
        print(f"[MILESTONE] Extracted project info: {project_name} ({estimated_weeks} weeks, {project_info['complexity']} complexity)")
        
        return project_info
    
    async def create_milestone_plan(self, project_info: Dict[str, Any]) -> List[MilestoneData]:
        """Create AI-powered milestone breakdown based on user timeline"""
        milestones = []
        current_date = datetime.now()
        user_weeks = project_info.get('user_specified_duration', 8)
        
        print(f"[MILESTONE] Creating timeline for {user_weeks} weeks based on user input")
        
        # Try to use AI for intelligent milestone planning with user timeline
        try:
            if ai_service.enable_ai:
                mission = project_info.get('original_mission', 'Project milestone planning')
                
                # Enhanced prompt with timeline constraints
                ai_prompt = f"""
                Analyze this project mission and create a realistic milestone plan for exactly {user_weeks} weeks:
                
                Mission: {mission}
                
                Available time: {user_weeks} weeks
                Project features needed:
                - Research/Analysis: {project_info.get('has_research', False)}
                - Development: {project_info.get('has_development', False)} 
                - Testing: {project_info.get('has_testing', False)}
                - Deployment: {project_info.get('has_deployment', False)}
                
                Create 4-6 milestones that fit within {user_weeks} weeks. Each milestone should have:
                - Realistic duration (in weeks)
                - Clear deliverables
                - Proper sequencing
                
                Focus on practical timeline that matches the user's constraints.
                """
                
                ai_milestones = await ai_service.generate_smart_milestones(ai_prompt, project_info)
                
                if ai_milestones:
                    total_weeks_used = 0
                    for i, ai_milestone in enumerate(ai_milestones):
                        duration = ai_milestone.get('duration_weeks', 2)
                        
                        # Ensure we don't exceed user timeline
                        if total_weeks_used + duration > user_weeks:
                            duration = max(1, user_weeks - total_weeks_used)
                        
                        if total_weeks_used >= user_weeks:
                            break
                            
                        start_date = current_date + timedelta(weeks=total_weeks_used)
                        end_date = current_date + timedelta(weeks=total_weeks_used + duration)
                        
                        milestones.append(MilestoneData(
                            name=ai_milestone.get('name', f'Milestone {i+1}'),
                            description=f"{ai_milestone.get('description', '')} | Deliverables: {', '.join(ai_milestone.get('deliverables', []))}",
                            deadline=end_date.strftime("%Y-%m-%d"),
                            priority=Priority.high if ai_milestone.get('critical_path', False) else Priority.medium
                        ))
                        
                        total_weeks_used += duration
                    
                    print(f"[MILESTONE] AI generated {len(milestones)} milestones using {total_weeks_used}/{user_weeks} weeks")
                    return milestones
                    
        except Exception as e:
            print(f"[MILESTONE] AI milestone generation failed, using structured fallback: {e}")
        
        # Structured fallback based on user timeline and project features
        milestone_plan = self.create_structured_milestone_plan(project_info, user_weeks, current_date)
        
        return milestone_plan
    
    def create_structured_milestone_plan(self, project_info: Dict[str, Any], total_weeks: int, start_date) -> List[MilestoneData]:
        """Create structured milestone plan based on project features and timeline"""
        milestones = []
        features = []
        
        # Determine required phases based on project features
        if project_info.get("has_research", True):
            features.append(("Planning & Research", "Project initiation, requirements gathering, and research phase"))
        
        features.append(("Design & Architecture", "System design, architecture planning, and technical specifications"))
        
        if project_info.get("has_development", True):
            features.append(("Development Phase", "Core development and implementation of features"))
        
        if project_info.get("has_testing", True):
            features.append(("Testing & Quality Assurance", "Testing, bug fixes, and quality assurance"))
        
        if project_info.get("has_deployment", True):
            features.append(("Deployment & Launch", "Deployment, launch preparation, and go-live"))
        
        # Distribute weeks among phases intelligently
        num_phases = len(features)
        base_weeks_per_phase = max(1, total_weeks // num_phases)
        extra_weeks = total_weeks % num_phases
        
        current_week = 0
        for i, (phase_name, phase_desc) in enumerate(features):
            # Give extra weeks to development and testing phases
            phase_duration = base_weeks_per_phase
            if extra_weeks > 0 and phase_name in ["Development Phase", "Testing & Quality Assurance"]:
                phase_duration += 1
                extra_weeks -= 1
            elif extra_weeks > 0 and i == len(features) - 1:
                phase_duration += extra_weeks  # Give remaining weeks to last phase
            
            milestone_date = start_date + timedelta(weeks=current_week + phase_duration)
            
            milestones.append(MilestoneData(
                name=phase_name,
                description=phase_desc,
                deadline=milestone_date.strftime("%Y-%m-%d"),
                priority=Priority.high if phase_name in ["Planning & Research", "Deployment & Launch"] else Priority.medium
            ))
            
            current_week += phase_duration
        
        print(f"[MILESTONE] Created structured plan with {len(milestones)} phases across {total_weeks} weeks")
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
