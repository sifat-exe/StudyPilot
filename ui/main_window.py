from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.routine_page import RoutinePage
from ui.assignment_page import AssignmentPage
from ui.class_test_page import ClassTestPage
from ui.profile_page import ProfilePage
from ui.study_materials_page import StudyMaterialsPage

class MainWindow(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Student", "user_id": None}
        
        self.setWindowTitle("StudyPilot")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.setStyleSheet("background-color: #f5f7fa;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self.user_info)
        self.sidebar.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar.logout_btn.clicked.connect(self.handle_logout)
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area, 1)
        
        # Pages
        self.dashboard = Dashboard(self.user_info)
        self.dashboard.logout_action.triggered.connect(self.handle_logout)
        self.routine_page = RoutinePage(self.user_info)
        self.study_materials_page = StudyMaterialsPage(self.user_info)
        self.assignment_page = AssignmentPage(self.user_info)
        self.class_test_page = ClassTestPage(self.user_info)
        self.profile_page = ProfilePage(self.user_info)
        self.profile_page.profile_saved.connect(self.handle_profile_saved)
        
        self.content_area.addWidget(self.dashboard)
        self.content_area.addWidget(self.routine_page)
        self.content_area.addWidget(self.study_materials_page)
        self.content_area.addWidget(self.assignment_page)
        self.content_area.addWidget(self.class_test_page)
        self.content_area.addWidget(self.profile_page)

        # Connect sidebar buttons
        for btn in self.sidebar.buttons:
            btn.clicked.connect(self.handle_navigation)
        
    def handle_navigation(self):
        sender = self.sender()
        text = sender.text()
        if sender in self.sidebar.buttons:
            index = self.sidebar.buttons.index(sender)
            text = self.sidebar.nav_items[index][0]
        
        # Ensure only the active button is highlighted (blue) and others are dimmed
        for btn in self.sidebar.buttons:
            btn.setChecked(btn == sender)
        
        if text == "Dashboard":
            self.content_area.setCurrentWidget(self.dashboard)
        elif text == "Class Routine":
            self.routine_page.load_data()
            self.content_area.setCurrentWidget(self.routine_page)
        elif text == "Study Materials":
            self.study_materials_page.load_data()
            self.content_area.setCurrentWidget(self.study_materials_page)
        elif text == "Assignments":
            self.assignment_page.load_data()
            self.content_area.setCurrentWidget(self.assignment_page)
        elif text == "Class Tests":
            self.class_test_page.load_data()
            self.content_area.setCurrentWidget(self.class_test_page)
        elif text == "Profile":
            self.profile_page.load_data()
            self.content_area.setCurrentWidget(self.profile_page)

    def handle_profile_saved(self, profile):
        if profile.get("name"):
            self.user_info["name"] = profile["name"]
            self.sidebar.update_user_display(self.user_info)

    def toggle_sidebar(self):
        self.sidebar.toggle()

    def handle_logout(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
