"""
🔗 Enhanced Trello Integration with Timeline Features
====================================================
Integrates timeline, calendar, milestones, and meeting scheduling into Trello
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

logger = logging.getLogger(__name__)

class TrelloTimelineIntegration:
    def __init__(self, api_key: str, api_token: str):
        self.api_key = api_key
        self.api_token = api_token
        self.base_url = "https://api.trello.com/1"
        
    def create_project_board_with_timeline(self, project_name: str, milestones: List[Dict], 
                                         tasks: List[Dict], timeline: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a comprehensive project board with timeline features"""
        
        try:
            # Step 1: Create the main project board
            board_id = self.create_board(f"📅 {project_name} - Timeline")
            if not board_id:
                return {"error": "Failed to create main board"}
            
            # Step 2: Create timeline-based lists
            lists = self.create_timeline_lists(board_id)
            if not lists:
                return {"error": "Failed to create timeline lists"}
            
            # Step 3: Create milestone cards with dates
            milestone_cards = self.create_milestone_cards(lists, milestones, timeline)
            
            # Step 4: Create task cards with scheduling
            task_cards = self.create_task_cards(lists, tasks, timeline)
            
            # Step 5: Create calendar/meeting cards
            meeting_cards = self.create_meeting_schedule_cards(lists, timeline)
            
            # Step 6: Create release/sprint cards
            release_cards = self.create_release_cards(lists, timeline)
            
            result = {
                "board_id": board_id,
                "board_name": f"📅 {project_name} - Timeline",
                "board_url": f"https://trello.com/b/{board_id}",
                "lists": lists,
                "milestone_cards": milestone_cards,
                "task_cards": task_cards,
                "meeting_cards": meeting_cards,
                "release_cards": release_cards,
                "total_cards": len(milestone_cards) + len(task_cards) + len(meeting_cards) + len(release_cards),
                "timeline_summary": {
                    "project_start": timeline.get("project_start"),
                    "project_end": timeline.get("project_summary", {}).get("project_end"),
                    "total_duration": timeline.get("project_summary", {}).get("total_duration_days"),
                    "milestones": len(milestones),
                    "tasks": len(tasks)
                }
            }
            
            logger.info(f"Successfully created timeline board with {result['total_cards']} cards")
            return result
            
        except Exception as e:
            logger.error(f"Error creating timeline board: {e}")
            return {"error": f"Timeline board creation failed: {str(e)}"}
    
    def create_timeline_lists(self, board_id: str) -> Dict[str, str]:
        """Create timeline-based lists for project management"""
        
        timeline_lists = [
            "📋 Project Overview",
            "🎯 Milestones",
            "📅 Sprint Planning", 
            "🔄 In Progress",
            "👥 Team Meetings",
            "🚀 Releases",
            "✅ Completed",
            "📊 Reviews & Retrospective"
        ]
        
        lists = {}
        
        # Get existing lists first
        existing_lists = self.get_lists_on_board(board_id)
        if existing_lists:
            # Archive default lists
            for lst in existing_lists:
                self.archive_list(lst['id'])
        
        # Create timeline lists
        for list_name in timeline_lists:
            list_id = self.create_list(board_id, list_name)
            if list_id:
                lists[list_name] = list_id
                logger.info(f"Created timeline list: {list_name}")
        
        return lists
    
    def create_milestone_cards(self, lists: Dict[str, str], milestones: List[Dict], 
                             timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create milestone cards with timeline information"""
        
        milestone_cards = []
        milestones_list_id = lists.get("🎯 Milestones")
        
        if not milestones_list_id:
            logger.warning("Milestones list not found")
            return milestone_cards
        
        # Get milestone timeline data
        milestone_timeline = timeline.get("milestones_timeline", [])
        
        for i, milestone in enumerate(milestones):
            # Get corresponding timeline data
            timeline_data = milestone_timeline[i] if i < len(milestone_timeline) else {}
            
            # Create milestone card
            card_name = f"🎯 {milestone.get('title', f'Milestone {i+1}')}"
            
            description = f"""**Milestone #{i+1}**

📝 **Description:**
{milestone.get('description', 'No description provided')}

📅 **Timeline:**
• Start Date: {timeline_data.get('start_date', 'TBD')}
• End Date: {timeline_data.get('end_date', 'TBD')}
• Duration: {timeline_data.get('duration_days', 0)} days

🎯 **Objectives:**
{milestone.get('objectives', 'Define milestone objectives')}

📊 **Success Criteria:**
{milestone.get('success_criteria', 'Define success criteria')}

🔗 **Dependencies:**
{', '.join(milestone.get('dependencies', [])) if milestone.get('dependencies') else 'None'}

*Generated by A2A Timeline System*
"""
            
            # Create the card with due date
            card_id = self.create_card_with_timeline(
                list_id=milestones_list_id,
                card_name=card_name,
                description=description,
                due_date=timeline_data.get('end_date'),
                start_date=timeline_data.get('start_date'),
                labels=["Milestone", "High Priority"]
            )
            
            if card_id:
                milestone_cards.append({
                    "card_id": card_id,
                    "milestone_title": milestone.get('title'),
                    "start_date": timeline_data.get('start_date'),
                    "end_date": timeline_data.get('end_date'),
                    "duration_days": timeline_data.get('duration_days')
                })
        
        return milestone_cards
    
    def create_task_cards(self, lists: Dict[str, str], tasks: List[Dict], 
                         timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create task cards with scheduling and assignment"""
        
        task_cards = []
        planning_list_id = lists.get("📅 Sprint Planning")
        
        if not planning_list_id:
            logger.warning("Sprint Planning list not found")
            return task_cards
        
        # Get task timeline data
        task_timeline = timeline.get("tasks_timeline", [])
        
        for i, task in enumerate(tasks):
            # Get corresponding timeline data
            timeline_data = task_timeline[i] if i < len(task_timeline) else {}
            
            card_name = f"📝 {task.get('title', f'Task {i+1}')}"
            
            description = f"""**Task #{i+1}**

📝 **Description:**
{task.get('description', 'No description provided')}

⏰ **Timeline:**
• Start Date: {timeline_data.get('start_date', 'TBD')}
• End Date: {timeline_data.get('end_date', 'TBD')}
• Duration: {timeline_data.get('duration_days', 0)} days
• Time Estimate: {timeline_data.get('time_estimate', 'TBD')}

👤 **Assignment:**
• Assigned to: {timeline_data.get('assigned_to', 'Unassigned')}
• Priority: {timeline_data.get('priority', 'Medium')}

🔧 **Skills Required:**
{', '.join(task.get('skills_required', [])) if task.get('skills_required') else 'None specified'}

🔗 **Dependencies:**
{', '.join(task.get('dependencies', [])) if task.get('dependencies') else 'None'}

📊 **Status:** {timeline_data.get('status', 'Planned')}

*Generated by A2A Task System*
"""
            
            # Create task card with timeline
            card_id = self.create_card_with_timeline(
                list_id=planning_list_id,
                card_name=card_name,
                description=description,
                due_date=timeline_data.get('end_date'),
                start_date=timeline_data.get('start_date'),
                labels=[timeline_data.get('priority', 'Medium'), "Task"]
            )
            
            if card_id:
                task_cards.append({
                    "card_id": card_id,
                    "task_title": task.get('title'),
                    "assigned_to": timeline_data.get('assigned_to'),
                    "start_date": timeline_data.get('start_date'),
                    "end_date": timeline_data.get('end_date'),
                    "priority": timeline_data.get('priority')
                })
        
        return task_cards
    
    def create_meeting_schedule_cards(self, lists: Dict[str, str], timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create meeting and calendar event cards"""
        
        meeting_cards = []
        meetings_list_id = lists.get("👥 Team Meetings")
        
        if not meetings_list_id:
            logger.warning("Team Meetings list not found")
            return meeting_cards
        
        # Get project timeline info
        project_start = timeline.get("project_start")
        project_end = timeline.get("project_summary", {}).get("project_end")
        
        if not project_start or not project_end:
            return meeting_cards
        
        # Define meeting schedule
        meetings = [
            {
                "name": "🚀 Project Kickoff Meeting",
                "description": "Project initiation, team introductions, goals alignment",
                "offset_days": 1,
                "duration": "2 hours",
                "frequency": "Once"
            },
            {
                "name": "📅 Sprint Planning Meeting",
                "description": "Plan upcoming sprint, assign tasks, set goals",
                "offset_days": 7,
                "duration": "1.5 hours", 
                "frequency": "Weekly"
            },
            {
                "name": "🔄 Daily Standup",
                "description": "Daily progress check, blockers discussion",
                "offset_days": 2,
                "duration": "15 minutes",
                "frequency": "Daily"
            },
            {
                "name": "📊 Sprint Review & Demo",
                "description": "Demo completed features, stakeholder feedback",
                "offset_days": 14,
                "duration": "1 hour",
                "frequency": "Bi-weekly"
            },
            {
                "name": "🔍 Sprint Retrospective",
                "description": "Team retrospective, process improvements",
                "offset_days": 14,
                "duration": "45 minutes",
                "frequency": "Bi-weekly"
            },
            {
                "name": "🎯 Milestone Review",
                "description": "Milestone progress review, adjustments",
                "offset_days": 30,
                "duration": "1 hour",
                "frequency": "Monthly"
            }
        ]
        
        for meeting in meetings:
            meeting_date = self._calculate_meeting_date(project_start, meeting["offset_days"])
            
            card_name = f"{meeting['name']}"
            
            description = f"""**{meeting['name']}**

📅 **Meeting Details:**
• Date: {meeting_date}
• Duration: {meeting['duration']}
• Frequency: {meeting['frequency']}

📝 **Description:**
{meeting['description']}

👥 **Attendees:**
• All team members
• Project stakeholders (as needed)

📋 **Agenda:**
• Review progress
• Discuss blockers
• Plan next steps
• Action items assignment

🔗 **Meeting Link:** [Add video conference link]

*Auto-scheduled by A2A Timeline System*
"""
            
            card_id = self.create_card_with_timeline(
                list_id=meetings_list_id,
                card_name=card_name,
                description=description,
                due_date=meeting_date,
                labels=["Meeting", "Calendar"]
            )
            
            if card_id:
                meeting_cards.append({
                    "card_id": card_id,
                    "meeting_name": meeting["name"],
                    "meeting_date": meeting_date,
                    "duration": meeting["duration"],
                    "frequency": meeting["frequency"]
                })
        
        return meeting_cards
    
    def create_release_cards(self, lists: Dict[str, str], timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create release and deployment cards"""
        
        release_cards = []
        releases_list_id = lists.get("🚀 Releases")
        
        if not releases_list_id:
            logger.warning("Releases list not found")
            return release_cards
        
        # Get milestones to create releases
        milestones_timeline = timeline.get("milestones_timeline", [])
        
        for i, milestone in enumerate(milestones_timeline):
            release_version = f"v{i+1}.0"
            release_date = milestone.get("end_date")
            
            card_name = f"🚀 Release {release_version}"
            
            description = f"""**Release {release_version}**

📅 **Release Schedule:**
• Target Date: {release_date}
• Milestone: {milestone.get('title', f'Milestone {i+1}')}

📦 **Release Contents:**
• Features completed in {milestone.get('title', f'Milestone {i+1}')}
• Bug fixes and improvements
• Documentation updates

✅ **Release Checklist:**
- [ ] Code review completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Deployment scripts ready
- [ ] Rollback plan prepared
- [ ] Stakeholder approval received

🔍 **Testing Requirements:**
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] User acceptance testing
- [ ] Load testing (if applicable)

📋 **Deployment Plan:**
1. Pre-deployment checks
2. Database migrations (if any)
3. Application deployment
4. Post-deployment verification
5. Monitoring and alerts setup

🎯 **Success Criteria:**
- All features working as expected
- No critical bugs
- Performance within acceptable limits
- User feedback positive

*Auto-generated for Milestone: {milestone.get('title', f'Milestone {i+1}')}*
"""
            
            card_id = self.create_card_with_timeline(
                list_id=releases_list_id,
                card_name=card_name,
                description=description,
                due_date=release_date,
                labels=["Release", "High Priority"]
            )
            
            if card_id:
                release_cards.append({
                    "card_id": card_id,
                    "release_version": release_version,
                    "release_date": release_date,
                    "milestone": milestone.get('title')
                })
        
        return release_cards
    
    def create_card_with_timeline(self, list_id: str, card_name: str, description: str = "",
                                 due_date: str = None, start_date: str = None, 
                                 labels: List[str] = None) -> Optional[str]:
        """Create a card with timeline features (due date, start date, labels)"""
        
        url = f"{self.base_url}/cards"
        params = {
            "idList": list_id,
            "name": card_name,
            "desc": description,
            "key": self.api_key,
            "token": self.api_token
        }
        
        # Add due date if provided
        if due_date:
            try:
                # Convert to Trello format (ISO 8601)
                due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                params["due"] = due_datetime.isoformat() + "Z"
            except ValueError:
                logger.warning(f"Invalid due date format: {due_date}")
        
        # Add start date if provided  
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                params["start"] = start_datetime.isoformat() + "Z"
            except ValueError:
                logger.warning(f"Invalid start date format: {start_date}")
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                card_data = response.json()
                card_id = card_data.get("id")
                
                # Add labels if provided
                if labels and card_id:
                    self._add_labels_to_card(card_id, labels)
                
                logger.info(f"Created timeline card: {card_name}")
                return card_id
            else:
                logger.error(f"Failed to create timeline card: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating timeline card: {e}")
            return None
    
    def create_board(self, board_name: str) -> Optional[str]:
        """Create a new Trello board"""
        url = f"{self.base_url}/boards/"
        params = {
            "name": board_name,
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            response = requests.post(url, params=params)
            if response.status_code == 200:
                board_data = response.json()
                return board_data.get("id")
            else:
                logger.error(f"Failed to create board: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating board: {e}")
            return None
    
    def create_list(self, board_id: str, list_name: str) -> Optional[str]:
        """Create a new list on a board"""
        url = f"{self.base_url}/lists"
        params = {
            "name": list_name,
            "idBoard": board_id,
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            response = requests.post(url, params=params)
            if response.status_code == 200:
                list_data = response.json()
                return list_data.get("id")
            else:
                logger.error(f"Failed to create list: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating list: {e}")
            return None
    
    def get_lists_on_board(self, board_id: str) -> Optional[list]:
        """Get all lists on a board"""
        url = f"{self.base_url}/boards/{board_id}/lists"
        params = {
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get lists: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting lists: {e}")
            return None
    
    def archive_list(self, list_id: str) -> bool:
        """Archive a list"""
        url = f"{self.base_url}/lists/{list_id}/closed"
        params = {
            "value": "true",
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            response = requests.put(url, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error archiving list: {e}")
            return False
    
    def _add_labels_to_card(self, card_id: str, labels: List[str]):
        """Add labels to a card"""
        # This is a simplified version - in reality you'd need to create/get label IDs
        # For now, we'll add them as comments or in the description
        pass
    
    def _calculate_meeting_date(self, project_start: str, offset_days: int) -> str:
        """Calculate meeting date based on project start and offset"""
        try:
            start_date = datetime.strptime(project_start, '%Y-%m-%d')
            meeting_date = start_date + timedelta(days=offset_days)
            return meeting_date.strftime('%Y-%m-%d')
        except ValueError:
            return project_start


# Example usage
if __name__ == "__main__":
    # Demo with timeline integration
    api_key = os.getenv("API_KEY_TRELLO")
    api_token = os.getenv("API_TOKEN_TRELLO")
    
    if api_key and api_token:
        trello = TrelloTimelineIntegration(api_key, api_token)
        
        # Example timeline data
        demo_timeline = {
            "project_start": "2025-08-15",
            "milestones_timeline": [
                {
                    "title": "Project Setup",
                    "start_date": "2025-08-15",
                    "end_date": "2025-08-29",
                    "duration_days": 14
                },
                {
                    "title": "Development Phase", 
                    "start_date": "2025-08-30",
                    "end_date": "2025-09-26",
                    "duration_days": 28
                }
            ],
            "tasks_timeline": [
                {
                    "title": "Setup Development Environment",
                    "start_date": "2025-08-15",
                    "end_date": "2025-08-16",
                    "assigned_to": "Senior Developer",
                    "priority": "High"
                }
            ],
            "project_summary": {
                "project_end": "2025-09-26",
                "total_duration_days": 42
            }
        }
        
        demo_milestones = [
            {"title": "Project Setup", "description": "Initial setup and planning"},
            {"title": "Development Phase", "description": "Core development work"}
        ]
        
        demo_tasks = [
            {"title": "Setup Development Environment", "description": "Configure development tools"}
        ]
        
        result = trello.create_project_board_with_timeline(
            "Demo E-commerce Project",
            demo_milestones,
            demo_tasks, 
            demo_timeline
        )
        
        print("🔗 Timeline Board Created:")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Trello API credentials not configured")
