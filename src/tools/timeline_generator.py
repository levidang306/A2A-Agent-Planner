"""
📅 Timeline Generator Tool for A2A System
=========================================
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

class TimelineGenerator:
    def __init__(self):
        self.business_days_only = True
        self.daily_work_hours = 8
        self.team_velocity_factor = 0.8  # Account for meetings, interruptions
    
    def generate_project_timeline(self, milestones: List[Dict], tasks: List[Dict], team_members: List[Dict], start_date: str = None) -> Dict[str, Any]:
        """Generate a detailed project timeline with dates and assignments"""
        
        if start_date:
            project_start = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            project_start = datetime.now() + timedelta(days=1)  # Start tomorrow
        
        timeline = {
            "project_start": project_start.strftime('%Y-%m-%d'),
            "generated_at": datetime.now().isoformat(),
            "milestones_timeline": [],
            "tasks_timeline": [],
            "team_assignments": [],
            "critical_path": [],
            "project_summary": {}
        }
        
        # Process milestones
        current_date = project_start
        for i, milestone in enumerate(milestones):
            duration_weeks = self._parse_duration(milestone.get('duration', '2 weeks'))
            milestone_end = self._add_business_days(current_date, duration_weeks * 5)  # 5 business days per week
            
            milestone_timeline = {
                "id": f"milestone_{i+1}",
                "title": milestone.get('title', f'Milestone {i+1}'),
                "description": milestone.get('description', ''),
                "start_date": current_date.strftime('%Y-%m-%d'),
                "end_date": milestone_end.strftime('%Y-%m-%d'),
                "duration_days": duration_weeks * 5,
                "dependencies": milestone.get('dependencies', []),
                "status": "planned"
            }
            
            timeline["milestones_timeline"].append(milestone_timeline)
            current_date = milestone_end + timedelta(days=1)
        
        # Process tasks with team assignments
        task_start_date = project_start
        team_workload = {member['name']: 0 for member in team_members}
        
        for i, task in enumerate(tasks):
            # Calculate task duration
            time_estimate = task.get('time_estimate', '8 hours')
            task_hours = self._parse_time_estimate(time_estimate)
            task_days = max(1, int((task_hours / self.daily_work_hours) / self.team_velocity_factor))
            
            # Assign to team member with least workload
            assigned_member = min(team_workload.items(), key=lambda x: x[1])
            team_workload[assigned_member[0]] += task_days
            
            task_end_date = self._add_business_days(task_start_date, task_days)
            
            task_timeline = {
                "id": f"task_{i+1}",
                "title": task.get('title', f'Task {i+1}'),
                "description": task.get('description', ''),
                "start_date": task_start_date.strftime('%Y-%m-%d'),
                "end_date": task_end_date.strftime('%Y-%m-%d'),
                "duration_days": task_days,
                "time_estimate": time_estimate,
                "assigned_to": assigned_member[0],
                "priority": task.get('priority', 'Medium'),
                "dependencies": task.get('dependencies', []),
                "status": "planned"
            }
            
            timeline["tasks_timeline"].append(task_timeline)
            
            # Move start date for next task (with some overlap for parallel work)
            if i < len(tasks) - 1:
                task_start_date = task_start_date + timedelta(days=max(1, task_days // 2))
        
        # Generate team assignments summary
        for member in team_members:
            member_tasks = [task for task in timeline["tasks_timeline"] if task["assigned_to"] == member['name']]
            total_workload = sum(task["duration_days"] for task in member_tasks)
            
            assignment = {
                "name": member['name'],
                "role": member.get('role', 'Team Member'),
                "total_tasks": len(member_tasks),
                "total_workload_days": total_workload,
                "tasks": [{"id": task["id"], "title": task["title"], "duration": task["duration_days"]} for task in member_tasks],
                "utilization": min(100, (total_workload / 30) * 100)  # Assume 30 working days per month
            }
            
            timeline["team_assignments"].append(assignment)
        
        # Calculate project end date
        last_task_end = max([datetime.strptime(task["end_date"], '%Y-%m-%d') for task in timeline["tasks_timeline"]])
        last_milestone_end = max([datetime.strptime(ms["end_date"], '%Y-%m-%d') for ms in timeline["milestones_timeline"]])
        project_end = max(last_task_end, last_milestone_end)
        
        timeline["project_summary"] = {
            "project_end": project_end.strftime('%Y-%m-%d'),
            "total_duration_days": (project_end - project_start).days,
            "total_milestones": len(milestones),
            "total_tasks": len(tasks),
            "team_size": len(team_members),
            "estimated_effort_hours": sum(self._parse_time_estimate(task.get('time_estimate', '8 hours')) for task in tasks)
        }
        
        return timeline
    
    def generate_gantt_chart_data(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data structure for Gantt chart visualization"""
        
        gantt_data = {
            "chart_title": "Project Timeline - Gantt Chart",
            "start_date": timeline["project_start"],
            "end_date": timeline["project_summary"]["project_end"],
            "tasks": [],
            "milestones": [],
            "dependencies": []
        }
        
        # Add milestones to Gantt
        for milestone in timeline["milestones_timeline"]:
            gantt_data["milestones"].append({
                "id": milestone["id"],
                "name": milestone["title"],
                "start": milestone["start_date"],
                "end": milestone["end_date"],
                "type": "milestone",
                "color": "#FF6B6B"
            })
        
        # Add tasks to Gantt
        for task in timeline["tasks_timeline"]:
            gantt_data["tasks"].append({
                "id": task["id"],
                "name": task["title"],
                "start": task["start_date"],
                "end": task["end_date"],
                "assigned_to": task["assigned_to"],
                "priority": task["priority"],
                "type": "task",
                "color": self._get_priority_color(task["priority"])
            })
        
        return gantt_data
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string like '2 weeks', '3 months' to weeks"""
        duration_str = duration_str.lower()
        
        if 'week' in duration_str:
            return int(''.join(filter(str.isdigit, duration_str)))
        elif 'month' in duration_str:
            return int(''.join(filter(str.isdigit, duration_str))) * 4
        elif 'day' in duration_str:
            return int(''.join(filter(str.isdigit, duration_str))) // 5  # Convert days to weeks
        else:
            return 2  # Default 2 weeks
    
    def _parse_time_estimate(self, time_str: str) -> int:
        """Parse time estimate like '8 hours', '2 days' to hours"""
        time_str = time_str.lower()
        
        if 'hour' in time_str:
            return int(''.join(filter(str.isdigit, time_str)))
        elif 'day' in time_str:
            return int(''.join(filter(str.isdigit, time_str))) * self.daily_work_hours
        elif 'week' in time_str:
            return int(''.join(filter(str.isdigit, time_str))) * 5 * self.daily_work_hours
        else:
            return 8  # Default 8 hours
    
    def _add_business_days(self, start_date: datetime, business_days: int) -> datetime:
        """Add business days to a date (skipping weekends)"""
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                days_added += 1
        
        return current_date
    
    def _get_priority_color(self, priority: str) -> str:
        """Get color for task priority"""
        colors = {
            "high": "#FF4757",
            "medium": "#FFA502", 
            "low": "#2ED573"
        }
        return colors.get(priority.lower(), "#3498DB")

# Calendar integration helper
class CalendarIntegration:
    def __init__(self):
        self.demo_mode = True  # Switch to False when implementing real calendar APIs
    
    def create_calendar_events(self, timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create calendar events from timeline"""
        events = []
        
        # Create milestone events
        for milestone in timeline["milestones_timeline"]:
            event = {
                "id": f"cal_event_{milestone['id']}",
                "title": f"🎯 Milestone: {milestone['title']}",
                "start_date": milestone['start_date'],
                "end_date": milestone['end_date'],
                "description": milestone['description'],
                "type": "milestone",
                "all_day": True,
                "calendar": "A2A Project Milestones"
            }
            events.append(event)
        
        # Create task deadline events
        for task in timeline["tasks_timeline"]:
            event = {
                "id": f"cal_event_{task['id']}",
                "title": f"📝 Task Due: {task['title']}",
                "start_date": task['end_date'],
                "end_date": task['end_date'],
                "description": f"Assigned to: {task['assigned_to']}\\n{task['description']}",
                "type": "task_deadline",
                "all_day": False,
                "attendees": [task['assigned_to']],
                "calendar": "A2A Project Tasks"
            }
            events.append(event)
        
        return events

# Example usage
if __name__ == "__main__":
    # Demo data
    demo_milestones = [
        {
            "title": "Project Setup & Planning",
            "description": "Initial project setup and requirements gathering",
            "duration": "2 weeks"
        },
        {
            "title": "Development Phase 1",
            "description": "Core backend development",
            "duration": "4 weeks"
        },
        {
            "title": "Development Phase 2", 
            "description": "Frontend and integration",
            "duration": "3 weeks"
        }
    ]
    
    demo_tasks = [
        {
            "title": "Setup Development Environment",
            "description": "Configure tools and repositories",
            "time_estimate": "8 hours",
            "priority": "High"
        },
        {
            "title": "Database Design",
            "description": "Design schema and relationships",
            "time_estimate": "16 hours",
            "priority": "High"
        },
        {
            "title": "API Development",
            "description": "Build REST API endpoints",
            "time_estimate": "3 days",
            "priority": "Medium"
        }
    ]
    
    demo_team = [
        {"name": "Alice Johnson", "role": "Backend Developer"},
        {"name": "Bob Smith", "role": "Frontend Developer"},
        {"name": "Carol Davis", "role": "UI/UX Designer"}
    ]
    
    # Generate timeline
    timeline_gen = TimelineGenerator()
    timeline = timeline_gen.generate_project_timeline(demo_milestones, demo_tasks, demo_team)
    
    print("📅 Generated Project Timeline:")
    print(json.dumps(timeline, indent=2, default=str))
