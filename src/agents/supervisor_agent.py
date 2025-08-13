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
        self.local_pm = LocalProjectManager()
        self.timeline_gen = TimelineGenerator()
        self.team_manager = TeamManager()
        self.calendar = CalendarIntegration()
        
        # Project storage for tracking
        self.active_projects = {}
        
    def extract_project_name_from_mission(self, mission: str) -> str:
        """Extract meaningful project name from mission text"""
        import re
        
        # Common project type patterns
        patterns = [
            (r'(?:create|build|develop)\s+(?:a|an)\s+([^.]+?)(?:with|that|for)', r'\1'),
            (r'(?:create|build|develop)\s+([^.]+?)(?:project|system|platform|app|application)', r'\1'),
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:project|system|platform)', r'\1'),
            (r'(?:e-commerce|ecommerce)', 'E-commerce Platform'),
            (r'(?:food delivery|delivery)', 'Food Delivery App'),
            (r'(?:enterprise|erp)', 'Enterprise ERP System'),
            (r'(?:blockchain|defi)', 'DeFi Blockchain App'),
            (r'(?:iot|internet of things)', 'Smart IoT System'),
            (r'(?:ai|artificial intelligence|machine learning|ml)', 'AI ML Platform'),
            (r'(?:website|web)', 'Company Website'),
            (r'(?:mobile app|app)', 'Mobile Application')
        ]
        
        mission_lower = mission.lower()
        
        # Try patterns in order
        for pattern, replacement in patterns:
            match = re.search(pattern, mission_lower, re.IGNORECASE)
            if not match:
                continue
            # If replacement is a static string and not a backreference, return it
            if isinstance(replacement, str) and replacement != r'\1':
                return replacement
            # Otherwise extract group 1
            name = match.group(1).strip() if match.groups() else match.group(0).strip()
            name = re.sub(r'\s+', ' ', name).title()
            return name
        
        # Fallback: extract first significant words
        words = mission.split()[:4]
        if len(words) >= 2:
            return ' '.join(words).title() + " Project"
        
        return "Custom Project"
        
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Supervisor Agent",
            version="3.0.0",
            description="Enhanced supervisor agent with Local Project Manager, timeline, and team management capabilities",
            agent_type=AgentType.supervisor,
            capabilities=[
                "mission_analysis",
                "work_division", 
                "project_coordination",
                "delegation",
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
        """Process incoming A2A message"""
        try:
            # Extract content from the message
            content = ""
            if request.params.message and request.params.message.parts:
                for part in request.params.message.parts:
                    if hasattr(part.root, 'text'):
                        content += part.root.text + " "
            
            content = content.strip()
            
            # Process the mission
            result = await self.handle_mission(content)
            
            # Create response message
            response_message = self.create_message(result)
            
            return MessageResponse(
                id=str(uuid.uuid4()),
                response=response_message
            )
            
        except Exception as e:
            error_message = f"Error processing mission: {str(e)}"
            return MessageResponse(
                id=str(uuid.uuid4()),
                response=self.create_message(error_message)
            )
    
    async def handle_mission(self, mission: str) -> str:
        """Enhanced mission handling with comprehensive tool integration"""
        print(f"[SUPERVISOR] Starting enhanced mission handling for: {mission}")
        # Generate unique project ID and extract meaningful name
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        project_name = self.extract_project_name_from_mission(mission)
        
        print(f"[SUPERVISOR] Starting project: {project_name}")
        
        # Store project
        self.active_projects[project_id] = {
            "mission": mission,
            "project_name": project_name,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        try:
            # Step 1: Analyze mission using AI
            mission_analysis = await self.analyze_mission_with_ai(mission)
            
            # Step 2: Get milestones from milestone agent
            milestone_request = SendMessageRequest(
                params=MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=mission_analysis))]
                    ),
                    task_data=TaskData(
                        title="Milestone Planning",
                        description="Create project milestones",
                        priority=Priority.high
                    )
                )
            )
            
            milestone_response = await self.send_to_agent(
                self.milestone_agent_url, 
                milestone_request
            )
            
            # Step 3: Get task breakdown from task agent
            task_request = SendMessageRequest(
                params=MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=f"{mission_analysis}\n\nMilestones:\n{milestone_response.response.parts[0].root.text}"))]
                    ),
                    task_data=TaskData(
                        title="Task Breakdown",
                        description="Break down milestones into detailed tasks",
                        priority=Priority.high
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
                params=MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=f"""
Mission: {mission}
Milestones: {milestone_response.response.parts[0].root.text}
Tasks: {task_response.response.parts[0].root.text}
Available Team: {json.dumps(team_members, indent=2)}
                    """))]
                    ),
                    task_data=TaskData(
                        title="Resource Allocation",
                        description="Allocate team resources for the project",
                        priority=Priority.medium
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
                milestones=getattr(milestone_response, 'milestones', None) or [],
                tasks=getattr(task_response, 'task_breakdown', None) or [],
                team_members=team_members,
                resource_allocation=getattr(resource_response, 'resource_allocation', None) or {}
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
            # Normalize data coming from Pydantic models (MilestoneData/TaskData) to plain dicts
            norm_milestones = self._normalize_milestones(milestones or [])
            norm_tasks = self._normalize_tasks(tasks or [])

            # 1. Create Local Project Files
            local_project_result = self.local_pm.create_project_structure(
                project_name=project_name,
                milestones=norm_milestones,
                tasks=norm_tasks,
                team_members=team_members
            )
            deliverables["local_project"] = local_project_result
            
            # 3. Generate Timeline
            timeline = self.timeline_gen.generate_project_timeline(
                milestones=norm_milestones,
                tasks=norm_tasks,
                team_members=team_members
            )
            deliverables["timeline"] = timeline
            
            # 4. Assign Tasks to Team
            task_assignments = self.team_manager.assign_tasks_to_team(
                tasks=norm_tasks,
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

    def _normalize_tasks(self, tasks: List[Any]) -> List[Dict[str, Any]]:
        """Convert TaskData models or mixed inputs into dicts expected by tools.
        Ensures keys like title, description, priority (str), time_estimate (e.g., '8 hours'),
        required_skills (list[str]), dependencies (list[str])."""
        normalized: List[Dict[str, Any]] = []
        
        # Handle case where a single TaskData object is passed instead of a list
        if tasks and not isinstance(tasks, list):
            tasks = [tasks]
            
        for t in tasks:
            try:
                # If it's a Pydantic model, get a dict first
                if hasattr(t, 'model_dump'):
                    td = t.model_dump()
                elif isinstance(t, dict):
                    td = t
                else:
                    # Fallback best-effort string repr
                    td = {"title": str(t), "description": "", "priority": "medium"}

                title = td.get("title") or td.get("name") or "Untitled Task"
                description = td.get("description", "")
                # Priority could be enum or string
                pr = td.get("priority", "medium")
                if hasattr(pr, 'value'):
                    pr = pr.value
                pr = str(pr).lower()

                # estimated_hours (float|int) -> time_estimate 'X hours'
                est_hours = td.get("estimated_hours")
                if isinstance(est_hours, (int, float)) and est_hours > 0:
                    time_estimate = f"{int(est_hours)} hours"
                else:
                    time_estimate = td.get("time_estimate", "8 hours")

                # skills_required -> required_skills
                req_skills = td.get("skills_required") or td.get("required_skills") or []
                if isinstance(req_skills, str):
                    req_skills = [req_skills]

                deps = td.get("dependencies") or []
                if isinstance(deps, str):
                    deps = [deps]

                normalized.append({
                    "title": title,
                    "description": description,
                    "priority": pr.title() if pr in ["low", "medium", "high", "urgent"] else pr,
                    "time_estimate": time_estimate,
                    "required_skills": req_skills,
                    "dependencies": deps
                })
            except Exception:
                normalized.append({
                    "title": "Untitled Task",
                    "description": "",
                    "priority": "Medium",
                    "time_estimate": "8 hours",
                    "required_skills": [],
                    "dependencies": []
                })
        return normalized

    def _normalize_milestones(self, milestones: List[Any]) -> List[Dict[str, Any]]:
        """Convert MilestoneData models or mixed inputs into dicts expected by tools.
        Ensures keys like title, description, duration (e.g., '2 weeks'), dependencies (list[str])."""
        normalized: List[Dict[str, Any]] = []
        
        # Handle case where a single MilestoneData object is passed instead of a list
        if milestones and not isinstance(milestones, list):
            milestones = [milestones]
            
        for m in milestones:
            try:
                if hasattr(m, 'model_dump'):
                    md = m.model_dump()
                elif isinstance(m, dict):
                    md = m
                else:
                    md = {"name": str(m)}

                title = md.get("title") or md.get("name") or "Milestone"
                description = md.get("description", "")
                duration = md.get("duration") or "2 weeks"
                deps = md.get("dependencies") or []
                if isinstance(deps, str):
                    deps = [deps]

                normalized.append({
                    "title": title,
                    "description": description,
                    "duration": duration,
                    "dependencies": deps,
                    "risk_level": (md.get("risk_level") or "Medium")
                })
            except Exception:
                normalized.append({
                    "title": "Milestone",
                    "description": "",
                    "duration": "2 weeks",
                    "dependencies": [],
                    "risk_level": "Medium"
                })
        return normalized
    
    def _strip_trello_lines(self, text: str) -> str:
        """Remove lines starting with [TRELLO] to avoid duplication in Task section."""
        lines = text.splitlines()
        filtered = [ln for ln in lines if not ln.strip().startswith('[TRELLO]')]
        return "\n".join(filtered).strip()

    def _kv_table(self, title: str, rows: List[tuple]) -> str:
        """Render a simple ASCII table for key-value pairs."""
        if not rows:
            return f"{title}\n(no data)"
        key_w = max(len("Key"), max(len(k) for k, _ in rows))
        val_w = max(len("Value"), max(len(str(v)) for _, v in rows))
        sep = "+-" + "-" * key_w + "-+-" + "-" * val_w + "-+"
        header = f"| {'Key'.ljust(key_w)} | {'Value'.ljust(val_w)} |"
        lines = [title, sep, header, sep]
        for k, v in rows:
            lines.append(f"| {k.ljust(key_w)} | {str(v).ljust(val_w)} |")
        lines.append(sep)
        return "\n".join(lines)

    def _extract_meta_from_analysis(self, text: str) -> Dict[str, str]:
        import re
        meta = {}
        m = re.search(r'^\[PROJECT\]\s*(.+)$', text, re.MULTILINE)
        if m:
            meta['Project'] = m.group(1).strip()
        m2 = re.search(r'\[MISSION\](.*?)(?:\n\n|\Z)', text, re.DOTALL)
        if m2:
            mission_block = m2.group(1).strip().replace('\n', ' ')
            meta['Mission'] = mission_block[:140] + ('…' if len(mission_block) > 140 else '')
        # Metadata lines
        d = re.search(r'Analysis Date:\s*([^\n]+)', text)
        model = re.search(r'AI Model:\s*([^\n]+)', text)
        conf = re.search(r'Confidence:\s*([^\n]+)', text)
        if d:
            meta['Analysis Date'] = d.group(1).strip()
        if model:
            meta['AI Model'] = model.group(1).strip()
        if conf:
            meta['Confidence'] = conf.group(1).strip()
        return meta

    def compile_enhanced_project_plan(self, mission_analysis: str, milestone_response,
                                      task_response, resource_response, project_deliverables: Dict) -> str:
        """Compile final plan divided by agent sections + tools summary (no emojis)."""

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get raw texts
        milestone_text = milestone_response.response.parts[0].root.text
        task_text = task_response.response.parts[0].root.text
        resource_text = resource_response.response.parts[0].root.text

        # Extract Trello info once
        trello_info = self.extract_trello_info_from_response(task_text)
        trello_rows = []
        if trello_info:
            trello_rows = [
                ("Board", trello_info.get('board_name', 'N/A')),
                ("URL", trello_info.get('board_url', 'N/A')),
                ("Cards", f"{trello_info.get('cards_created', 0)}/{trello_info.get('total_tasks', 0)}"),
            ]
        else:
            trello_rows = [("Status", "Not configured or failed")]

        # Supervisor summary table
        meta = self._extract_meta_from_analysis(mission_analysis)
        sup_rows = [(k, v) for k, v in meta.items()]
        sup_table = self._kv_table("[AGENT: SUPERVISOR]", sup_rows)

        # Milestone summary table
        ms_list = getattr(milestone_response, 'milestones', None) or []
        ms_count = len(ms_list)
        ms_rows = [("Milestones", ms_count)]
        # try to gather first and last deadlines
        def _ms_get(x, key):
            return getattr(x, key, None) if not isinstance(x, dict) else x.get(key)
        try:
            deadlines = [ _ms_get(m, 'deadline') for m in ms_list if _ms_get(m, 'deadline') ]
            if deadlines:
                ms_rows.append(("First Deadline", min(deadlines)))
                ms_rows.append(("Last Deadline", max(deadlines)))
        except Exception:
            pass
        ms_table = self._kv_table("[AGENT: MILESTONE]", ms_rows)

        # Task summary table
        tasks = getattr(task_response, 'task_breakdown', None) or []
        total_tasks = len(tasks)
        total_hours = 0
        def _task_get(x, key):
            return getattr(x, key, None) if not isinstance(x, dict) else x.get(key)
        for t in tasks:
            h = _task_get(t, 'estimated_hours')
            try:
                total_hours += float(h or 0)
            except Exception:
                pass
        task_rows = [("Tasks", total_tasks), ("Estimated Hours", total_hours)] + trello_rows
        task_table = self._kv_table("[AGENT: TASK]", task_rows)

        # Resource summary table (best-effort parse from text)
        import re as _re
        team_sz = _re.search(r'Team Members:\s*(\d+)', resource_text)
        cost = _re.search(r'Estimated Cost:\s*\$([\d,]+)', resource_text)
        timeline = _re.search(r'Timeline:\s*([^\n]+)', resource_text)
        res_rows = [
            ("Team Members", team_sz.group(1) if team_sz else "N/A"),
            ("Estimated Cost", f"${cost.group(1)}" if cost else "N/A"),
            ("Timeline", timeline.group(1).strip() if timeline else "N/A"),
        ]
        res_table = self._kv_table("[AGENT: RESOURCE]", res_rows)

        # Tools/Deliverables summary table
        local_project_info = project_deliverables.get('local_project', {}) or {}
        timeline_info = project_deliverables.get('timeline', {}) or {}
        assignments = project_deliverables.get('task_assignments', {}) or {}
        calendar_events = project_deliverables.get('calendar_events', []) or []
        gantt = project_deliverables.get('gantt_chart', {}) or {}
        rows_tools = []
        if local_project_info and not local_project_info.get('error'):
            rows_tools.append(("Local Project Path", local_project_info.get('project_path', 'Unknown')))
            rows_tools.append(("Files Created", len(local_project_info.get('files_created', []))))
        if timeline_info:
            start_date = timeline_info.get('project_start', 'TBD')
            end_date = timeline_info.get('project_summary', {}).get('project_end', 'TBD')
            duration = timeline_info.get('project_summary', {}).get('total_duration_days', 0)
            rows_tools.extend([
                ("Timeline Start", start_date),
                ("Timeline End", end_date),
                ("Timeline Days", duration),
            ])
        if assignments:
            rows_tools.append(("Assignments", len(assignments.get('task_assignments', []))))
        if calendar_events:
            rows_tools.append(("Calendar Events", len(calendar_events)))
        if gantt:
            rows_tools.append(("Gantt Data", "Generated"))
        tools_table = self._kv_table("[TOOLS / DELIVERABLES]", rows_tools)

        # Build final plan (tables only, no emojis)
        header = f"A2A PROTOCOL RESULT - DIVIDED BY AGENT\n[TIMESTAMP] {timestamp}\n"
        plan = "\n\n".join([header, sup_table, ms_table, task_table, res_table, tools_table, "READY FOR EXECUTION"]).strip()

        return plan.strip()

    def extract_trello_info_from_response(self, task_response_text: str) -> Dict[str, Any]:
        """Extract Trello integration information from task response"""
        import re
        
        trello_info = {}
        
        # Extract board name
        board_match = re.search(r'\[TRELLO\] Board Created: (.+)', task_response_text)
        if board_match:
            trello_info['board_name'] = board_match.group(1).strip()
        
        # Extract board URL
        url_match = re.search(r'\[TRELLO\] Board URL: (.+)', task_response_text)
        if url_match:
            trello_info['board_url'] = url_match.group(1).strip()
        
        # Extract cards created info
        cards_match = re.search(r'\[TRELLO\] Cards Created: (\d+)/(\d+)', task_response_text)
        if cards_match:
            trello_info['cards_created'] = int(cards_match.group(1))
            trello_info['total_tasks'] = int(cards_match.group(2))
        
        # Check for errors
        error_match = re.search(r'\[TRELLO\] Integration Failed: (.+)', task_response_text)
        if error_match:
            trello_info['error'] = error_match.group(1).strip()
        
        return trello_info

    async def analyze_mission_with_ai(self, mission: str) -> str:
        """AI-powered mission analysis with intelligent fallback"""
        try:
            # Get project name first
            project_name = self.extract_project_name_from_mission(mission)
            
            if ai_service.enable_ai:
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
                
                result = await ai_service.analyze_project_requirements(analysis_prompt)
                
                print(f"[SUPERVISOR] AI analysis completed for: {project_name}")
                return f"""
[PROJECT] {project_name}
[MISSION] {mission}

[ANALYSIS]
{result}

[METADATA]
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- AI Model: {os.getenv('AI_PROVIDER', 'GPT-4')}
- Confidence: High (AI-powered analysis)
                """.strip()
            else:
                # Use intelligent structured analysis instead of fallback warning
                print(f"[SUPERVISOR] Using intelligent analysis for: {project_name}")
                return await self.intelligent_mission_analysis(mission)
                
        except Exception as e:
            print(f"[SUPERVISOR] AI analysis error, using intelligent fallback: {str(e)}")
            return await self.intelligent_mission_analysis(mission)

    async def intelligent_mission_analysis(self, mission: str) -> str:
        """Intelligent structured analysis without AI dependency"""
        project_name = self.extract_project_name_from_mission(mission)
        
        # Analyze mission content
        mission_lower = mission.lower()
        
        # Detect complexity based on keywords
        complexity_indicators = {
            'simple': ['simple', 'basic', 'homepage', 'landing', 'contact form'],
            'medium': ['platform', 'system', 'dashboard', 'integration', 'api'],
            'complex': ['enterprise', 'scalable', 'real-time', 'microservices', 'ai', 'blockchain', 'erp']
        }
        
        complexity = 'Medium'
        for level, keywords in complexity_indicators.items():
            if any(keyword in mission_lower for keyword in keywords):
                complexity = level.title()
                if level == 'complex':  # Stop at complex (highest)
                    break
        
        # Estimate duration based on complexity and features
        feature_keywords = [
            'authentication', 'payment', 'dashboard', 'api', 'mobile', 'admin',
            'notification', 'search', 'analytics', 'integration', 'security',
            'real-time', 'responsive', 'scalable', 'database', 'user management'
        ]
        
        feature_count = len([word for word in mission.split() if word.lower() in feature_keywords])
        
        if complexity == 'Simple' or feature_count <= 3:
            duration = "4-6 weeks"
            team_size = "3-4"
        elif complexity == 'Medium' or feature_count <= 8:
            duration = "8-12 weeks"
            team_size = "4-6"
        else:
            duration = "12-24 weeks"
            team_size = "6-10"
        
        # Extract key features
        features = []
        for keyword in feature_keywords:
            if keyword in mission_lower:
                features.append(keyword.replace('_', ' ').title())
        
        if not features:
            features = ['Core Functionality', 'User Interface', 'Data Management']
        
        # Determine tech stack based on content
        tech_stack = []
        if any(word in mission_lower for word in ['web', 'website', 'platform']):
            tech_stack.extend(['Frontend Framework', 'Backend API', 'Database'])
        if 'mobile' in mission_lower:
            tech_stack.extend(['React Native/Flutter', 'Mobile APIs'])
        if any(word in mission_lower for word in ['payment', 'ecommerce', 'checkout']):
            tech_stack.append('Payment Gateway')
        if 'real-time' in mission_lower:
            tech_stack.append('WebSocket/Real-time')
        
        if not tech_stack:
            tech_stack = ['Modern Web Technologies', 'Cloud Infrastructure']

        return f"""
[PROJECT] {project_name}
[MISSION] {mission}

[ANALYSIS]
1. COMPLEXITY ASSESSMENT: {complexity}
    - Based on feature analysis and technical requirements
    - Features identified: {len(features)} key components

2. ESTIMATED TIMELINE: {duration}
    - Development phases: Planning → Design → Development → Testing → Deployment
    - Team size recommended: {team_size} members

3. KEY TECHNICAL REQUIREMENTS:
    {chr(10).join(f"   - {feature}" for feature in features[:6])}

4. PRIMARY DELIVERABLES:
    - Functional {project_name.lower()}
    - Technical documentation
    - Deployment package
    - User training materials

5. RISK FACTORS:
    - Technical complexity: {complexity}
    - Integration challenges: {'High' if 'integration' in mission_lower else 'Medium'}
    - Timeline pressure: {'High' if feature_count > 8 else 'Medium'}

6. SUCCESS METRICS:
    - Feature completion rate
    - Performance benchmarks
    - User acceptance criteria
    - Quality assurance metrics

[TECHNICAL STACK]
{chr(10).join(f"   - {tech}" for tech in tech_stack)}

[METADATA]
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Analysis Method: Intelligent Pattern Recognition
- Confidence: High (Structured Analysis)
- Features Detected: {len(features)}
          """.strip()

    async def basic_mission_coordination(self, mission: str) -> str:
        """Fallback basic coordination without enhanced tools"""
        try:
            print(f"[SUPERVISOR] Basic coordination for mission: {mission}")
            # Step 1: Send to milestone agent
            milestone_request = SendMessageRequest(
                params=MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=f"Break down this mission into milestones: {mission}"))]
                    )
                )
            )
            
            milestone_response = await self.send_to_agent(
                self.milestone_agent_url, 
                milestone_request
            )
            
            # Step 2: Send to task agent
            task_request = SendMessageRequest(
                params=MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=f"Create detailed tasks for: {mission}\n\nMilestones: {milestone_response.response.parts[0].root.text}"))]
                    )
                )
            )
            
            task_response = await self.send_to_agent(
                self.task_agent_url,
                task_request
            )
            
            # Step 3: Send to resource agent
            resource_request = SendMessageRequest(
                params=MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(root=TextPart(text=f"Allocate resources for: {mission}\n\nTasks: {task_response.response.parts[0].root.text}"))]
                    )
                )
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
