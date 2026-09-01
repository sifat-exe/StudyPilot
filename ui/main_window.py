from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtWidgets import QMainWindow, QLabel
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard

class MainWindow(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Student", "user_id": None}
        
        self.setWindowTitle("StudyPilot")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.setStyleSheet("background-color: #f5f7fa;")

        welcome_label = QLabel(
            f"Welcome, {self.user_info['name']}!"
        )

        self.setCentralWidget(welcome_label)

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
        
        # Dashboard
        self.dashboard = Dashboard(self.user_info)
        self.dashboard.logout_action.triggered.connect(self.handle_logout)
        self.content_area.addWidget(self.dashboard)
        
    def toggle_sidebar(self):
        self.sidebar.toggle()

    def handle_logout(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

