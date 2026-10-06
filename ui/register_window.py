from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFrame,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QCursor
import re


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyPilot - Register")
        self.resize(1000, 750)
        self.setStyleSheet("background-color: #f0f4f8;")
        self.setMinimumSize(900, 700)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Panel (Branding) - same as LoginWindow
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #1a2a44; color: white;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 50, 50, 50)

        # Logo and title area
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("🚀")
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

        # Graphic placeholder
        graphic_label = QLabel("📝 Create Your Account\n      Get Started ✓")
        graphic_label.setFont(QFont("Segoe UI", 19, QFont.Bold))
        graphic_label.setStyleSheet("color: #8fb1e9; background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;")
        graphic_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(graphic_label)
        left_layout.addStretch()

        quote_label = QLabel("\"A better you, a brighter tomorrow.\"")
        quote_label.setFont(QFont("Segoe UI", 16, italic=True))
        quote_label.setStyleSheet("color: #a0aec0;")
        left_layout.addWidget(quote_label)

        # Right Panel (Registration Form)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #ffffff;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 30, 60, 30)

        # Registration Card
        register_card = QFrame()
        register_card.setStyleSheet("""
            QFrame#RegisterCard {
                background-color: white;
                border-radius: 15px;
            }
        """)
        register_card.setObjectName("RegisterCard")

        card_layout = QVBoxLayout(register_card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(15)

        welcome_label = QLabel("Create Account")
        welcome_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #2d3748;")

        subtitle_label = QLabel("Register to start using StudyPilot")
        subtitle_label.setFont(QFont("Segoe UI", 11))
        subtitle_label.setStyleSheet("color: #718096;")
        subtitle_label.setAlignment(Qt.AlignCenter)

        # Input field style (reused from LoginWindow)
        input_style = """
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
        """

        # Full Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.name_input.setMinimumHeight(45)
        self.name_input.setStyleSheet(input_style)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setMinimumHeight(45)
        self.email_input.setStyleSheet(input_style)

        # Password with show/hide
        pass_layout = QHBoxLayout()
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password (min 6 characters)")
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

        # Confirm Password with show/hide
        confirm_pass_layout = QHBoxLayout()
        confirm_pass_layout.setContentsMargins(0, 0, 0, 0)
        confirm_pass_layout.setSpacing(0)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumHeight(45)
        self.confirm_password_input.setStyleSheet("""
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

        self.show_confirm_pass_btn = QPushButton("👁")
        self.show_confirm_pass_btn.setMinimumHeight(45)
        self.show_confirm_pass_btn.setFixedWidth(40)
        self.show_confirm_pass_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.show_confirm_pass_btn.setStyleSheet("""
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

        self.show_confirm_pass_btn.clicked.connect(
            self.toggle_confirm_password_visibility
        )

        confirm_pass_layout.addWidget(self.confirm_password_input)
        confirm_pass_layout.addWidget(self.show_confirm_pass_btn)

        confirm_pass_container = QWidget()
        confirm_pass_container.setLayout(confirm_pass_layout)


        # Register Button
        self.register_btn = QPushButton("Register")
        self.register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_btn.setMinimumHeight(50)
        self.register_btn.setStyleSheet("""
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
        self.register_btn.clicked.connect(self.handle_register)

        # Allow Enter key to submit from any field
        self.name_input.returnPressed.connect(self.handle_register)
        self.email_input.returnPressed.connect(self.handle_register)
        self.password_input.returnPressed.connect(self.handle_register)
        self.confirm_password_input.returnPressed.connect(self.handle_register)

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

        # Back to Login
        back_layout = QHBoxLayout()
        back_btn = QPushButton("Already have an account?\nBack to Login")
        back_btn.setFlat(True)
        back_btn.setMinimumHeight(45)
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
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
        back_btn.clicked.connect(self.go_back_to_login)
        back_layout.addWidget(back_btn)

        # Add widgets to card
        card_layout.addWidget(welcome_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.name_input)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(pass_container)
        card_layout.addWidget(confirm_pass_container)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.register_btn)
        card_layout.addSpacing(10)
        card_layout.addLayout(divider_layout)
        card_layout.addSpacing(10)
        card_layout.addLayout(back_layout)

        # Add drop shadow to card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        register_card.setGraphicsEffect(shadow)

        right_layout.addStretch()
        right_layout.addWidget(register_card)
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

    def toggle_confirm_password_visibility(self):
        if self.confirm_password_input.echoMode() == QLineEdit.Password:
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
            self.show_confirm_pass_btn.setText("🚫")
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            self.show_confirm_pass_btn.setText("👁")
    

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

    def handle_register(self):
        from services.auth_service import AuthService
        from PySide6.QtWidgets import QMessageBox

        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # --- Validation ---
        if not name:
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Please enter your full name.")
            return

        if not email:
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Please enter your email.")
            return

        # Simple email format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Please enter a valid email address.")
            return

        if not password:
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Please enter a password.")
            return

        if len(password) < 6:
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Password must be at least 6 characters long.")
            return

        if not confirm_password:
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Please confirm your password.")
            return

        if password != confirm_password:
            self.show_message_box(QMessageBox.Warning, "Validation Error", "Passwords do not match.")
            return

        # --- Attempt Registration ---
        try:
            auth_service = AuthService()
            result = auth_service.register(name, email, password)

            if result["success"]:
                self.show_message_box(QMessageBox.Information, "Registration Successful",
                                      "Your account has been created!\nYou can now log in.")
                self.go_back_to_login()
            else:
                self.show_message_box(QMessageBox.Warning, "Registration Failed", result["message"])
        except Exception as e:
            self.show_message_box(QMessageBox.Critical, "System Error",
                                  f"An error occurred during registration: {str(e)}")

    def go_back_to_login(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

