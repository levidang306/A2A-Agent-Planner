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
    
    async def handle_mission(self, mission: str) -> str:
        """Enhanced mission handling with comprehensive tool integration"""
        
        # Generate unique project ID
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        project_name = f"A2A Project {datetime.now().strftime('%Y%m%d_%H%M')}"
        
        # Store project
        self.active_projects[project_id] = {
            "mission": mission,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        try:
            # Step 1: Analyze mission using AI
            mission_analysis = await self.analyze_mission_with_ai(mission)
            
            # Step 2: Get milestones from milestone agent
            milestone_request = SendMessageRequest(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(root=mission_analysis)]
                ),
                params=MessageSendParams(
                    recipient_type=AgentType.milestone,
                    task_data=TaskData(
                        task_id=project_id,
                        priority=Priority.high,
                        metadata={"original_mission": mission}
                    )
                )
            )
            
            milestone_response = await self.send_to_agent(
                self.milestone_agent_url, 
                milestone_request
            )
            
            # Step 3: Get task breakdown from task agent
            task_request = SendMessageRequest(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(root=f"{mission_analysis}\n\nMilestones:\n{milestone_response.response.parts[0].root.text}")]
                ),
                params=MessageSendParams(
                    recipient_type=AgentType.task,
                    task_data=TaskData(
                        task_id=project_id,
                        priority=Priority.high,
                        metadata={"milestones": milestone_response.milestones}
                    )
                )
            )
            
            task_response = await self.send_to_agent(
                self.task_agent_url,
                task_request
            )
            
            # Step 4: Get resource allocation from resource agent
            team_members = [
                {"name": "Senior Developer", "role": "Full-Stack Lead", "skills": {"python": 9, "react": 8}},
                {"name": "Frontend Developer", "role": "UI/UX Specialist", "skills": {"react": 9, "css": 8}},
                {"name": "Backend Developer", "role": "API Specialist", "skills": {"python": 9, "database": 8}},
                {"name": "QA Engineer", "role": "Testing Lead", "skills": {"testing": 9, "automation": 7}}
            ]
            
            resource_request = SendMessageRequest(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(root=f"""
Mission: {mission}
Milestones: {milestone_response.response.parts[0].root.text}
Tasks: {task_response.response.parts[0].root.text}
Available Team: {json.dumps(team_members, indent=2)}
                    """)]
                ),
                params=MessageSendParams(
                    recipient_type=AgentType.resource,
                    task_data=TaskData(
                        task_id=project_id,
                        priority=Priority.medium,
                        metadata={
                            "milestones": milestone_response.milestones,
                            "tasks": task_response.task_breakdown,
                            "team_members": team_members
                        }
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
            
            # Step 6: Compile enhanced project plan
            final_plan = self.compile_enhanced_project_plan(
                mission_analysis, milestone_response, task_response, 
                resource_response, project_deliverables
            )
            
            # Update project status
            self.active_projects[project_id]["status"] = "completed"
            self.active_projects[project_id]["completed_at"] = datetime.now().isoformat()
            self.active_projects[project_id]["deliverables"] = project_deliverables
            
            return final_plan
            
        except Exception as e:
            print(f"❌ Error in enhanced mission handling: {e}")
            # Fallback to basic coordination
            return await self.basic_mission_coordination(mission)
    
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
            
            # 3. Generate Timeline
            timeline = self.timeline_gen.generate_project_timeline(
                milestones=milestones or [],
                tasks=tasks or [],
                team_members=team_members
            )
            deliverables["timeline"] = timeline
            
            # 4. Assign Tasks to Team
            task_assignments = self.team_manager.assign_tasks_to_team(
                tasks=tasks or [],
                team_members=team_members
            )
            deliverables["task_assignments"] = task_assignments
            
            # 5. Generate Calendar Events
            calendar_events = self.calendar.create_calendar_events(timeline)
            deliverables["calendar_events"] = calendar_events
            
            # 6. Generate Gantt Chart Data
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

🐙 GITHUB PROJECT CREATED:
"""
        
        # Add GitHub information
        github_info = project_deliverables.get("github_project", {})
        if github_info and not github_info.get("error"):
            repo_name = github_info.get('repository_name', 'Unknown')
            issues_count = len(github_info.get('issues_created', []))
            milestones_count = len(github_info.get('milestones_created', []))
            project_url = github_info.get('project_board_url', 'Created')
            
            plan += f"""
[REPOSITORY] {repo_name}
[ISSUES CREATED] {issues_count} issues
[MILESTONES] {milestones_count} milestones
[PROJECT BOARD] {project_url}
"""
            
            # List the specific issues created
            issues_created = github_info.get('issues_created', [])
            if issues_created:
                plan += "\n[GITHUB ISSUES]\n"
                for issue in issues_created[:5]:  # Show first 5 issues
                    issue_num = issue.get('number', '?')
                    issue_title = issue.get('title', 'Unknown')
                    plan += f"  • #{issue_num}: {issue_title}\n"
                if len(issues_created) > 5:
                    plan += f"  • ... and {len(issues_created) - 5} more issues\n"

        plan += "\n📁 LOCAL PROJECT FILES CREATED:"
        
        # Add Local Project information
        local_project_info = project_deliverables.get("local_project", {})
        if local_project_info and not local_project_info.get("error"):
            project_path = local_project_info.get('project_path', 'Unknown')
            files_count = len(local_project_info.get('files_created', []))
            
            plan += f"""
[PROJECT PATH] {project_path}
[FILES CREATED] {files_count} project files
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
            start_date = timeline_info.get('project_start', 'TBD')
            end_date = timeline_info.get('project_summary', {}).get('project_end', 'TBD')
            duration = timeline_info.get('project_summary', {}).get('total_duration_days', 0)
            milestones_count = timeline_info.get('project_summary', {}).get('total_milestones', 0)
            tasks_count = timeline_info.get('project_summary', {}).get('total_tasks', 0)
            
            plan += f"""

📅 PROJECT TIMELINE GENERATED:
[START] {start_date}
[END] {end_date}
[DURATION] {duration} days
[MILESTONES] {milestones_count} milestones
[TASKS] {tasks_count} tasks scheduled
"""
        
        # Add Team Assignments
        assignments = project_deliverables.get("task_assignments", {})
        if assignments:
            plan += "\n👥 TEAM ASSIGNMENTS OPTIMIZED:\n"
            for assignment in assignments.get("task_assignments", []):
                task_title = assignment.get('task_title', 'Unknown Task')
                assigned_to = assignment.get('assigned_to', 'Unassigned')
                estimated_hours = assignment.get('estimated_hours', 0)
                plan += f"[TASK] {task_title} → {assigned_to} ({estimated_hours}h)\n"
        
        # Add Calendar Integration
        calendar_events = project_deliverables.get("calendar_events", [])
        if calendar_events:
            events_count = len(calendar_events)
            plan += f"""

📆 CALENDAR EVENTS GENERATED:
[EVENTS] {events_count} calendar events ready for import
[TYPES] Milestones, task deadlines, and team meetings
"""
        
        # Original agent responses
        milestone_text = milestone_response.response.parts[0].root.text
        task_text = task_response.response.parts[0].root.text
        resource_text = resource_response.response.parts[0].root.text
        
        plan += f"""

═══════════════════════════════════════════════════════════════
📋 DETAILED MILESTONE PLAN:
═══════════════════════════════════════════════════════════════
{milestone_text}

═══════════════════════════════════════════════════════════════
📝 TASK BREAKDOWN:
═══════════════════════════════════════════════════════════════
{task_text}

═══════════════════════════════════════════════════════════════
👥 RESOURCE ALLOCATION:
═══════════════════════════════════════════════════════════════
{resource_text}

🎯 READY FOR EXECUTION!
The project has been fully planned and integrated with GitHub Issues and local project management files.
Check your GitHub repository for issues and project board, and the local project directory for files.
        """
        
        return plan.strip()

    async def analyze_mission_with_ai(self, mission: str) -> str:
        """Use AI to analyze the mission and provide intelligent insights"""
        try:
            analysis_prompt = f"""
Analyze this project mission and provide a comprehensive breakdown:

Mission: {mission}

Please provide:
1. Project complexity assessment (Simple/Medium/Complex)
2. Estimated timeline (in weeks)
3. Key technical requirements
4. Primary deliverables
5. Risk factors
6. Success metrics

Format your response as a structured analysis suitable for project planning.
            """
            
            result = await ai_service.analyze_text(analysis_prompt)
            
            return f"""
[AI-POWERED] MISSION ANALYSIS:
════════════════════════════════════════════════════════════════

[MISSION] {mission}

[ANALYSIS]
{result}

[METADATA]
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- AI Model: {os.getenv('AI_PROVIDER', 'Unknown')}
- Confidence: High (AI-powered analysis)
            """.strip()
            
        except Exception as e:
            # Fallback to simple analysis
            return f"""
[WARNING] AI Analysis unavailable (using fallback): {str(e)}

[FALLBACK] BASIC MISSION ANALYSIS:
[INFO] - Project: {mission}
[INFO] - Complexity: Medium (estimated)
[INFO] - Estimated Duration: To be determined by milestone agent
[INFO] - Key Requirements: To be broken down by task agent
[INFO] - Resource Needs: To be allocated by resource agent
            """.strip()

    async def basic_mission_coordination(self, mission: str) -> str:
        """Fallback basic coordination without enhanced tools"""
        try:
            # Step 1: Send to milestone agent
            milestone_request = SendMessageRequest(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(root=f"Break down this mission into milestones: {mission}")]
                ),
                params=MessageSendParams(recipient_type=AgentType.milestone)
            )
            
            milestone_response = await self.send_to_agent(
                self.milestone_agent_url, 
                milestone_request
            )
            
            # Step 2: Send to task agent
            task_request = SendMessageRequest(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(root=f"Create detailed tasks for: {mission}\n\nMilestones: {milestone_response.response.parts[0].root.text}")]
                ),
                params=MessageSendParams(recipient_type=AgentType.task)
            )
            
            task_response = await self.send_to_agent(
                self.task_agent_url,
                task_request
            )
            
            # Step 3: Send to resource agent
            resource_request = SendMessageRequest(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(root=f"Allocate resources for: {mission}\n\nTasks: {task_response.response.parts[0].root.text}")]
                ),
                params=MessageSendParams(recipient_type=AgentType.resource)
            )
            
            resource_response = await self.send_to_agent(
                self.resource_agent_url,
                resource_request
            )
            
            return self.compile_project_plan(mission, milestone_response, task_response, resource_response)
            
        except Exception as e:
            return f"[ERROR] Failed to coordinate project: {str(e)}"
    
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
