"""Supervisor Agent - Receives missions and divides work"""
from typing import List, Dict, Any
import uuid
import os
import json
from datetime import datetime
from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType, TaskData, Priority
)
from ..a2a.ai_service import ai_service
from .base_agent import BaseAgent

# Import new tools
from ..tools.github_integration import GitHubIntegration
from ..tools.local_project_manager import LocalProjectManager
from ..tools.timeline_generator import TimelineGenerator, CalendarIntegration
from ..tools.team_manager import TeamManager


class SupervisorAgent(BaseAgent):
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.getenv('SUPERVISOR_PORT', '9001'))
        super().__init__("Supervisor", AgentType.supervisor, port)
        
        # Known agents endpoints from environment
        self.milestone_agent_url = os.getenv('MILESTONE_URL', "http://localhost:9002")
        self.task_agent_url = os.getenv('TASK_URL', "http://localhost:9003")
        self.resource_agent_url = os.getenv('RESOURCE_URL', "http://localhost:9004")
        
        # Initialize tools
        self.github = GitHubIntegration()
        self.local_pm = LocalProjectManager()
        self.timeline_gen = TimelineGenerator()
        self.team_manager = TeamManager()
        self.calendar = CalendarIntegration()
        
        # Project storage for tracking
        self.active_projects = {}
        
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Supervisor Agent",
            version="3.0.0",
            description="Enhanced supervisor agent with GitHub Issues, Local Project Manager, timeline, and team management capabilities",
            agent_type=AgentType.supervisor,
            capabilities=[
                "mission_analysis",
                "work_division", 
                "project_coordination",
                "delegation",
                "github_issues_creation",
                "github_project_boards",
                "local_project_file_creation",
                "timeline_generation",
                "team_management",
                "gantt_chart_creation",
                "task_assignment",
                "calendar_integration"
            ],
            endpoints={
                "base_url": f"http://localhost:{self.port}",
                "send_message": f"http://localhost:{self.port}/api/send_message"
            },
            contact={
                "email": "supervisor@taskmanagement.com"
            }
        )
    
    async def process_message(self, request: SendMessageRequest) -> MessageResponse:
        """Enhanced processing with tool integration"""
        message = request.params.message
        content = message.parts[0].root.text
        
        # Generate project ID
        project_id = str(uuid.uuid4())[:8]
        project_name = await self.extract_project_name(content)
        
        # Analyze the mission
        mission_analysis = await self.analyze_mission(content)
        project_requirements = await self.extract_project_requirements(content)
        
        # Step 1: Generate team based on requirements
        team_members = self.team_manager.create_team_from_requirements(project_requirements)
        
        # Step 2: Send to Milestone Agent for timeline planning
        milestone_request = SendMessageRequest(
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(
                        text=f"Create milestone plan for: {content}\n\nMission Analysis: {mission_analysis}\n\nTeam: {json.dumps([m['role'] for m in team_members], indent=2)}"
                    ))]
                )
            )
        )
        
        milestone_response = await self.send_to_agent(
            self.milestone_agent_url, 
            milestone_request
        )
        
        # Step 3: Send milestones to Task Agent for detailed task breakdown
        task_request = SendMessageRequest(
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(
                        text=f"Break down milestones into detailed tasks:\n{milestone_response.response.parts[0].root.text}\n\nTeam Skills Available: {json.dumps({m['name']: list(m['skills'].keys()) for m in team_members}, indent=2)}"
                    ))]
                ),
                milestone_data=milestone_response.milestones[0] if milestone_response.milestones else None
            )
        )
        
        task_response = await self.send_to_agent(
            self.task_agent_url,
            task_request
        )
        
        # Step 4: Send task breakdown to Resource Agent for team allocation
        resource_request = SendMessageRequest(
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(
                        text=f"Allocate resources for task breakdown:\n{task_response.response.parts[0].root.text}\n\nAvailable Team: {json.dumps(team_members, indent=2)}"
                    ))]
                )
            )
        )
        
        resource_response = await self.send_to_agent(
            self.resource_agent_url,
            resource_request
        )
        
        # Step 5: Create comprehensive project deliverables using tools
        project_deliverables = await self.create_project_deliverables(
            project_id=project_id,
            project_name=project_name,
            milestones=milestone_response.milestones,
            tasks=task_response.task_breakdown,
            team_members=team_members,
            resource_allocation=resource_response.resource_allocation
        )
        
        # Store active project
        self.active_projects[project_id] = {
            "name": project_name,
            "created_at": datetime.now().isoformat(),
            "deliverables": project_deliverables,
            "status": "active"
        }
        
        # Compile final response with tool integrations
        final_response = self.compile_enhanced_project_plan(
            mission_analysis,
            milestone_response,
            task_response,
            resource_response,
            project_deliverables
        )
        
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(final_response),
            milestones=milestone_response.milestones,
            task_breakdown=task_response.task_breakdown,
            resource_allocation=resource_response.resource_allocation
        )
    
    async def analyze_mission(self, mission: str) -> str:
        """AI-powered mission analysis"""
        try:
            # Use AI service for intelligent analysis
            ai_analysis = await ai_service.analyze_project_requirements(mission)
            
            return f"""
[AI-ANALYSIS] AI-POWERED MISSION ANALYSIS:
[RESULT] - Project Complexity: {ai_analysis.get('complexity', 'medium').upper()}
[RESULT] - Estimated Duration: {ai_analysis.get('estimated_weeks', 8)} weeks
[RESULT] - Project Type: {ai_analysis.get('project_type', 'web').upper()}
[RESULT] - Recommended Team Size: {ai_analysis.get('recommended_team_size', 3)} members
[RESULT] - Key Technologies: {', '.join(ai_analysis.get('key_technologies', []))}
[RESULT] - Required Skills: {', '.join(ai_analysis.get('required_skills', []))}
[RESULT] - Risk Factors: {', '.join(ai_analysis.get('risk_factors', []))}
[RESULT] - Budget Category: {ai_analysis.get('budget_category', 'medium').upper()}

[STATUS] AI Analysis Complete - Proceeding with specialized agents...
            """.strip()
            
        except Exception as e:
            return f"[ERROR] AI Analysis failed: {str(e)}, using fallback analysis"
    
    async def extract_project_name(self, mission: str) -> str:
        """Extract a project name from the mission description"""
        # Simple extraction - in production, use AI
        words = mission.split()[:5]  # Take first 5 words
        project_name = " ".join(words).replace("Create", "").replace("Build", "").strip()
        return project_name[:50] if project_name else "A2A Generated Project"
    
    async def extract_project_requirements(self, mission: str) -> Dict[str, Any]:
        """Extract structured requirements from mission"""
        return {
            "description": mission,
            "complexity": "medium",  # Could use AI to determine
            "features": [],
            "timeline": "8 weeks",
            "budget": "$50,000"
        }
    
    async def create_project_deliverables(self, project_id: str, project_name: str, 
                                        milestones: List[Dict], tasks: List[Dict], 
                                        team_members: List[Dict], resource_allocation: Dict) -> Dict[str, Any]:
        """Create comprehensive project deliverables using integrated tools"""
        
        deliverables = {
            "project_id": project_id,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # 1. Create GitHub Issues and Project Board
            github_result = self.github.create_project_issues(
                project_name=project_name,
                milestones=milestones or [],
                tasks=tasks or [],
                team_members=team_members
            )
            deliverables["github_project"] = github_result
            
            # 2. Create Local Project Files
            local_project_result = self.local_pm.create_project_structure(
                project_name=project_name,
                milestones=milestones or [],
                tasks=tasks or [],
                team_members=team_members
            )
            deliverables["local_project"] = local_project_result
            
            # 2. Generate Timeline
            timeline = self.timeline_gen.generate_project_timeline(
                milestones=milestones or [],
                tasks=tasks or [],
                team_members=team_members
            )
            deliverables["timeline"] = timeline
            
            # 3. Assign Tasks to Team
            task_assignments = self.team_manager.assign_tasks_to_team(
                tasks=tasks or [],
                team_members=team_members
            )
            deliverables["task_assignments"] = task_assignments
            
            # 4. Generate Calendar Events
            calendar_events = self.calendar.create_calendar_events(timeline)
            deliverables["calendar_events"] = calendar_events
            
            # 5. Generate Gantt Chart Data
            gantt_data = self.timeline_gen.generate_gantt_chart_data(timeline)
            deliverables["gantt_chart"] = gantt_data
            
        except Exception as e:
            deliverables["error"] = f"Tool integration failed: {str(e)}"
        
        return deliverables
    
    def compile_enhanced_project_plan(self, mission_analysis: str, milestone_response, 
                                    task_response, resource_response, project_deliverables: Dict) -> str:
        """Compile comprehensive project plan with tool integrations"""
        
        plan = f"""
🚀 ENHANCED A2A PROJECT PLAN
════════════════════════════════════════════════════════════════

{mission_analysis}

📊 PROJECT DELIVERABLES & INTEGRATIONS:
════════════════════════════════════════════════════════════════

� GITHUB PROJECT CREATED:
"""
        
        # Add GitHub information
        github_info = project_deliverables.get("github_project", {})
        if github_info and not github_info.get("error"):
            plan += f"""
[REPOSITORY] {github_info.get('repository_name', 'Unknown')}
[ISSUES CREATED] {len(github_info.get('issues_created', []))} issues
[MILESTONES] {len(github_info.get('milestones_created', []))} milestones
[PROJECT BOARD] {github_info.get('project_board_url', 'Created')}
"""
            
            # List the specific issues created
            issues_created = github_info.get('issues_created', [])
            if issues_created:
                plan += "\n[GITHUB ISSUES]\n"
                for issue in issues_created[:5]:  # Show first 5 issues
                    plan += f"  • #{issue.get('number', '?')}: {issue.get('title', 'Unknown')}\n"
                if len(issues_created) > 5:
                    plan += f"  • ... and {len(issues_created) - 5} more issues\n"

�📁 LOCAL PROJECT FILES CREATED:
"""
        
        # Add Local Project information
        local_project_info = project_deliverables.get("local_project", {})
        if local_project_info and not local_project_info.get("error"):
            plan += f"""
[PROJECT PATH] {local_project_info.get('project_path', 'Unknown')}
[FILES CREATED] {len(local_project_info.get('files_created', []))} project files
[INCLUDES] CSV tasks, Gantt chart, team data, timeline JSON
"""
            
            # List the specific files created
            files_created = local_project_info.get('files_created', [])
            if files_created:
                plan += "\n[FILES]\n"
                for file_path in files_created:
                    file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
                    plan += f"  • {file_name}\n"
        
        # Add Timeline information
        timeline_info = project_deliverables.get("timeline", {})
        if timeline_info:
            plan += f"""

📅 PROJECT TIMELINE GENERATED:
[START] {timeline_info.get('project_start', 'TBD')}
[END] {timeline_info.get('project_summary', {}).get('project_end', 'TBD')}
[DURATION] {timeline_info.get('project_summary', {}).get('total_duration_days', 0)} days
[MILESTONES] {timeline_info.get('project_summary', {}).get('total_milestones', 0)} milestones
[TASKS] {timeline_info.get('project_summary', {}).get('total_tasks', 0)} tasks scheduled
"""
        
        # Add Team Assignments
        assignments = project_deliverables.get("task_assignments", {})
        if assignments:
            plan += f"""

👥 TEAM ASSIGNMENTS OPTIMIZED:
"""
            for assignment in assignments.get("task_assignments", []):
                plan += f"[TASK] {assignment['task_title']} → {assignment['assigned_to']} ({assignment['estimated_hours']}h)\n"
        
        # Add Calendar Integration
        calendar_events = project_deliverables.get("calendar_events", [])
        if calendar_events:
            plan += f"""

📆 CALENDAR EVENTS GENERATED:
[EVENTS] {len(calendar_events)} calendar events ready for import
[TYPES] Milestones, task deadlines, and team meetings
"""
        
        # Original agent responses
        plan += f"""

═══════════════════════════════════════════════════════════════
📋 DETAILED MILESTONE PLAN:
═══════════════════════════════════════════════════════════════
{milestone_response.response.parts[0].root.text}

═══════════════════════════════════════════════════════════════
📝 TASK BREAKDOWN:
═══════════════════════════════════════════════════════════════
{task_response.response.parts[0].root.text}

═══════════════════════════════════════════════════════════════
👥 RESOURCE ALLOCATION:
═══════════════════════════════════════════════════════════════
{resource_response.response.parts[0].root.text}

🎯 READY FOR EXECUTION!
The project has been fully planned and integrated with local project management files.
Check the project directory for your CSV task list, Gantt chart, and team assignments.
        """
        
        return plan.strip()
    
    def compile_project_plan(self, analysis: str, milestones, tasks, resources) -> str:
        """Compile the complete project plan"""
        return f"""
[SUMMARY] PROJECT PLAN SUMMARY

{analysis}

[MILESTONES] MILESTONES:
{milestones.response.parts[0].root.text}

[TASKS] TASK BREAKDOWN:
{tasks.response.parts[0].root.text}

[RESOURCES] RESOURCE ALLOCATION:
{resources.response.parts[0].root.text}

[COMPLETE] Project coordination complete. All specialized agents have contributed to the plan.
        """.strip()


if __name__ == "__main__":
    agent = SupervisorAgent()
    agent.run()
