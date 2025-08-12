"""Resource Agent - Handles team allocation and resource management"""
from typing import List, Dict, Any, Tuple
import uuid
import os
from ..a2a.types import (
    AgentCard, SendMessageRequest, MessageResponse, Message, 
    Role, Part, TextPart, MessageSendParams, AgentType, Priority
)
from .base_agent import BaseAgent


class ResourceAgent(BaseAgent):
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.getenv('RESOURCE_PORT', '9004'))
        super().__init__("Resource", AgentType.resource, port)
        
        # Simulated available team members with skills
        self.available_resources = {
            "senior_developers": [
                {"name": "Alice Johnson", "skills": ["backend_development", "system_design", "architecture", "python", "api_design"]},
                {"name": "Bob Chen", "skills": ["frontend_development", "javascript", "react", "ui_design"]},
                {"name": "Carol Davis", "skills": ["fullstack_development", "backend_development", "frontend_development", "database_design"]}
            ],
            "mid_developers": [
                {"name": "David Wilson", "skills": ["backend_development", "database_administration", "sql"]},
                {"name": "Eva Rodriguez", "skills": ["frontend_development", "javascript", "testing"]},
                {"name": "Frank Kim", "skills": ["backend_development", "api_design", "integration_testing"]}
            ],
            "specialists": [
                {"name": "Grace Liu", "skills": ["ux_design", "ui_design", "research"]},
                {"name": "Henry Brown", "skills": ["devops", "infrastructure", "deployment", "monitoring"]},
                {"name": "Iris Taylor", "skills": ["testing", "test_automation", "uat_coordination", "integration_testing"]}
            ],
            "analysts": [
                {"name": "Jack Moore", "skills": ["business_analysis", "communication", "research", "analysis"]},
                {"name": "Kate Singh", "skills": ["technical_analysis", "data_modeling", "analysis"]}
            ]
        }
        
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Resource Agent",
            version="1.0.0",
            description="Resource agent that handles team allocation and resource management",
            agent_type=AgentType.resource,
            capabilities=[
                "team_allocation",
                "resource_planning",
                "skill_matching",
                "workload_balancing",
                "capacity_planning"
            ],
            endpoints={
                "base_url": f"http://localhost:{self.port}",
                "send_message": f"http://localhost:{self.port}/api/send_message"
            },
            contact={
                "email": "resource@taskmanagement.com"
            }
        )
    
    async def process_message(self, request: SendMessageRequest) -> MessageResponse:
        """Process resource allocation request"""
        message = request.params.message
        content = message.parts[0].root.text
        
        # Extract skills and requirements from content
        required_skills = self.extract_required_skills(content)
        
        # Allocate resources based on requirements
        allocation = self.allocate_resources(required_skills, content)
        
        # Generate response
        response_text = self.format_resource_response(allocation, required_skills)
        
        return MessageResponse(
            id=str(uuid.uuid4()),
            response=self.create_message(response_text),
            resource_allocation=allocation
        )
    
    def extract_required_skills(self, content: str) -> List[str]:
        """Extract required skills from task breakdown content"""
        skills = set()
        content_lower = content.lower()
        
        # Map common terms to skills
        skill_mapping = {
            "backend": ["backend_development", "api_design"],
            "frontend": ["frontend_development", "javascript"],
            "database": ["database_design", "database_administration", "sql"],
            "testing": ["testing", "test_automation", "integration_testing"],
            "design": ["ui_design", "ux_design", "system_design"],
            "analysis": ["business_analysis", "technical_analysis"],
            "deployment": ["devops", "infrastructure", "deployment"],
            "research": ["research", "analysis"],
            "architecture": ["architecture", "system_design"]
        }
        
        for term, skill_list in skill_mapping.items():
            if term in content_lower:
                skills.update(skill_list)
        
        return list(skills)
    
    def allocate_resources(self, required_skills: List[str], content: str) -> Dict[str, Any]:
        """Allocate team members based on required skills"""
        allocation = {
            "teams": [],
            "total_members": 0,
            "estimated_cost": 0,
            "timeline": {},
            "recommendations": []
        }
        
        # Analyze project complexity to determine team size
        complexity = self.analyze_project_complexity(content)
        
        # Get skill matches
        skill_matches = self.find_skill_matches(required_skills)
        
        # Create teams based on project phases
        teams = self.create_teams(skill_matches, complexity)
        
        allocation["teams"] = teams
        allocation["total_members"] = sum(len(team["members"]) for team in teams)
        allocation["estimated_cost"] = self.calculate_estimated_cost(teams)
        allocation["timeline"] = self.create_resource_timeline(teams)
        allocation["recommendations"] = self.generate_recommendations(teams, required_skills)
        
        return allocation
    
    def analyze_project_complexity(self, content: str) -> str:
        """Analyze project complexity from content"""
        content_lower = content.lower()
        
        complexity_indicators = {
            "high": ["architecture", "system design", "multiple", "complex", "integration"],
            "medium": ["development", "testing", "deployment"],
            "low": ["simple", "basic", "minimal"]
        }
        
        scores = {"high": 0, "medium": 0, "low": 0}
        
        for level, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in content_lower:
                    scores[level] += 1
        
        return max(scores, key=scores.get)
    
    def find_skill_matches(self, required_skills: List[str]) -> Dict[str, List[Dict]]:
        """Find team members that match required skills"""
        matches = {"perfect": [], "good": [], "partial": []}
        
        all_members = []
        for category, members in self.available_resources.items():
            for member in members:
                member["category"] = category
                all_members.append(member)
        
        for member in all_members:
            member_skills = set(member["skills"])
            required_set = set(required_skills)
            
            overlap = len(member_skills.intersection(required_set))
            coverage = overlap / len(required_set) if required_set else 0
            
            if coverage >= 0.7:
                matches["perfect"].append({**member, "coverage": coverage})
            elif coverage >= 0.4:
                matches["good"].append({**member, "coverage": coverage})
            elif coverage > 0:
                matches["partial"].append({**member, "coverage": coverage})
        
        return matches
    
    def create_teams(self, skill_matches: Dict[str, List[Dict]], complexity: str) -> List[Dict[str, Any]]:
        """Create teams based on skill matches and complexity"""
        teams = []
        
        # Determine team structure based on complexity
        if complexity == "high":
            teams = self.create_complex_project_teams(skill_matches)
        elif complexity == "medium":
            teams = self.create_medium_project_teams(skill_matches)
        else:
            teams = self.create_simple_project_teams(skill_matches)
        
        return teams
    
    def create_complex_project_teams(self, skill_matches: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Create teams for complex projects"""
        teams = []
        
        # Core Development Team
        core_team = {
            "name": "Core Development Team",
            "role": "Primary development and architecture",
            "members": [],
            "lead": None
        }
        
        # Add senior developers and architects
        perfect_matches = sorted(skill_matches["perfect"], key=lambda x: x["coverage"], reverse=True)
        for member in perfect_matches[:3]:
            core_team["members"].append(member)
            if not core_team["lead"] and "architecture" in member["skills"]:
                core_team["lead"] = member["name"]
        
        if not core_team["lead"] and core_team["members"]:
            core_team["lead"] = core_team["members"][0]["name"]
        
        teams.append(core_team)
        
        # QA and Testing Team
        qa_team = {
            "name": "QA & Testing Team",
            "role": "Testing and quality assurance",
            "members": [],
            "lead": None
        }
        
        # Add testing specialists
        for member in skill_matches["good"] + skill_matches["partial"]:
            if "testing" in member["skills"] or "test_automation" in member["skills"]:
                qa_team["members"].append(member)
                if not qa_team["lead"]:
                    qa_team["lead"] = member["name"]
        
        if qa_team["members"]:
            teams.append(qa_team)
        
        return teams
    
    def create_medium_project_teams(self, skill_matches: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Create teams for medium complexity projects"""
        team = {
            "name": "Development Team",
            "role": "Full-stack development and delivery",
            "members": [],
            "lead": None
        }
        
        # Add best matches
        all_matches = skill_matches["perfect"] + skill_matches["good"]
        all_matches = sorted(all_matches, key=lambda x: x["coverage"], reverse=True)
        
        team["members"] = all_matches[:4]
        if team["members"]:
            team["lead"] = team["members"][0]["name"]
        
        return [team]
    
    def create_simple_project_teams(self, skill_matches: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Create teams for simple projects"""
        team = {
            "name": "Small Development Team",
            "role": "End-to-end development",
            "members": [],
            "lead": None
        }
        
        # Add minimal team
        all_matches = skill_matches["perfect"] + skill_matches["good"] + skill_matches["partial"]
        all_matches = sorted(all_matches, key=lambda x: x["coverage"], reverse=True)
        
        team["members"] = all_matches[:2]
        if team["members"]:
            team["lead"] = team["members"][0]["name"]
        
        return [team]
    
    def calculate_estimated_cost(self, teams: List[Dict[str, Any]]) -> int:
        """Calculate estimated project cost based on team composition"""
        cost_per_hour = {
            "senior_developers": 150,
            "mid_developers": 100,
            "specialists": 120,
            "analysts": 90
        }
        
        total_cost = 0
        estimated_project_hours = 200  # Base estimate
        
        for team in teams:
            for member in team["members"]:
                category = member.get("category", "mid_developers")
                hourly_rate = cost_per_hour.get(category, 100)
                total_cost += hourly_rate * estimated_project_hours
        
        return total_cost
    
    def create_resource_timeline(self, teams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create resource allocation timeline"""
        return {
            "phase_1": "Team formation and project kickoff (Week 1-2)",
            "phase_2": "Active development phase (Week 3-6)", 
            "phase_3": "Testing and finalization (Week 7-8)",
            "total_duration": "8 weeks",
            "peak_utilization": f"Week 3-6 with {sum(len(team['members']) for team in teams)} team members"
        }
    
    def generate_recommendations(self, teams: List[Dict[str, Any]], required_skills: List[str]) -> List[str]:
        """Generate recommendations for resource allocation"""
        recommendations = []
        
        total_members = sum(len(team["members"]) for team in teams)
        
        if total_members < 3:
            recommendations.append("Consider hiring additional resources for faster delivery")
        elif total_members > 8:
            recommendations.append("Large team size may require additional coordination overhead")
        
        # Check skill coverage
        all_skills = set()
        for team in teams:
            for member in team["members"]:
                all_skills.update(member["skills"])
        
        missing_skills = set(required_skills) - all_skills
        if missing_skills:
            recommendations.append(f"Consider training or hiring for missing skills: {', '.join(missing_skills)}")
        
        recommendations.append("Regular team meetings recommended for coordination")
        recommendations.append("Consider agile methodology for iterative delivery")
        
        return recommendations
    
    def format_resource_response(self, allocation: Dict[str, Any], required_skills: List[str]) -> str:
        """Format resource allocation as readable text"""
        response = "[RESOURCES] RESOURCE ALLOCATION PLAN:\n\n"
        
        # Team composition
        for i, team in enumerate(allocation["teams"], 1):
            response += f"[TEAM{i}] {team['name']}\n"
            response += f"        [ROLE] {team['role']}\n"
            response += f"        [LEAD] {team.get('lead', 'TBD')}\n"
            response += f"        [MEMBERS] ({len(team['members'])}):\n"
            
            for member in team["members"]:
                skills_str = ", ".join(member["skills"][:3])  # Show first 3 skills
                if len(member["skills"]) > 3:
                    skills_str += "..."
                response += f"          [MEMBER] {member['name']} ({member['category']}) - {skills_str}\n"
            response += "\n"
        
        # Summary statistics
        response += f"[SUMMARY] ALLOCATION SUMMARY:\n"
        response += f"          [TOTAL] Team Members: {allocation['total_members']}\n"
        response += f"          [COST] Estimated Cost: ${allocation['estimated_cost']:,}\n"
        response += f"          [TIME] Timeline: {allocation['timeline']['total_duration']}\n\n"
        
        # Timeline
        response += f"[TIMELINE] RESOURCE TIMELINE:\n"
        for phase, description in allocation['timeline'].items():
            if phase != 'total_duration':
                response += f"           [PHASE] {description}\n"
        response += "\n"
        
        # Recommendations
        if allocation["recommendations"]:
            response += f"[RECOMMEND] RECOMMENDATIONS:\n"
            for rec in allocation["recommendations"]:
                response += f"            [TIP] {rec}\n"
        
        response += "\n[STATUS] Resource allocation complete - team ready for project execution"
        
        return response


if __name__ == "__main__":
    agent = ResourceAgent()
    agent.run()
