from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.routine_page import RoutinePage
from ui.assignment_page import AssignmentPage
from ui.class_test_page import ClassTestPage

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
        self.assignment_page = AssignmentPage(self.user_info)
        self.class_test_page = ClassTestPage(self.user_info)
        
        self.content_area.addWidget(self.dashboard)
        self.content_area.addWidget(self.routine_page)
        self.content_area.addWidget(self.assignment_page)
        self.content_area.addWidget(self.class_test_page)

        # Connect sidebar buttons
        for btn in self.sidebar.buttons:
            btn.clicked.connect(self.handle_navigation)
        
    def handle_navigation(self):
        sender = self.sender()
        text = sender.text()
        
        # Ensure only the active button is highlighted (blue) and others are dimmed
        for btn in self.sidebar.buttons:
            btn.setChecked(btn == sender)
        
        if "Dashboard" in text:
            self.content_area.setCurrentWidget(self.dashboard)
        elif "Class Routine" in text:
            self.routine_page.load_data()
            self.content_area.setCurrentWidget(self.routine_page)
        elif "Assignments" in text:
            self.assignment_page.load_data()
            self.content_area.setCurrentWidget(self.assignment_page)
        elif "Class Tests" in text:
            self.class_test_page.load_data()
            self.content_area.setCurrentWidget(self.class_test_page)

    def toggle_sidebar(self):
        self.sidebar.toggle()

    def handle_logout(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
