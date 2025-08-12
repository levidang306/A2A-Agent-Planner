"""
👥 Team Management Tool for A2A System
======================================
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class TeamManager:
    def __init__(self):
        self.skill_database = {
            # Programming Languages
            "python": {"category": "backend", "level_multiplier": 1.0},
            "javascript": {"category": "frontend", "level_multiplier": 1.0},
            "typescript": {"category": "frontend", "level_multiplier": 1.1},
            "java": {"category": "backend", "level_multiplier": 1.1},
            "react": {"category": "frontend", "level_multiplier": 1.2},
            "nodejs": {"category": "backend", "level_multiplier": 1.1},
            "sql": {"category": "database", "level_multiplier": 1.0},
            "mongodb": {"category": "database", "level_multiplier": 1.0},
            
            # Design & UI/UX
            "ui_design": {"category": "design", "level_multiplier": 1.2},
            "ux_research": {"category": "design", "level_multiplier": 1.3},
            "figma": {"category": "design", "level_multiplier": 1.0},
            "photoshop": {"category": "design", "level_multiplier": 1.0},
            
            # DevOps & Infrastructure
            "docker": {"category": "devops", "level_multiplier": 1.2},
            "kubernetes": {"category": "devops", "level_multiplier": 1.4},
            "aws": {"category": "devops", "level_multiplier": 1.3},
            "ci_cd": {"category": "devops", "level_multiplier": 1.2},
            
            # Project Management
            "project_management": {"category": "management", "level_multiplier": 1.3},
            "agile": {"category": "management", "level_multiplier": 1.1},
            "scrum": {"category": "management", "level_multiplier": 1.1}
        }
    
    def create_team_from_requirements(self, project_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimal team composition based on project requirements"""
        
        # Analyze project requirements to determine needed skills
        required_skills = self._analyze_project_requirements(project_requirements)
        
        # Generate team members based on requirements
        team_members = []
        
        if required_skills.get("backend", 0) > 0:
            backend_dev = self._create_team_member(
                role="Backend Developer",
                primary_skills=["python", "nodejs", "sql", "docker"],
                experience_level="senior" if required_skills["backend"] > 7 else "mid"
            )
            team_members.append(backend_dev)
        
        if required_skills.get("frontend", 0) > 0:
            frontend_dev = self._create_team_member(
                role="Frontend Developer", 
                primary_skills=["javascript", "react", "typescript"],
                experience_level="senior" if required_skills["frontend"] > 7 else "mid"
            )
            team_members.append(frontend_dev)
        
        if required_skills.get("design", 0) > 0:
            designer = self._create_team_member(
                role="UI/UX Designer",
                primary_skills=["ui_design", "ux_research", "figma"],
                experience_level="senior" if required_skills["design"] > 7 else "mid"
            )
            team_members.append(designer)
        
        if required_skills.get("devops", 0) > 0:
            devops_eng = self._create_team_member(
                role="DevOps Engineer",
                primary_skills=["docker", "kubernetes", "aws", "ci_cd"],
                experience_level="senior"
            )
            team_members.append(devops_eng)
        
        if required_skills.get("management", 0) > 0 or len(team_members) > 3:
            project_manager = self._create_team_member(
                role="Project Manager",
                primary_skills=["project_management", "agile", "scrum"],
                experience_level="senior"
            )
            team_members.append(project_manager)
        
        # Add team lead if team size > 4
        if len(team_members) > 4:
            tech_lead = self._create_team_member(
                role="Technical Lead",
                primary_skills=["python", "javascript", "project_management"],
                experience_level="senior"
            )
            team_members.insert(0, tech_lead)
        
        return team_members
    
    def assign_tasks_to_team(self, tasks: List[Dict], team_members: List[Dict]) -> Dict[str, Any]:
        """Assign tasks to team members based on skills and workload"""
        
        assignments = {
            "task_assignments": [],
            "team_workload": {},
            "skill_coverage": {},
            "recommendations": []
        }
        
        # Initialize workload tracking
        for member in team_members:
            assignments["team_workload"][member["name"]] = {
                "assigned_tasks": 0,
                "total_hours": 0,
                "utilization": 0
            }
        
        # Assign each task
        for task in tasks:
            best_assignee = self._find_best_assignee(task, team_members, assignments["team_workload"])
            
            if best_assignee:
                task_hours = self._estimate_task_hours(task)
                
                assignment = {
                    "task_id": task.get("id", f"task_{hash(task.get('title', ''))}"),
                    "task_title": task.get("title", "Untitled Task"),
                    "assigned_to": best_assignee["name"],
                    "assignee_role": best_assignee["role"],
                    "estimated_hours": task_hours,
                    "match_score": self._calculate_skill_match(task, best_assignee),
                    "priority": task.get("priority", "Medium")
                }
                
                assignments["task_assignments"].append(assignment)
                
                # Update workload
                assignments["team_workload"][best_assignee["name"]]["assigned_tasks"] += 1
                assignments["team_workload"][best_assignee["name"]]["total_hours"] += task_hours
            else:
                assignments["recommendations"].append(f"No suitable assignee found for: {task.get('title', 'Unknown task')}")
        
        # Calculate utilization (assume 40 hours per week)
        for member_name, workload in assignments["team_workload"].items():
            workload["utilization"] = min(100, (workload["total_hours"] / 40) * 100)
        
        return assignments
    
    def _analyze_project_requirements(self, requirements: Dict[str, Any]) -> Dict[str, int]:
        """Analyze project requirements to determine skill complexity (1-10 scale)"""
        
        description = requirements.get("description", "").lower()
        features = str(requirements.get("features", [])).lower()
        complexity = requirements.get("complexity", "medium").lower()
        
        # Base complexity multiplier
        complexity_multiplier = {
            "simple": 0.7,
            "medium": 1.0, 
            "complex": 1.5,
            "enterprise": 2.0
        }.get(complexity, 1.0)
        
        skills_needed = {
            "backend": 5,    # Default
            "frontend": 5,   # Default
            "design": 3,     # Default
            "devops": 2,     # Default
            "management": 2  # Default
        }
        
        # Analyze keywords in description
        if any(word in description for word in ["api", "database", "server", "backend"]):
            skills_needed["backend"] += 2
        
        if any(word in description for word in ["ui", "interface", "frontend", "react", "angular"]):
            skills_needed["frontend"] += 2
        
        if any(word in description for word in ["design", "ux", "user experience", "wireframe"]):
            skills_needed["design"] += 3
        
        if any(word in description for word in ["deployment", "docker", "kubernetes", "aws", "cloud"]):
            skills_needed["devops"] += 3
        
        if any(word in description for word in ["team", "coordination", "multiple", "large"]):
            skills_needed["management"] += 2
        
        # Apply complexity multiplier
        for skill in skills_needed:
            skills_needed[skill] = int(skills_needed[skill] * complexity_multiplier)
            skills_needed[skill] = min(10, skills_needed[skill])  # Cap at 10
        
        return skills_needed
    
    def _create_team_member(self, role: str, primary_skills: List[str], experience_level: str) -> Dict[str, Any]:
        """Create a team member with realistic profile"""
        
        # Name generation (demo purposes)
        first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Quinn"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        
        import random
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Experience level to skill mapping
        skill_levels = {
            "junior": 6,
            "mid": 7,
            "senior": 9,
            "expert": 10
        }
        
        base_skill_level = skill_levels.get(experience_level, 7)
        
        # Generate skills with levels
        skills = {}
        for skill in primary_skills:
            variation = random.randint(-1, 1)
            skills[skill] = min(10, max(1, base_skill_level + variation))
        
        # Add some secondary skills
        all_skills = list(self.skill_database.keys())
        secondary_skills = random.sample([s for s in all_skills if s not in primary_skills], 3)
        for skill in secondary_skills:
            skills[skill] = random.randint(3, 6)
        
        # Calculate hourly rate based on experience and skills
        base_rates = {
            "junior": 35,
            "mid": 55,
            "senior": 75,
            "expert": 95
        }
        
        hourly_rate = base_rates.get(experience_level, 55)
        skill_bonus = sum(skills.values()) / len(skills) * 5
        final_rate = int(hourly_rate + skill_bonus)
        
        return {
            "name": name,
            "role": role,
            "experience_level": experience_level,
            "skills": skills,
            "hourly_rate": final_rate,
            "availability": "Full-time",
            "timezone": "UTC-5",
            "contact": {
                "email": f"{name.lower().replace(' ', '.')}@company.com",
                "slack": f"@{name.lower().replace(' ', '')}"
            },
            "bio": f"Experienced {role.lower()} with {experience_level} level expertise in {', '.join(primary_skills[:3])}.",
            "created_at": datetime.now().isoformat()
        }
    
    def _find_best_assignee(self, task: Dict, team_members: List[Dict], current_workload: Dict) -> Optional[Dict]:
        """Find the best team member to assign a task to"""
        
        best_member = None
        best_score = 0
        
        for member in team_members:
            # Calculate skill match score
            skill_score = self._calculate_skill_match(task, member)
            
            # Calculate workload penalty (prefer less loaded members)
            workload_penalty = current_workload[member["name"]]["total_hours"] / 40.0  # Normalize to 40 hours
            
            # Calculate final score (skill match - workload penalty)
            final_score = skill_score - (workload_penalty * 0.3)
            
            if final_score > best_score:
                best_score = final_score
                best_member = member
        
        return best_member
    
    def _calculate_skill_match(self, task: Dict, member: Dict) -> float:
        """Calculate how well a team member's skills match a task"""
        
        task_description = task.get("description", "").lower()
        task_title = task.get("title", "").lower()
        task_text = f"{task_title} {task_description}"
        
        total_match = 0
        skills_matched = 0
        
        for skill, level in member["skills"].items():
            if skill in task_text or any(keyword in task_text for keyword in [skill.replace("_", " ")]):
                skill_info = self.skill_database.get(skill, {"level_multiplier": 1.0})
                match_value = level * skill_info["level_multiplier"]
                total_match += match_value
                skills_matched += 1
        
        # Normalize score (0-10 scale)
        if skills_matched > 0:
            return min(10, total_match / skills_matched)
        else:
            return 0
    
    def _estimate_task_hours(self, task: Dict) -> int:
        """Estimate task duration in hours"""
        
        time_estimate = task.get("time_estimate", "8 hours").lower()
        
        if "hour" in time_estimate:
            return int(''.join(filter(str.isdigit, time_estimate)) or 8)
        elif "day" in time_estimate:
            return int(''.join(filter(str.isdigit, time_estimate)) or 1) * 8
        elif "week" in time_estimate:
            return int(''.join(filter(str.isdigit, time_estimate)) or 1) * 40
        else:
            return 8  # Default 8 hours

# Example usage
if __name__ == "__main__":
    team_manager = TeamManager()
    
    # Demo project requirements
    project_requirements = {
        "description": "Build a full-stack e-commerce platform with React frontend, Python backend, and AWS deployment",
        "complexity": "complex",
        "features": ["user authentication", "payment processing", "inventory management", "admin dashboard"],
        "timeline": "3 months",
        "budget": "$150,000"
    }
    
    # Generate team
    team = team_manager.create_team_from_requirements(project_requirements)
    
    print("👥 Generated Team:")
    for member in team:
        print(f"- {member['name']} ({member['role']}) - ${member['hourly_rate']}/hr")
    
    # Demo tasks
    demo_tasks = [
        {
            "title": "Setup React Frontend",
            "description": "Initialize React app with TypeScript and configure routing",
            "time_estimate": "16 hours",
            "priority": "High"
        },
        {
            "title": "Design User Interface",
            "description": "Create wireframes and mockups for the e-commerce interface", 
            "time_estimate": "24 hours",
            "priority": "High"
        },
        {
            "title": "Build Python API",
            "description": "Develop REST API endpoints using Python and FastAPI",
            "time_estimate": "32 hours", 
            "priority": "Medium"
        }
    ]
    
    # Assign tasks
    assignments = team_manager.assign_tasks_to_team(demo_tasks, team)
    
    print("\\n📋 Task Assignments:")
    for assignment in assignments["task_assignments"]:
        print(f"- {assignment['task_title']} → {assignment['assigned_to']} ({assignment['estimated_hours']}h)")
    
    print(json.dumps(assignments, indent=2))
