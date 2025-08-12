#!/usr/bin/env python3
"""
A2A GitHub Integration Demo
==========================
Run the A2A system with GitHub Issues and Local Project Manager
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the parent directory to sys.path to import src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.agents.supervisor_agent import SupervisorAgent
    from src.tools.github_integration import GitHubIntegration
    from src.tools.local_project_manager import LocalProjectManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

async def demo_github_integration():
    """Demo the GitHub integration functionality"""
    
    print("🐙 Testing GitHub Integration")
    print("=" * 50)
    
    # Initialize GitHub tool
    github = GitHubIntegration()
    
    # Test data
    project_name = "A2A Demo E-commerce Project"
    milestones = [
        {
            "title": "Backend API Development",
            "description": "Create REST APIs for user management and product catalog",
            "due_date": "2025-09-15"
        },
        {
            "title": "Frontend UI Implementation", 
            "description": "Build responsive React frontend with shopping cart",
            "due_date": "2025-10-01"
        }
    ]
    
    tasks = [
        {
            "title": "User Authentication API",
            "description": "Implement JWT-based authentication system",
            "time_estimate": "16 hours",
            "priority": "High",
            "milestone": "Backend API Development"
        },
        {
            "title": "Product Catalog API",
            "description": "Create CRUD operations for product management",
            "time_estimate": "12 hours", 
            "priority": "High",
            "milestone": "Backend API Development"
        },
        {
            "title": "Shopping Cart Component",
            "description": "React component for cart management",
            "time_estimate": "10 hours",
            "priority": "Medium",
            "milestone": "Frontend UI Implementation"
        }
    ]
    
    team_members = [
        {"name": "Alex Smith", "role": "Backend Developer"},
        {"name": "Sarah Lee", "role": "Frontend Developer"}
    ]
    
    # Create GitHub project
    print("📝 Creating GitHub Issues and Project...")
    result = github.create_project_issues(project_name, milestones, tasks, team_members)
    
    if result.get("error"):
        print(f"❌ GitHub Error: {result['error']}")
        print("💡 This might be demo mode - check your GitHub token in .env file")
    else:
        print(f"✅ GitHub Project Created!")
        print(f"📊 Repository: {result.get('repository_name', 'Unknown')}")
        print(f"🎯 Issues Created: {len(result.get('issues_created', []))}")
        print(f"📅 Milestones: {len(result.get('milestones_created', []))}")
        
        # Show some issues
        issues = result.get('issues_created', [])
        if issues:
            print("\n📋 Sample Issues Created:")
            for issue in issues[:3]:
                print(f"  • #{issue.get('number', '?')}: {issue.get('title', 'Unknown')}")
    
    return result

async def demo_supervisor_agent():
    """Demo the full Supervisor Agent with GitHub integration"""
    
    print("\n🤖 Testing A2A Supervisor Agent")
    print("=" * 50)
    
    # Initialize supervisor
    supervisor = SupervisorAgent()
    
    # Test mission
    mission = "Create a modern e-commerce mobile application with secure payment processing, user authentication, product catalog, and order management system"
    
    print(f"📨 Mission: {mission}")
    print("\n🔄 Starting A2A coordination...")
    
    try:
        # This will coordinate with other agents and create GitHub issues + local files
        result = await supervisor.handle_mission(mission)
        
        print("✅ A2A Coordination Complete!")
        print("\n" + "="*60)
        print("📋 FINAL PROJECT PLAN:")
        print("="*60)
        print(result)
        
    except Exception as e:
        print(f"❌ Error in A2A coordination: {e}")
        print("💡 Make sure all agents are running and GitHub token is configured")

async def demo_local_project_manager():
    """Demo the Local Project Manager"""
    
    print("\n📁 Testing Local Project Manager")
    print("=" * 50)
    
    from src.tools.local_project_manager import LocalProjectManager
    
    local_pm = LocalProjectManager()
    
    # Sample data
    project_name = "A2A GitHub Demo Project"
    milestones = [
        {"title": "Setup Phase", "duration": "1 week"},
        {"title": "Development Phase", "duration": "4 weeks"},
        {"title": "Testing Phase", "duration": "1 week"}
    ]
    
    tasks = [
        {"title": "Environment Setup", "time_estimate": "4 hours", "priority": "High"},
        {"title": "Database Design", "time_estimate": "8 hours", "priority": "High"},
        {"title": "API Development", "time_estimate": "24 hours", "priority": "Medium"}
    ]
    
    team_members = [
        {"name": "John Doe", "role": "Full-Stack Developer", "skills": {"python": 8, "react": 7}},
        {"name": "Jane Smith", "role": "UI Designer", "skills": {"design": 9, "figma": 8}}
    ]
    
    # Create project structure
    result = local_pm.create_project_structure(project_name, milestones, tasks, team_members)
    
    print(f"✅ Local Project Created!")
    print(f"📁 Path: {result['project_path']}")
    print(f"📄 Files: {len(result['files_created'])}")
    
    print("\n📋 Files Created:")
    for file_path in result['files_created']:
        file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
        print(f"  • {file_name}")
    
    return result

def print_instructions():
    """Print usage instructions"""
    
    print("""
🎯 A2A GITHUB INTEGRATION GUIDE
═══════════════════════════════════════════════════════════════

🔧 SETUP INSTRUCTIONS:

1. GitHub Token Setup:
   - Go to: https://github.com/settings/tokens
   - Generate new token with 'repo' permissions
   - Update .env file with your token:
     GITHUB_TOKEN=your_token_here
     GITHUB_REPO_OWNER=your_username
     GITHUB_REPO_NAME=your_repository

2. Run A2A Agents:
   - Open 4 terminals
   - Terminal 1: python -m src.agents.supervisor_agent
   - Terminal 2: python -m src.agents.milestone_agent  
   - Terminal 3: python -m src.agents.task_agent
   - Terminal 4: python -m src.agents.resource_agent

3. Test the System:
   - Run: python demo_github_integration.py
   - Check your GitHub repository for new issues
   - Check a2a_projects/ folder for local files

🚀 WHAT THE SYSTEM CREATES:

GitHub:
- ✅ Repository issues for each task
- ✅ Milestones with due dates
- ✅ Project board organization
- ✅ Labels and assignments

Local Files:
- ✅ PROJECT_OVERVIEW.md - Project summary
- ✅ TASKS.csv - Spreadsheet for task management
- ✅ GANTT_CHART.html - Visual timeline
- ✅ TEAM.json - Team member details
- ✅ README.md - Instructions

💡 TIPS:
- Use real GitHub repository for best results
- CSV files work great with Excel/Google Sheets
- HTML Gantt chart opens in any browser
- All files are git-friendly for version control
""")

async def main():
    """Main demo function"""
    
    print("🚀 A2A GITHUB INTEGRATION DEMO")
    print("=" * 60)
    
    # Check environment
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token or github_token == 'your_token_here':
        print("⚠️ GitHub token not configured!")
        print("💡 Update .env file with your GitHub token for full functionality")
        print("🔧 Demo will run in offline mode")
        print()
    
    # Run demos
    try:
        # Test 1: GitHub Integration
        await demo_github_integration()
        
        # Test 2: Local Project Manager  
        await demo_local_project_manager()
        
        # Test 3: Full Supervisor Agent (if you want to test full A2A flow)
        choice = input("\n🤖 Run full A2A Supervisor Agent demo? (y/n): ").lower()
        if choice == 'y':
            await demo_supervisor_agent()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED!")
        print("🎯 Your A2A system is ready with GitHub integration!")
        print("="*60)
        
        # Show instructions
        print_instructions()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
