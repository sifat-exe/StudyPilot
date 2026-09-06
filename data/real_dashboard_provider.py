from database.database import get_dashboard_summary


class RealDashboardProvider:

    def get_dashboard_summary(self, user_id):
        return get_dashboard_summary(user_id)