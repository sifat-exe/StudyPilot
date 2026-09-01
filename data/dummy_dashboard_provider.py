# data/dummy_dashboard_provider.py

class DummyDashboardProvider:
    """Provides hardcoded dashboard data for testing the UI."""
    
    def get_dashboard_summary(self, user_id):
        # Return dummy data related to this user
        return {
            "today_progress": {
                "completed": 2,
                "total": 4,
                "percentage": 50
            },
            "weekly_stats": {
                "hours": 12.5,
                "sessions": 18,
                "streak": 6
            },
            "schedule": [
                {"time": "6:00 PM - 7:30 PM", "course": "Data Structures", "topic": "Linked List", "status": "Pending"},
                {"time": "7:45 PM - 8:45 PM", "course": "Object Oriented Programming", "topic": "Inheritance", "status": "Pending"}
            ],
            "deadlines": [
                {"title": "Data Structures Assignment", "subtitle": "Assignment \u2022 CSE 210", "due": "2 days", "color": "#e53e3e"},
                {"title": "OOP Class Test 1", "subtitle": "Class Test \u2022 CSE 220", "due": "4 days", "color": "#e53e3e"}
            ],
            "courses": [
                {"name": "Data Structures", "progress": 70, "color": "#3182ce"},
                {"name": "Object Oriented Programming", "progress": 55, "color": "#38a169"},
                {"name": "Discrete Mathematics", "progress": 80, "color": "#805ad5"},
                {"name": "Electrical Machines", "progress": 45, "color": "#dd6b20"}
            ]
        }

