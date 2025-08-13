"""Task Agent - AI-powered intelligent task breakdown with context-aware analysis"""
from typing import List, Dict, Any, Optional
import uuid
import os
import logging
import json
import re
from datetime import datetime
from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType, TaskData, Priority
)
from .base_agent import BaseAgent
from ..tools.trello_integration import TrelloIntegration
from ..a2a.ai_service import AIService

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.getenv('TASK_PORT', '9003'))
        super().__init__("Task", AgentType.task, port)
        
        # Initialize AI service for intelligent task generation
        self.ai_service = AIService()
        logger.info(f"AI Service enabled: {self.ai_service.enable_ai}")
        
        # Initialize Trello integration
        self.trello_api_key = os.getenv('API_KEY_TRELLO')
        self.trello_api_token = os.getenv('API_TOKEN_TRELLO')
        self.trello_enabled = bool(self.trello_api_key and self.trello_api_token)
        
        if self.trello_enabled:
            self.trello = TrelloIntegration(self.trello_api_key, self.trello_api_token)
            logger.info("Task Agent initialized with Trello integration")
            print("[INIT] Trello integration enabled")
        else:
            self.trello = None
            logger.warning("Task Agent initialized without Trello integration")
            print("[INIT] Trello integration disabled - missing credentials")
        
        # Current project context
        self.current_project_context = {}
        self.current_board_id = None
        self.task_lists = {}
        
    def _extract_resources_from_context(self, content: str) -> Dict[str, Any]:
        """Extract team resources, budget, and constraints from supervisor context."""
        resources = {
            "team_size": None,
            "roles_needed": [],
            "budget_constraint": None,
            "timeline_constraint": None,
            "technology_stack": [],
            "skill_requirements": [],
            "external_dependencies": [],
            "constraints": []
        }
        
        content_lower = content.lower()
        
        # Extract team size
        team_patterns = [
            r"team\s+of\s+(\d+)",
            r"(\d+)\s+developers?",
            r"(\d+)\s+people",
            r"(\d+)\s+team\s+members?"
        ]
        for pattern in team_patterns:
            match = re.search(pattern, content_lower)
            if match:
                resources["team_size"] = int(match.group(1))
                break
        
        # Extract roles and skills needed
        role_keywords = {
            "frontend": ["frontend", "ui", "ux", "react", "vue", "angular"],
            "backend": ["backend", "api", "server", "database"],
            "fullstack": ["fullstack", "full-stack", "full stack"],
            "devops": ["devops", "deployment", "ci/cd", "docker", "kubernetes"],
            "mobile": ["mobile", "ios", "android", "react native", "flutter"],
            "blockchain": ["blockchain", "smart contract", "solidity", "web3"],
            "ai": ["ai", "machine learning", "data science", "ml"],
            "qa": ["testing", "qa", "quality assurance"],
            "designer": ["design", "ui/ux", "graphic", "visual"],
            "pm": ["project manager", "scrum master", "product owner"]
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                resources["roles_needed"].append(role)
        
        # Extract technology stack
        tech_patterns = [
            r"using\s+([^.\n]+?)(?:\s+for|\s+to|\.)",
            r"built\s+with\s+([^.\n]+?)(?:\s+for|\s+to|\.)",
            r"technologies?:\s*([^.\n]+)",
            r"stack:\s*([^.\n]+)"
        ]
        for pattern in tech_patterns:
            match = re.search(pattern, content_lower)
            if match:
                tech_text = match.group(1).strip()
                # Split by common separators
                techs = re.split(r'[,\s+and\s+|\s+&\s+]', tech_text)
                resources["technology_stack"].extend([t.strip() for t in techs if t.strip()])
        
        # Extract constraints
        constraint_patterns = [
            (r"budget\s*:?\s*\$?([0-9,]+)", "budget"),
            (r"deadline\s*:?\s*([^.\n]+)", "timeline"),
            (r"must\s+use\s+([^.\n]+)", "technology"),
            (r"cannot\s+use\s+([^.\n]+)", "restriction"),
            (r"limited\s+to\s+([^.\n]+)", "limitation")
        ]
        for pattern, constraint_type in constraint_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                resources["constraints"].append({
                    "type": constraint_type,
                    "description": match.strip()
                })
        
        return resources

    def _enhance_ai_prompting(self, context: Dict[str, Any], resources: Dict[str, Any]) -> str:
        """Create sophisticated AI prompts based on project context and resources."""
        
        domain_expertise = {
            "blockchain": {
                "considerations": "smart contract security, gas optimization, consensus mechanisms",
                "phases": "smart contract development, testing on testnets, security audits, mainnet deployment",
                "risks": "security vulnerabilities, regulatory compliance, scalability issues"
            },
            "ecommerce": {
                "considerations": "payment integration, inventory management, user experience, scalability",
                "phases": "product catalog, payment gateway, order management, analytics integration",
                "risks": "payment security, data privacy, performance under load"
            },
            "mobile": {
                "considerations": "platform compatibility, app store guidelines, responsive design, offline functionality",
                "phases": "UI/UX design, native development, testing on devices, app store submission",
                "risks": "device fragmentation, approval delays, performance optimization"
            },
            "ai": {
                "considerations": "data quality, model training, inference optimization, ethical AI",
                "phases": "data collection, model development, training pipeline, deployment infrastructure",
                "risks": "data bias, model drift, computational costs"
            },
            "enterprise": {
                "considerations": "security compliance, integration requirements, scalability, maintenance",
                "phases": "requirements gathering, architecture design, development, deployment, support",
                "risks": "integration complexity, compliance requirements, change management"
            }
        }
        
        domain_info = domain_expertise.get(context['domain'], domain_expertise['enterprise'])
        
        prompt = f"""
You are an expert {context['domain']} project manager and technical architect with 15+ years of experience.

PROJECT CONTEXT:
Name: {context['project_name']}
Domain: {context['domain']} 
Complexity: {context['complexity']}
Timeline: {context.get('timeline', 'TBD')} weeks

RESOURCE CONSTRAINTS:
Team Size: {resources.get('team_size', 'TBD')}
Available Roles: {', '.join(resources.get('roles_needed', ['TBD']))}
Technology Stack: {', '.join(resources.get('technology_stack', ['TBD']))}
Key Constraints: {'; '.join([f"{c['type']}: {c['description']}" for c in resources.get('constraints', [])])}

DOMAIN-SPECIFIC CONSIDERATIONS:
{domain_info['considerations']}

TYPICAL PROJECT PHASES:
{domain_info['phases']}

KEY RISKS TO MITIGATE:
{domain_info['risks']}

MILESTONE CONTEXT:
{chr(10).join(context.get('milestones', ['No milestones provided'])[:5])}

Generate 12-20 specific, actionable tasks that demonstrate deep {context['domain']} expertise:

1. Tasks must be specific to {context['domain']} domain best practices
2. Consider the {context['complexity']} complexity level appropriately  
3. Account for team size of {resources.get('team_size', 'unknown')} and available roles
4. Respect technology constraints: {', '.join(resources.get('technology_stack', ['flexible']))}
5. Include realistic time estimates for {context.get('timeline', 8)}-week timeline
6. Address domain-specific risks and considerations
7. Ensure proper task sequencing and dependencies
8. Include both technical and project management tasks

Return ONLY a valid JSON array with this structure:
[
  {{
    "title": "Specific domain-appropriate task name",
    "description": "Detailed description showing {context['domain']} expertise",
    "estimated_hours": 16.0,
    "priority": "urgent|high|medium|low", 
    "skills_required": ["specific_skill_1", "specific_skill_2"],
    "dependencies": ["Previous Task Name"]
  }}
]

Focus on tasks that a {context['domain']} expert would prioritize. Avoid generic software development tasks.
"""
        return prompt
        
    def get_agent_card(self) -> AgentCard:
        capabilities = [
            "ai_powered_task_breakdown",
            "context_aware_analysis", 
            "intelligent_time_estimation",
            "dynamic_skill_identification",
            "dependency_analysis",
            "domain_specific_tasks",
            "resource_extraction",
            "project_context_understanding"
        ]
        
        if self.trello_enabled:
            capabilities.extend([
                "trello_board_creation",
                "trello_task_cards",
                "trello_list_management",
                "automatic_task_tracking"
            ])
        
        return AgentCard(
            name="Task Agent",
            version="4.0.0",
            description="AI-powered intelligent task agent with context-aware analysis and Trello integration",
            agent_type=AgentType.task,
            capabilities=capabilities,
            endpoints={
                "base_url": f"http://localhost:{self.port}",
                "send_message": f"http://localhost:{self.port}/api/send_message"
            },
            contact={
                "email": "task@taskmanagement.com"
            }
        )
    
    def _extract_project_name(self, content: str) -> str:
        """Extract a clean project name from upstream content.
        Priority:
        1) Explicit "[PROJECT] <name>" line in the content
        2) Heuristic from mission-like phrases (create/build/develop ...)
        3) Fallback to "A2A Project"
        """
        import re

        # 1) Try explicit [PROJECT] marker
        m = re.search(r"^\[PROJECT\]\s*(.+)$", content, re.IGNORECASE | re.MULTILINE)
        if m:
            name = m.group(1).strip()
            # Guardrails: strip noise and limit length
            name = re.sub(r"\s+", " ", name)
            return name[:80]

        # 2) Heuristic extraction from mission phrasing
        mission_lower = content.lower()
        patterns = [
            (r"(?:create|build|develop)\s+(?:a|an)\s+([^.\n\r]+?)(?:\s+with|\s+that|\s+for|\s+project|\.|\n|\r)", True),
            (r"(?:create|build|develop)\s+([^.\n\r]+?)(?:\s+project|\s+system|\s+platform|\s+app|\s+application)", True),
        ]
        for pattern, _ in patterns:
            match = re.search(pattern, mission_lower, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Cleanup and title case
                candidate = re.sub(r"\s+", " ", candidate)
                candidate = candidate.title()
                if 3 <= len(candidate) <= 80:
                    return candidate

        # 3) Fallback
        return "A2A Project"

    def _extract_project_context(self, content: str) -> Dict[str, Any]:
        """Extract project context and requirements from supervisor content."""
        context = {
            "project_name": self._extract_project_name(content),
            "timeline": None,
            "features": [],
            "technologies": [],
            "complexity": "medium",
            "domain": "general",
            "milestones": []
        }
        
        # Extract timeline information
        timeline_patterns = [
            r"(?:timeline|duration):\s*(\d+)\s*weeks",
            r"within\s+(\d+)\s+weeks",
            r"(\d+)\s+week\s+project"
        ]
        for pattern in timeline_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                context["timeline"] = int(match.group(1))
                break
        
        # Extract features/requirements
        feature_section = re.search(r"(?:features?|requirements?)[\s\S]*?(?:\n\n|\Z)", content, re.IGNORECASE)
        if feature_section:
            lines = feature_section.group().split('\n')
            for line in lines:
                if line.strip().startswith(('-', '•', '*')):
                    feature = line.strip().lstrip('-•* ').strip()
                    if feature:
                        context["features"].append(feature)
        
        # Extract milestones from content
        milestone_matches = re.findall(r"\[M\d+\][^[]*", content)
        for milestone in milestone_matches:
            context["milestones"].append(milestone.strip())
        
        # Determine project domain and complexity
        content_lower = content.lower()
        
        # Domain detection
        if any(term in content_lower for term in ["blockchain", "defi", "smart contract", "crypto"]):
            context["domain"] = "blockchain"
        elif any(term in content_lower for term in ["ecommerce", "e-commerce", "shopping", "payment"]):
            context["domain"] = "ecommerce"
        elif any(term in content_lower for term in ["mobile app", "ios", "android"]):
            context["domain"] = "mobile"
        elif any(term in content_lower for term in ["ai", "machine learning", "ml", "neural"]):
            context["domain"] = "ai"
        elif any(term in content_lower for term in ["iot", "sensor", "device"]):
            context["domain"] = "iot"
        elif any(term in content_lower for term in ["erp", "enterprise", "business"]):
            context["domain"] = "enterprise"
        
        # Complexity detection
        complexity_indicators = {
            "simple": ["basic", "simple", "minimal", "straightforward"],
            "medium": ["comprehensive", "full-featured", "scalable"],
            "complex": ["enterprise", "multi-chain", "advanced", "sophisticated", "complex"]
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                context["complexity"] = level
                break
        
        return context

    async def generate_intelligent_tasks(self, context: Dict[str, Any], resources: Dict[str, Any]) -> List[TaskData]:
        """Use AI to generate project-specific tasks based on context and resources."""
        try:
            # Use enhanced prompting for better intelligence
            prompt = self._enhance_ai_prompting(context, resources)

            logger.info("Generating intelligent tasks using enhanced AI prompting")
            ai_response = await self.ai_service.analyze_text(prompt)
            
            if not ai_response:
                logger.warning("AI service unavailable, falling back to context-aware templates")
                return self._generate_context_aware_fallback_tasks(context)
            
            # Try to extract JSON from AI response
            try:
                # Look for JSON array in the response
                json_match = re.search(r'\[\s*\{.*\}\s*\]', ai_response, re.DOTALL)
                if json_match:
                    tasks_data = json.loads(json_match.group())
                else:
                    # If no JSON found, try to parse the entire response
                    tasks_data = json.loads(ai_response)
                
                tasks = []
                for task_dict in tasks_data:
                    # Map priority string to Priority enum
                    priority_str = task_dict.get('priority', 'medium').lower()
                    priority_map = {
                        'urgent': Priority.urgent,
                        'high': Priority.high,
                        'medium': Priority.medium,
                        'low': Priority.low
                    }
                    priority = priority_map.get(priority_str, Priority.medium)
                    
                    task = TaskData(
                        title=task_dict.get('title', 'Untitled Task'),
                        description=task_dict.get('description', ''),
                        priority=priority,
                        estimated_hours=float(task_dict.get('estimated_hours', 8.0)),
                        skills_required=task_dict.get('skills_required', []),
                        dependencies=task_dict.get('dependencies', [])
                    )
                    tasks.append(task)
                
                logger.info(f"Successfully generated {len(tasks)} intelligent tasks using enhanced prompting")
                return tasks
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse AI-generated tasks: {e}")
                logger.warning("Falling back to context-aware templates")
                return self._generate_context_aware_fallback_tasks(context)
                
        except Exception as e:
            logger.error(f"Error generating intelligent tasks: {e}")
            return self._generate_context_aware_fallback_tasks(context)

    def _generate_context_aware_fallback_tasks(self, context: Dict[str, Any]) -> List[TaskData]:
        """Generate context-aware tasks as fallback when AI is unavailable."""
        domain = context['domain']
        complexity = context['complexity']
        timeline_weeks = context.get('timeline', 8)
        
        # Base tasks that apply to most projects
        base_tasks = [
            TaskData(
                title="Requirements Analysis and Documentation",
                description=f"Analyze and document detailed requirements for the {context['project_name']} project",
                priority=Priority.high,
                estimated_hours=16.0 if complexity == 'complex' else 12.0,
                skills_required=["business_analysis", "documentation"],
                dependencies=[]
            ),
            TaskData(
                title="Technical Architecture Design",
                description=f"Design system architecture suitable for {domain} domain and {complexity} complexity",
                priority=Priority.high,
                estimated_hours=24.0 if complexity == 'complex' else 16.0,
                skills_required=["system_design", "architecture"],
                dependencies=["Requirements Analysis and Documentation"]
            )
        ]
        
        # Domain-specific tasks
        domain_tasks = []
        
        if domain == "blockchain":
            domain_tasks = [
                TaskData(
                    title="Smart Contract Architecture",
                    description="Design and plan smart contract structure and interactions",
                    priority=Priority.high,
                    estimated_hours=32.0,
                    skills_required=["solidity", "blockchain_architecture"],
                    dependencies=["Technical Architecture Design"]
                ),
                TaskData(
                    title="Smart Contract Development",
                    description="Implement core smart contracts with security best practices",
                    priority=Priority.high,
                    estimated_hours=80.0,
                    skills_required=["solidity", "smart_contract_development"],
                    dependencies=["Smart Contract Architecture"]
                ),
                TaskData(
                    title="Security Audit Preparation",
                    description="Prepare contracts for security audit and vulnerability assessment",
                    priority=Priority.urgent,
                    estimated_hours=24.0,
                    skills_required=["security_audit", "smart_contract_testing"],
                    dependencies=["Smart Contract Development"]
                )
            ]
        elif domain == "ecommerce":
            domain_tasks = [
                TaskData(
                    title="Payment Gateway Integration",
                    description="Integrate multiple payment processors (Stripe, PayPal) with security compliance",
                    priority=Priority.high,
                    estimated_hours=40.0,
                    skills_required=["payment_integration", "security"],
                    dependencies=["Technical Architecture Design"]
                ),
                TaskData(
                    title="Product Catalog System",
                    description="Develop product management system with search and filtering capabilities",
                    priority=Priority.high,
                    estimated_hours=48.0,
                    skills_required=["backend_development", "database_design"],
                    dependencies=["Technical Architecture Design"]
                ),
                TaskData(
                    title="Shopping Cart & Checkout Flow",
                    description="Implement shopping cart functionality and streamlined checkout process",
                    priority=Priority.high,
                    estimated_hours=36.0,
                    skills_required=["frontend_development", "ux_design"],
                    dependencies=["Product Catalog System"]
                )
            ]
        elif domain == "mobile":
            domain_tasks = [
                TaskData(
                    title="Cross-Platform Framework Setup",
                    description="Set up React Native or Flutter development environment",
                    priority=Priority.high,
                    estimated_hours=16.0,
                    skills_required=["mobile_development", "react_native"],
                    dependencies=["Technical Architecture Design"]
                ),
                TaskData(
                    title="Mobile UI/UX Implementation",
                    description="Develop responsive mobile interface with platform-specific guidelines",
                    priority=Priority.high,
                    estimated_hours=60.0,
                    skills_required=["mobile_ui", "user_experience"],
                    dependencies=["Cross-Platform Framework Setup"]
                )
            ]
        
        # Common development tasks
        common_tasks = [
            TaskData(
                title="Database Design and Implementation",
                description=f"Design and implement database schema for {domain} requirements",
                priority=Priority.high,
                estimated_hours=28.0 if complexity == 'complex' else 20.0,
                skills_required=["database_design", "sql"],
                dependencies=["Technical Architecture Design"]
            ),
            TaskData(
                title="API Development and Integration",
                description="Develop RESTful APIs and integrate with external services",
                priority=Priority.high,
                estimated_hours=40.0 if complexity == 'complex' else 28.0,
                skills_required=["api_development", "backend_development"],
                dependencies=["Database Design and Implementation"]
            ),
            TaskData(
                title="Testing Strategy Implementation",
                description="Implement comprehensive testing including unit, integration, and E2E tests",
                priority=Priority.high,
                estimated_hours=32.0,
                skills_required=["testing", "test_automation"],
                dependencies=["API Development and Integration"]
            )
        ]
        
        all_tasks = base_tasks + domain_tasks + common_tasks
        
        # Adjust estimates based on timeline
        if timeline_weeks and timeline_weeks < 8:
            # Shorter timeline - reduce estimates and prioritize critical tasks
            for task in all_tasks:
                task.estimated_hours *= 0.8
                if task.priority == Priority.medium:
                    task.priority = Priority.low
        elif timeline_weeks and timeline_weeks > 16:
            # Longer timeline - allow for more detailed work
            for task in all_tasks:
                task.estimated_hours *= 1.2
        
        return all_tasks
    
    def _create_enhanced_trello_lists(self, board_id: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Create specialized Trello lists based on project context."""
        try:
            # Remove default lists first
            existing_lists = self.trello.get_lists_on_board(board_id)
            for lst in existing_lists:
                if lst['name'] in ['To Do', 'Doing', 'Done']:
                    # Archive default lists to replace with specialized ones
                    pass  # Keep them for now, add specialized ones
            
            # Create domain-specific lists (cleaned of emojis to prevent Unicode errors)
            domain_lists = {
                "blockchain": ["Planning", "Smart Contracts", "Testing", "Deployment", "Complete"],
                "ecommerce": ["Planning", "Frontend", "Backend", "Payments", "Testing", "Complete"],
                "mobile": ["Planning", "UI/UX", "iOS Dev", "Android Dev", "Testing", "Release", "Complete"],
                "ai": ["Planning", "Data Prep", "Model Dev", "Training", "Deployment", "Complete"],
                "enterprise": ["Planning", "Architecture", "Development", "Integration", "Testing", "Deployment", "Complete"]
            }
            
            domain = context.get('domain', 'enterprise')
            lists_to_create = domain_lists.get(domain, domain_lists['enterprise'])
            
            created_lists = {}
            for list_name in lists_to_create:
                try:
                    list_id = self.trello.create_list(board_id, list_name)
                    if list_id:
                        created_lists[list_name] = list_id
                        logger.info(f"Created specialized list: {list_name}")
                except Exception as e:
                    logger.error(f"Failed to create list {list_name}: {e}")
            
            return created_lists
            
        except Exception as e:
            logger.error(f"Error creating enhanced Trello lists: {e}")
            # Fallback to existing lists
            existing_lists = self.trello.get_lists_on_board(board_id)
            return {lst['name']: lst['id'] for lst in existing_lists}

    def _assign_task_to_optimal_list(self, task: TaskData, available_lists: Dict[str, str], context: Dict[str, Any]) -> str:
        """Intelligently assign tasks to the most appropriate Trello list."""
        
        # Priority-based assignment (cleaned of emojis)
        if task.priority == Priority.urgent:
            priority_lists = ["Planning", "To Do"]
        elif task.priority == Priority.high:
            priority_lists = ["Planning", "Architecture", "To Do"]
        else:
            priority_lists = list(available_lists.keys())
        
        # Skill-based assignment (cleaned of emojis)
        skill_mapping = {
            "frontend": ["Frontend", "UI/UX", "Development"],
            "backend": ["Backend", "Development", "Smart Contracts"],
            "mobile": ["iOS Dev", "Android Dev", "Release"],
            "testing": ["Testing"],
            "deployment": ["Deployment"],
            "design": ["UI/UX", "Frontend"],
            "architecture": ["Architecture", "Planning"],
            "data": ["Data Prep"],
            "ai": ["Model Dev", "Training"]
        }
        
        # Find best match based on skills
        for skill in task.skills_required:
            skill_lower = skill.lower()
            for skill_key, preferred_lists in skill_mapping.items():
                if skill_key in skill_lower:
                    for preferred_list in preferred_lists:
                        if preferred_list in available_lists:
                            return available_lists[preferred_list]
        
        # Fallback to priority-based assignment
        for priority_list in priority_lists:
            if priority_list in available_lists:
                return available_lists[priority_list]
        
        # Ultimate fallback to first available list
        return list(available_lists.values())[0] if available_lists else None

    async def create_enhanced_trello_project(self, project_description: str, tasks: List[TaskData], context: Dict[str, Any], resources: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create enhanced Trello board with specialized lists and intelligent task assignment."""
        if not self.trello:
            logger.warning("Trello integration not available")
            return None
        
        try:
            logger.info("Creating enhanced Trello project with intelligent task organization")
            
            # Create project board with clean name
            clean_name = self._extract_project_name(project_description)
            project_name = f"{clean_name} - Project Tasks"
            
            # Add context info to board name if useful
            if context.get('domain') and context['domain'] != 'general':
                project_name = f"{clean_name} - {context['domain'].title()} Project"
            
            board_id = self.trello.create_board(project_name)
            
            if not board_id:
                logger.error("Failed to create Trello board")
                return {"error": "Failed to create Trello board"}
            
            self.current_board_id = board_id
            
            # Create specialized lists based on project context
            specialized_lists = self._create_enhanced_trello_lists(board_id, context)
            
            if not specialized_lists:
                logger.error("Failed to create board lists")
                return {"error": "Failed to create board lists"}
            
            # Create cards with intelligent assignment
            created_cards = []
            for task in tasks:
                # Assign to optimal list
                target_list_id = self._assign_task_to_optimal_list(task, specialized_lists, context)
                
                if not target_list_id:
                    logger.warning(f"Could not assign list for task: {task.title}")
                    continue
                
                # Enhanced card description with context
                card_description = self._create_enhanced_card_description(task, context, resources)
                
                # Create the card
                card_id = self.trello.create_card(
                    list_id=target_list_id,
                    card_name=task.title,
                    description=card_description
                )
                
                if card_id:
                    # Find list name for the assigned list_id
                    assigned_list_name = next((name for name, id in specialized_lists.items() if id == target_list_id), "Unknown")
                    
                    created_cards.append({
                        "task_title": task.title,
                        "card_id": card_id,
                        "estimated_hours": task.estimated_hours,
                        "priority": task.priority.value,
                        "assigned_list": assigned_list_name,
                        "skills": task.skills_required
                    })
                    logger.info(f"Created enhanced card for task: {task.title} -> {assigned_list_name}")
                else:
                    logger.warning(f"Failed to create Trello card for task: {task.title}")
            
            # Enhanced results with context information
            trello_results = {
                "board_id": board_id,
                "board_name": project_name,
                "board_url": f"https://trello.com/b/{board_id}",
                "cards_created": len(created_cards),
                "total_tasks": len(tasks),
                "created_cards": created_cards,
                "specialized_lists": list(specialized_lists.keys()),
                "project_context": {
                    "domain": context.get('domain'),
                    "complexity": context.get('complexity'),
                    "timeline": context.get('timeline'),
                    "team_size": resources.get('team_size')
                }
            }
            
            logger.info(f"Successfully created enhanced Trello project with {len(created_cards)} intelligently organized task cards")
            return trello_results
            
        except Exception as e:
            logger.error(f"Error creating enhanced Trello project: {e}")
            return {"error": f"Enhanced Trello integration failed: {str(e)}"}

    def _create_enhanced_card_description(self, task: TaskData, context: Dict[str, Any], resources: Dict[str, Any]) -> str:
        """Create detailed card description with project context."""
        description = f"""
**Task Description:**
{task.description}

**Project Context:**
• Domain: {context.get('domain', 'General').title()}
• Complexity: {context.get('complexity', 'Medium').title()}
• Timeline: {context.get('timeline', 'TBD')} weeks

**Task Details:**
• Estimated Hours: {task.estimated_hours}
• Priority: {task.priority.value.upper()}
• Skills Required: {', '.join(task.skills_required) if task.skills_required else 'General'}

**Dependencies:**
{', '.join(task.dependencies) if task.dependencies else 'None - can start immediately'}

**Resource Context:**
• Team Size: {resources.get('team_size', 'TBD')}
• Available Roles: {', '.join(resources.get('roles_needed', [])) if resources.get('roles_needed') else 'TBD'}

**Technology Stack:**
{', '.join(resources.get('technology_stack', [])) if resources.get('technology_stack') else 'To be determined'}

---
*Generated by A2A Intelligent Task Agent v4.0*
*Context-aware task breakdown with resource optimization*
        """.strip()
        
        return description

    async def process_message(self, request: SendMessageRequest) -> MessageResponse:
        """Process task breakdown request with enhanced intelligence and resource extraction."""
        print("[TASK] ======= PROCESSING ENHANCED MESSAGE =======")
        
        message = request.params.message
        content = message.parts[0].root.text
        milestone_data = getattr(request.params, 'milestone_data', None)
        
        print(f"[TASK] Content received: {content[:100]}...")
        print(f"[TASK] Enhanced Trello integration: {self.trello_enabled}")
        
        logger.info("Processing enhanced intelligent task breakdown request")
        
        # Step 1: Extract project context for intelligent analysis
        print("[TASK] Extracting project context...")
        project_context = self._extract_project_context(content)
        print(f"[TASK] Project context: {project_context['project_name']} ({project_context['domain']}, {project_context['complexity']})")
        
        # Step 2: Extract resources from supervisor context
        print("[TASK] Extracting resource context...")
        resource_context = self._extract_resources_from_context(content)
        print(f"[TASK] Resources: Team size: {resource_context.get('team_size', 'TBD')}, Roles: {len(resource_context.get('roles_needed', []))}")
        
        # Store contexts for potential future use
        self.current_project_context = {
            **project_context,
            **resource_context
        }
        
        # Step 3: Generate intelligent tasks with enhanced prompting
        print("[TASK] Generating intelligent tasks with enhanced prompting...")
        task_breakdown = await self.generate_intelligent_tasks(project_context, resource_context)
        print(f"[TASK] Generated {len(task_breakdown)} intelligent tasks using enhanced AI")
        
        # Step 4: Create enhanced Trello project if enabled
        trello_results = None
        if self.trello_enabled:
            print("[TASK] Starting enhanced Trello integration...")
            trello_results = await self.create_enhanced_trello_project(content, task_breakdown, project_context, resource_context)
            if trello_results and "error" not in trello_results:
                print(f"[TASK] Enhanced Trello project created: {trello_results.get('board_name')}")
                print(f"[TASK] Specialized lists: {', '.join(trello_results.get('specialized_lists', []))}")
            else:
                print(f"[TASK] Trello integration issue: {trello_results}")
        else:
            print("[TASK] Trello integration disabled")
        
        # Step 5: Generate enhanced response
        response_text = self.format_enhanced_task_response(task_breakdown, trello_results, project_context, resource_context)
        
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(response_text),
            task_breakdown=task_breakdown
        )

    async def create_trello_project(self, project_description: str, tasks: List[TaskData]) -> Optional[Dict[str, Any]]:
        """Create Trello board and cards for the project"""
        if not self.trello:
            return None
        
        try:
            logger.info("Creating Trello board for task management")
            
            # Create project board with a clean, human-friendly name
            clean_name = self._extract_project_name(project_description)
            # Ensure no analysis banners or emojis make it into the board name
            project_name = f"{clean_name} - Project Tasks"
            board_id = self.trello.create_board(project_name)
            
            if not board_id:
                logger.error("Failed to create Trello board")
                return {"error": "Failed to create Trello board"}
            
            self.current_board_id = board_id
            
            # Get default lists on the board
            lists = self.trello.get_lists_on_board(board_id)
            if not lists:
                logger.error("Failed to get board lists")
                return {"error": "Failed to get board lists"}
            
            # Map lists by name for task organization
            list_mapping = {}
            for lst in lists:
                list_mapping[lst['name']] = lst['id']
            
            # Default Trello board has "To Do", "Doing", "Done" lists
            default_list_id = lists[0]['id']  # Use first list as default
            
            # Create cards for each task
            created_cards = []
            for task in tasks:
                # Determine appropriate list based on task priority
                target_list_id = self._get_target_list_id(task, list_mapping, default_list_id)
                
                # Create task description with details
                card_description = f"""
**Description:** {task.description}

**Estimated Hours:** {task.estimated_hours}
**Priority:** {task.priority.value.upper()}
**Skills Required:** {', '.join(task.skills_required)}

**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}

*Generated by A2A Task Agent*
                """.strip()
                
                # Create the card
                card_id = self.trello.create_card(
                    list_id=target_list_id,
                    card_name=task.title,
                    description=card_description
                )
                
                if card_id:
                    created_cards.append({
                        "task_title": task.title,
                        "card_id": card_id,
                        "estimated_hours": task.estimated_hours,
                        "priority": task.priority.value
                    })
                    logger.info(f"Created Trello card for task: {task.title}")
                else:
                    logger.warning(f"Failed to create Trello card for task: {task.title}")
            
            trello_results = {
                "board_id": board_id,
                "board_name": project_name,
                "board_url": f"https://trello.com/b/{board_id}",
                "cards_created": len(created_cards),
                "total_tasks": len(tasks),
                "created_cards": created_cards,
                "lists_available": [{"name": lst['name'], "id": lst['id']} for lst in lists]
            }
            
            logger.info(f"Successfully created Trello project with {len(created_cards)} task cards")
            return trello_results
            
        except Exception as e:
            logger.error(f"Error creating Trello project: {e}")
            return {"error": f"Trello integration failed: {str(e)}"}
    
    def _get_target_list_id(self, task: TaskData, list_mapping: Dict[str, str], default_list_id: str) -> str:
        """Determine which Trello list to place the task card in"""
        # Place high priority tasks in "To Do" list (assuming it exists)
        if task.priority == Priority.urgent or task.priority == Priority.high:
            return list_mapping.get("To Do", default_list_id)
        else:
            # Medium/low priority tasks go to default list
            return default_list_id
    
    def format_task_response(self, tasks: List[TaskData], trello_results: Optional[Dict[str, Any]] = None) -> str:
        """Format intelligent task breakdown as readable text"""
        if not tasks:
            return "[WARNING] No specific tasks identified from the provided context."
        
        response = "[TASKS] INTELLIGENT TASK BREAKDOWN:\n\n"
        
        # Add Trello integration results if available
        if trello_results and "error" not in trello_results:
            response += f"[TRELLO] Board Created: {trello_results.get('board_name', 'N/A')}\n"
            response += f"[TRELLO] Board URL: {trello_results.get('board_url', 'N/A')}\n"
            response += f"[TRELLO] Cards Created: {trello_results.get('cards_created', 0)}/{trello_results.get('total_tasks', 0)}\n\n"
        elif trello_results and "error" in trello_results:
            response += f"[TRELLO] Integration Failed: {trello_results['error']}\n\n"
        
        total_hours = 0
        for i, task in enumerate(tasks, 1):
            response += f"[T{i}] {task.title}\n"
            response += f"     [DESC] {task.description}\n"
            response += f"     [TIME] Estimated: {task.estimated_hours} hours\n"
            response += f"     [PRIORITY] {task.priority.value.upper()}\n"
            response += f"     [SKILLS] {', '.join(task.skills_required)}\n"
            
            if task.dependencies:
                response += f"     [DEPS] Dependencies: {', '.join(task.dependencies)}\n"
            
            response += "\n"
            total_hours += task.estimated_hours or 0
        
        response += f"[SUMMARY] Total Estimated Hours: {total_hours}\n"
        response += f"[SUMMARY] Estimated Weeks: {total_hours / 40:.1f} (assuming 40 hours/week)\n"
        response += "[STATUS] Intelligent task breakdown complete - ready for resource allocation"
        
        return response
    
    def format_enhanced_task_response(self, tasks: List[TaskData], trello_results: Optional[Dict[str, Any]] = None, 
                                    context: Dict[str, Any] = None, resources: Dict[str, Any] = None) -> str:
        """Format enhanced intelligent task breakdown with context and resource information."""
        if not tasks:
            return "[WARNING] No specific tasks identified from the provided context."
        
        response = "[TASKS] ENHANCED INTELLIGENT TASK BREAKDOWN:\n\n"
        
        # Add project context summary
        if context:
            response += "[CONTEXT] Project Analysis:\n"
            response += f"  • Project: {context.get('project_name', 'TBD')}\n"
            response += f"  • Domain: {context.get('domain', 'General').title()}\n"
            response += f"  • Complexity: {context.get('complexity', 'Medium').title()}\n"
            response += f"  • Timeline: {context.get('timeline', 'TBD')} weeks\n"
            if context.get('features'):
                response += f"  • Key Features: {len(context['features'])} identified\n"
            response += "\n"
        
        # Add resource context
        if resources:
            response += "[RESOURCES] Team & Constraints:\n"
            if resources.get('team_size'):
                response += f"  • Team Size: {resources['team_size']} members\n"
            if resources.get('roles_needed'):
                response += f"  • Roles Required: {', '.join(resources['roles_needed'])}\n"
            if resources.get('technology_stack'):
                response += f"  • Technology Stack: {', '.join(resources['technology_stack'][:5])}\n"
            if resources.get('constraints'):
                response += f"  • Constraints: {len(resources['constraints'])} identified\n"
            response += "\n"
        
        # Add Trello integration results
        if trello_results and "error" not in trello_results:
            response += "[TRELLO] Enhanced Board Created:\n"
            response += f"  • Board: {trello_results.get('board_name', 'N/A')}\n"
            response += f"  • URL: {trello_results.get('board_url', 'N/A')}\n"
            response += f"  • Cards: {trello_results.get('cards_created', 0)}/{trello_results.get('total_tasks', 0)}\n"
            if trello_results.get('specialized_lists'):
                response += f"  • Lists: {', '.join(trello_results['specialized_lists'][:3])}...\n"
            response += "\n"
        elif trello_results and "error" in trello_results:
            response += f"[TRELLO] Integration Issue: {trello_results['error']}\n\n"
        
        # Group tasks by priority for better organization
        priority_groups = {
            Priority.urgent: [],
            Priority.high: [],
            Priority.medium: [],
            Priority.low: []
        }
        
        for task in tasks:
            priority_groups[task.priority].append(task)
        
        task_counter = 1
        total_hours = 0
        
        for priority in [Priority.urgent, Priority.high, Priority.medium, Priority.low]:
            priority_tasks = priority_groups[priority]
            if not priority_tasks:
                continue
                
            response += f"[{priority.value.upper()} PRIORITY] {len(priority_tasks)} Tasks:\n"
            
            for task in priority_tasks:
                response += f"[T{task_counter}] {task.title}\n"
                response += f"     [DESC] {task.description}\n"
                response += f"     [TIME] {task.estimated_hours} hours\n"
                response += f"     [SKILLS] {', '.join(task.skills_required) if task.skills_required else 'General'}\n"
                
                if task.dependencies:
                    response += f"     [DEPS] {', '.join(task.dependencies)}\n"
                
                # Add Trello assignment info if available
                if trello_results and "created_cards" in trello_results:
                    card_info = next((card for card in trello_results["created_cards"] if card["task_title"] == task.title), None)
                    if card_info and "assigned_list" in card_info:
                        response += f"     [TRELLO] Assigned to: {card_info['assigned_list']}\n"
                
                response += "\n"
                task_counter += 1
                total_hours += task.estimated_hours or 0
        
        # Enhanced summary with resource considerations
        response += "[SUMMARY] Enhanced Analysis:\n"
        response += f"  • Total Tasks: {len(tasks)}\n"
        response += f"  • Total Hours: {total_hours}\n"
        response += f"  • Estimated Duration: {total_hours / 40:.1f} weeks (40h/week)\n"
        
        if resources and resources.get('team_size'):
            team_weeks = total_hours / (40 * resources['team_size'])
            response += f"  • With {resources['team_size']} team members: {team_weeks:.1f} weeks\n"
        
        # Add domain-specific insights
        if context and context.get('domain') != 'general':
            domain_insights = {
                "blockchain": "Consider gas optimization, security audits, and regulatory compliance",
                "ecommerce": "Focus on payment security, user experience, and scalability",
                "mobile": "Plan for app store approval, device testing, and platform compliance",
                "ai": "Ensure data quality, model validation, and ethical AI considerations",
                "enterprise": "Address security, integration, and change management requirements"
            }
            domain = context['domain']
            if domain in domain_insights:
                response += f"  • {domain.title()} Focus: {domain_insights[domain]}\n"
        
        response += "\n[STATUS] Enhanced intelligent task breakdown complete - optimized for resources and context"
        
        return response


if __name__ == "__main__":
    agent = TaskAgent()
    agent.run()
