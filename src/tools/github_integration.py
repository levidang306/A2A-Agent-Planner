"""
🐙 GitHub Issues Integration Tool for A2A System
================================================
Alternative to Trello - Creates real GitHub issues for project management
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import base64

class GitHubProjectManager:
    def __init__(self, token: str = None, repo_owner: str = None, repo_name: str = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repo_owner = repo_owner or os.getenv('GITHUB_REPO_OWNER', 'your-username')
        self.repo_name = repo_name or os.getenv('GITHUB_REPO_NAME', 'a2a-projects')
        self.base_url = "https://api.github.com"
        
        self.headers = {
            'Authorization': f'token {self.token}' if self.token else None,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        if not self.token:
            print("⚠️ GitHub token not found. Using demo mode.")
            self.demo_mode = True
        else:
            self.demo_mode = False
    
    def create_project_repository(self, project_name: str, description: str) -> Dict[str, Any]:
        """Create a new GitHub repository for the project"""
        if self.demo_mode:
            return self._demo_create_repo(project_name, description)
        
        repo_data = {
            "name": f"a2a-{project_name.lower().replace(' ', '-')}",
            "description": f"A2A Generated Project: {description}",
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "auto_init": True,
            "gitignore_template": "Python"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=repo_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "demo_mode": True}
    
    def create_milestone_issues(self, repo_name: str, milestones: List[Dict]) -> List[Dict[str, Any]]:
        """Create GitHub issues for milestones"""
        if self.demo_mode:
            return self._demo_create_issues(repo_name, milestones, "milestone")
        
        created_issues = []
        
        for i, milestone in enumerate(milestones):
            issue_data = {
                "title": f"🎯 Milestone {i+1}: {milestone.get('title', 'Milestone')}",
                "body": self._format_milestone_body(milestone),
                "labels": ["milestone", "high-priority"],
                "assignees": []
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/repos/{self.repo_owner}/{repo_name}/issues",
                    headers=self.headers,
                    json=issue_data
                )
                response.raise_for_status()
                created_issues.append(response.json())
            except Exception as e:
                created_issues.append({"error": str(e), "title": milestone.get('title', 'Milestone')})
        
        return created_issues
    
    def create_task_issues(self, repo_name: str, tasks: List[Dict], team_members: List[Dict]) -> List[Dict[str, Any]]:
        """Create GitHub issues for tasks with time estimates"""
        if self.demo_mode:
            return self._demo_create_issues(repo_name, tasks, "task")
        
        created_issues = []
        
        for i, task in enumerate(tasks):
            # Assign to team member (use first available)
            assignee = team_members[i % len(team_members)]['name'].lower().replace(' ', '') if team_members else None
            
            issue_data = {
                "title": f"📝 Task {i+1}: {task.get('title', 'Task')}",
                "body": self._format_task_body(task),
                "labels": self._get_task_labels(task),
                "assignees": [assignee] if assignee else []
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/repos/{self.repo_owner}/{repo_name}/issues",
                    headers=self.headers,
                    json=issue_data
                )
                response.raise_for_status()
                created_issues.append(response.json())
            except Exception as e:
                created_issues.append({"error": str(e), "title": task.get('title', 'Task')})
        
        return created_issues
    
    def create_project_board(self, repo_name: str, project_name: str) -> Dict[str, Any]:
        """Create GitHub project board"""
        if self.demo_mode:
            return self._demo_create_board(project_name)
        
        board_data = {
            "name": f"A2A Project: {project_name}",
            "body": f"Project management board generated by A2A system for {project_name}",
            "organization_permission": "read"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/repos/{self.repo_owner}/{repo_name}/projects",
                headers=self.headers,
                json=board_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "demo_mode": True}
    
    def _format_milestone_body(self, milestone: Dict) -> str:
        """Format milestone issue body"""
        return f"""## 🎯 Milestone Description

{milestone.get('description', 'No description provided')}

## ⏱️ Timeline
- **Duration**: {milestone.get('duration', 'TBD')}
- **Dependencies**: {milestone.get('dependencies', 'None')}

## 📋 Success Criteria
- [ ] All associated tasks completed
- [ ] Quality assurance passed
- [ ] Documentation updated
- [ ] Stakeholder approval received

---
*Generated by A2A System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _format_task_body(self, task: Dict) -> str:
        """Format task issue body with time estimates"""
        return f"""## 📝 Task Description

{task.get('description', 'No description provided')}

## ⏱️ Time Estimate
**Estimated Time**: {task.get('time_estimate', 'TBD')}

## 🔧 Technical Details
{task.get('technical_details', 'See task description above')}

## ✅ Acceptance Criteria
- [ ] Implementation completed
- [ ] Unit tests written and passing
- [ ] Code review completed
- [ ] Documentation updated

## 🏷️ Task Information
- **Priority**: {task.get('priority', 'Medium')}
- **Dependencies**: {task.get('dependencies', 'None')}
- **Skills Required**: {', '.join(task.get('required_skills', []))}

---
*Generated by A2A System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _get_task_labels(self, task: Dict) -> List[str]:
        """Get appropriate labels for task"""
        labels = ["task"]
        
        priority = task.get('priority', 'medium').lower()
        if priority == 'high':
            labels.append("high-priority")
        elif priority == 'low':
            labels.append("low-priority")
        
        # Add technical labels based on description
        description = task.get('description', '').lower()
        if 'frontend' in description or 'ui' in description:
            labels.append("frontend")
        if 'backend' in description or 'api' in description:
            labels.append("backend")
        if 'database' in description or 'db' in description:
            labels.append("database")
        if 'design' in description or 'ux' in description:
            labels.append("design")
        
        return labels
    
    # Demo mode methods
    def _demo_create_repo(self, project_name: str, description: str) -> Dict[str, Any]:
        return {
            "id": f"demo_repo_{hash(project_name) % 10000}",
            "name": f"a2a-{project_name.lower().replace(' ', '-')}",
            "full_name": f"{self.repo_owner}/a2a-{project_name.lower().replace(' ', '-')}",
            "description": description,
            "html_url": f"https://github.com/{self.repo_owner}/a2a-{project_name.lower().replace(' ', '-')}",
            "issues_url": f"https://api.github.com/repos/{self.repo_owner}/a2a-{project_name.lower().replace(' ', '-')}/issues{{/number}}",
            "demo_mode": True,
            "created_at": datetime.now().isoformat()
        }
    
    def _demo_create_issues(self, repo_name: str, items: List[Dict], item_type: str) -> List[Dict[str, Any]]:
        issues = []
        for i, item in enumerate(items):
            issues.append({
                "id": f"demo_issue_{item_type}_{i+1}",
                "number": i + 1,
                "title": f"{'🎯' if item_type == 'milestone' else '📝'} {item_type.title()} {i+1}: {item.get('title', item_type.title())}",
                "html_url": f"https://github.com/{self.repo_owner}/{repo_name}/issues/{i+1}",
                "state": "open",
                "labels": [{"name": item_type}, {"name": "a2a-generated"}],
                "demo_mode": True,
                "created_at": datetime.now().isoformat()
            })
        return issues
    
    def _demo_create_board(self, project_name: str) -> Dict[str, Any]:
        return {
            "id": f"demo_board_{hash(project_name) % 10000}",
            "name": f"A2A Project: {project_name}",
            "html_url": f"https://github.com/{self.repo_owner}/a2a-{project_name.lower().replace(' ', '-')}/projects/1",
            "demo_mode": True,
            "created_at": datetime.now().isoformat()
        }

# Example usage and testing
if __name__ == "__main__":
    github_pm = GitHubProjectManager()
    
    # Demo project creation
    demo_milestones = [
        {
            "title": "Project Setup & Planning",
            "description": "Initial project setup, requirements gathering, and team coordination",
            "duration": "2 weeks",
            "dependencies": "None"
        },
        {
            "title": "Core Development Phase",
            "description": "Main development work including backend and frontend implementation",
            "duration": "6 weeks", 
            "dependencies": "Project Setup"
        }
    ]
    
    demo_tasks = [
        {
            "title": "Setup Development Environment",
            "description": "Configure development tools, repositories, and CI/CD pipeline",
            "time_estimate": "8 hours",
            "priority": "High",
            "required_skills": ["DevOps", "Git"]
        },
        {
            "title": "Database Design",
            "description": "Design database schema and relationships",
            "time_estimate": "16 hours",
            "priority": "High",
            "required_skills": ["Database", "SQL"]
        }
    ]
    
    demo_team = [
        {"name": "John Doe", "role": "Full-stack Developer"},
        {"name": "Jane Smith", "role": "UI/UX Designer"}
    ]
    
    # Create repository
    repo_result = github_pm.create_project_repository("E-commerce Platform Demo", "Demo e-commerce platform")
    print("🐙 GitHub Repository Created:")
    print(json.dumps(repo_result, indent=2))
    
    # Create milestone issues
    milestone_issues = github_pm.create_milestone_issues("a2a-ecommerce-platform-demo", demo_milestones)
    print("\\n🎯 Milestone Issues Created:")
    print(json.dumps(milestone_issues, indent=2))
    
    # Create task issues
    task_issues = github_pm.create_task_issues("a2a-ecommerce-platform-demo", demo_tasks, demo_team)
    print("\\n📝 Task Issues Created:")
    print(json.dumps(task_issues, indent=2))
