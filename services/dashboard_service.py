# services/dashboard_service.py
from config import USE_DUMMY_DATA
from data.dummy_dashboard_provider import DummyDashboardProvider

class DashboardService:
    """Service layer for fetching dashboard data."""
    
    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyDashboardProvider()
        else:
            # TODO (Sifat): Create a RealDashboardProvider that uses your database functions
            # self.provider = RealDashboardProvider()
            
            # Temporary fallback
            print("WARNING: Real database dashboard not implemented yet. Falling back to dummy data.")
            self.provider = DummyDashboardProvider()
            
    def get_dashboard_summary(self, user_id):
        """Fetches all dashboard statistics and lists for the user."""
        return self.provider.get_dashboard_summary(user_id)

