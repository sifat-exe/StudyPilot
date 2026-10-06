# services/dashboard_service.py
from config import USE_DUMMY_DATA
from data.dummy_dashboard_provider import DummyDashboardProvider

class DashboardService:
    """Service layer for fetching dashboard data."""
    
    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyDashboardProvider()
        else:
            from data.real_dashboard_provider import RealDashboardProvider
            self.provider = RealDashboardProvider()
            
    def get_dashboard_summary(self, user_id):
        """Fetches all dashboard statistics and lists for the user."""
        return self.provider.get_dashboard_summary(user_id)

