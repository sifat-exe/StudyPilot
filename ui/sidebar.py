from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QFrame, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor

class Sidebar(QFrame):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Student"}
        self.is_expanded = True
        
        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                color: white;
            }
            QLabel {
                background-color: transparent;
                color: white;
            }
            QPushButton {
                background-color: transparent;
                text-align: left;
                padding: 12px 15px;
                border: none;
                border-radius: 8px;
                color: #cbd5e0;
                font-size: 14px;
                font-family: "Segoe UI";
            }
            QPushButton:hover {
                background-color: #334155;
                color: white;
            }
            QPushButton:checked {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 20, 15, 20)
        self.layout.setSpacing(8)
        
        # Header (Hamburger + Logo)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 20px;
                text-align: center;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        
        self.logo_label = QLabel("🚀 StudyPilot")
        self.logo_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.logo_label.setStyleSheet("color: white; background-color: transparent;")
        
        self.header_layout.addWidget(self.toggle_btn)
        self.header_layout.addWidget(self.logo_label)
        self.header_layout.addStretch()
        
        self.layout.addLayout(self.header_layout)
        self.layout.addSpacing(25)
        
        # Navigation Items
        self.nav_items = [
            ("Dashboard", "📊"),
            ("Class Routine", "📅"),
            ("Study Materials", "📚"),
            ("Assignments", "📝"),
            ("Class Tests", "📋"),
            ("Study Planner", "🎯"),
            ("Progress", "📈"),
            ("Notifications", "🔔")
        ]
        
        self.buttons = []
        for text, icon in self.nav_items:
            btn = QPushButton(f"{icon}   {text}")
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.layout.addWidget(btn)
            self.buttons.append(btn)
            
            if text == "Dashboard":
                btn.setChecked(True)
                
        self.layout.addStretch()
        
        # User profile area at bottom
        self.profile_frame = QFrame()
        self.profile_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-radius: 8px;
            }
        """)
        profile_layout = QHBoxLayout(self.profile_frame)
        profile_layout.setContentsMargins(10, 10, 10, 10)
        
        # Use first letter of name for avatar
        initial = self.user_info["name"][0].upper() if self.user_info["name"] else "U"
        avatar = QLabel(initial)
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 16px; font-weight: bold;")
        
        name_role = QVBoxLayout()
        name_lbl = QLabel(self.user_info["name"])
        name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        role_lbl = QLabel("Student")
        role_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        name_role.addWidget(name_lbl)
        name_role.addWidget(role_lbl)
        name_role.setSpacing(0)
        
        logout_btn = QPushButton("🚪")
        logout_btn.setFixedSize(32, 32)
        logout_btn.setStyleSheet("background: transparent; color: #94a3b8;")
        
        profile_layout.addWidget(avatar)
        profile_layout.addLayout(name_role)
        profile_layout.addWidget(logout_btn)
        
        self.layout.addWidget(self.profile_frame)
        
        self.setFixedWidth(260)
        
    def toggle(self):
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.setFixedWidth(260)
            self.logo_label.show()
            for btn, (text, icon) in zip(self.buttons, self.nav_items):
                btn.setText(f"{icon}   {text}")
            self.profile_frame.show()
        else:
            self.setFixedWidth(70)
            self.logo_label.hide()
            for btn, (text, icon) in zip(self.buttons, self.nav_items):
                btn.setText(f"{icon}")
                btn.setToolTip(text)
            self.profile_frame.hide()

