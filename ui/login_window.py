from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QCheckBox, QFrame, 
                               QSizePolicy, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QCursor

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyPilot - Login")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #f0f4f8;")
        self.setMinimumSize(900, 650)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Panel (Branding)
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #1a2a44; color: white;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 50, 50, 50)
        
        # Logo and title area
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("🚀") # Placeholder for logo
        logo_icon.setFont(QFont("Segoe UI", 32))
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        logo_label = QLabel("StudyPilot")
        logo_font = QFont("Segoe UI", 24, QFont.Bold)
        logo_label.setFont(logo_font)
        
        tagline_label = QLabel("Plan Smarter. Study Better.")
        tagline_label.setFont(QFont("Segoe UI", 12))
        tagline_label.setStyleSheet("color: #a0aec0;")
        
        title_layout.addWidget(logo_label)
        title_layout.addWidget(tagline_label)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addLayout(title_layout)
        logo_layout.addStretch()
        
        left_layout.addLayout(logo_layout)
        left_layout.addStretch()
        
        # Graphic placeholder / decorative element
        graphic_label = QLabel("📋Your Study Journey\n     Starts Here ✓")
        graphic_label.setFont(QFont("Segoe UI", 19, QFont.Bold))
        graphic_label.setStyleSheet("color: #8fb1e9; background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;")
        graphic_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(graphic_label)
        left_layout.addStretch()
        
        quote_label = QLabel("\"A better you, a brighter tomorrow.\"")
        quote_label.setFont(QFont("Segoe UI", 16, italic=True))
        quote_label.setStyleSheet("color: #a0aec0;")
        left_layout.addWidget(quote_label)
        
        # Right Panel (Login Form)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #ffffff;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 40, 60, 40)
        
        # Login Card
        login_card = QFrame()
        login_card.setStyleSheet("""
            QFrame#LoginCard {
                background-color: white;
                border-radius: 15px;
            }
        """)
        login_card.setObjectName("LoginCard")
        
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        welcome_label = QLabel("Welcome Back")
        welcome_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #2d3748;")
        
        subtitle_label = QLabel("Login to continue to StudyPilot")
        subtitle_label.setFont(QFont("Segoe UI", 11))
        subtitle_label.setStyleSheet("color: #718096;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Inputs
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setMinimumHeight(45)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #cbd5e0;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                color: #2d3748;
            }
            QLineEdit:focus {
                border: 2px solid #3182ce;
            }
        """)
        
        # Password field with show/hide button
        pass_layout = QHBoxLayout()
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                            padding: 10px 15px;
                            border: 1px solid #cbd5e0;
                            border-top-left-radius: 8px;
                            border-bottom-left-radius: 8px;
                            border-top-right-radius: 0px;
                            border-bottom-right-radius: 0px;
                            background-color: white;
                            font-size: 14px;
                            color: #2d3748;
                            border-right: none;
                        }
                        QLineEdit:focus {
                            border: 2px solid #3182ce;
 
                        }
        """)
        
        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setMinimumHeight(45)
        self.show_pass_btn.setFixedWidth(40)
        self.show_pass_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_pass_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #cbd5e0;
                border-left: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: white;
                color: #718096;
            }
            QPushButton:hover {
                color: #2d3748;
            }
        """)
        self.show_pass_btn.clicked.connect(self.toggle_password_visibility)
        
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.show_pass_btn)
        
        pass_container = QWidget()
        pass_container.setLayout(pass_layout)
        
        # Options: Remember me & Forgot Password
        options_layout = QHBoxLayout()
        remember_cb = QCheckBox("Remember me")
        remember_cb.setFont(QFont("Segoe UI", 10))
        remember_cb.setStyleSheet("""
            QCheckBox { color: #000000; }
            QCheckBox::indicator { width: 15px; height: 15px;}
        """)
        
        forgot_btn = QPushButton("Forgot password?")
        forgot_btn.setFlat(True)
        forgot_btn.setCursor(QCursor(Qt.PointingHandCursor))
        forgot_btn.setFont(QFont("Segoe UI", 10))
        forgot_btn.setStyleSheet("color: #3182ce; text-align: right; border: none;")
        
        options_layout.addWidget(remember_cb)
        options_layout.addStretch()
        options_layout.addWidget(forgot_btn)

    # have to implement forget_btn button's work here like forgot_btn.clicked.connect(...)
        
        # Login Button
        self.login_btn = QPushButton("Login")
        self.login_btn.setDefault(True)
        self.login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b6cb0;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2c5282;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Divider
        divider_layout = QHBoxLayout()
        line1 = QFrame(); line1.setFrameShape(QFrame.HLine); line1.setStyleSheet("color: #e2e8f0;")
        line2 = QFrame(); line2.setFrameShape(QFrame.HLine); line2.setStyleSheet("color: #e2e8f0;")
        or_label = QLabel("OR")
        or_label.setAlignment(Qt.AlignCenter)
        or_label.setStyleSheet("color: #a0aec0; font-size: 12px;")
        divider_layout.addWidget(line1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line2)
        
        # Register section
        register_layout = QHBoxLayout()
        
        register_btn = QPushButton("Don't have an account?\nRegister")
        register_btn.setFlat(True)
        register_btn.setMinimumHeight(45)
        register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        register_btn.setStyleSheet("""
            QPushButton {
                color: #4a5568;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f7fafc;
            }
        """)
        register_layout.addWidget(register_btn)

        register_btn.clicked.connect(self.open_register_window)
    
        # Add widgets to card
        card_layout.addWidget(welcome_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(pass_container)
        card_layout.addLayout(options_layout)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_btn)
        card_layout.addSpacing(15)
        card_layout.addLayout(divider_layout)
        card_layout.addSpacing(15)
        card_layout.addLayout(register_layout)
        
        # Add drop shadow to card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        login_card.setGraphicsEffect(shadow)
        
        right_layout.addStretch()
        right_layout.addWidget(login_card)
        right_layout.addStretch()
        
        # Adjust panel sizes
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)
        
    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_pass_btn.setText("🚫")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_pass_btn.setText("👁")
            
    def show_message_box(self, icon, title, message):
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QPalette, QColor
        
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)
        
        # Set palette for native Qt dialogs on Windows
        palette = msg.palette()
        palette.setColor(QPalette.Window, QColor("#1e293b"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.Base, QColor("#1e293b"))
        palette.setColor(QPalette.Text, QColor("#ffffff"))
        palette.setColor(QPalette.Button, QColor("#2563eb"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        msg.setPalette(palette)
        
        # Explicit stylesheet for child controls
        msg.setStyleSheet("""
            QMessageBox, QDialog, QWidget {
                background-color: #1e293b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        msg.exec()

    def handle_login(self):
        from services.auth_service import AuthService
        from PySide6.QtWidgets import QMessageBox
        
        email_or_username = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email_or_username or not password:
            self.show_message_box(QMessageBox.Warning, "Login Error", "Please enter both email/username and password.")
            return
            
        try:
            auth_service = AuthService()
            user_info = auth_service.login(email_or_username, password)
            
            if user_info:
                from ui.main_window import MainWindow
                self.main_window = MainWindow(user_info)
                self.main_window.show()
                self.close()
            else:
                self.show_message_box(QMessageBox.Critical, "Login Failed", "Invalid credentials. Please try again.")
        except Exception as e:
            self.show_message_box(QMessageBox.Critical, "System Error", f"An error occurred during login: {str(e)}")

    def open_register_window(self):
        from ui.register_window import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()
