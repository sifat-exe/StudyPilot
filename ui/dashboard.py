from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QProgressBar, QPushButton, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor
from services.dashboard_service import DashboardService


class Dashboard(QWidget):
    navigate_to_planner = Signal()

    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Student", "user_id": None}
        self.init_ui()
        self.load_data()


    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: white; border-bottom: 1px solid #e2e8f0;")
        top_bar.setFixedHeight(65)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel("Dashboard")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748;")

        user_menu = QPushButton(f"👤 {self.user_info['name']} ▼")
        user_menu.setFlat(True)
        user_menu.setCursor(QCursor(Qt.PointingHandCursor))
        user_menu.setStyleSheet("""
            QPushButton {
                color: #4a5568; 
                font-weight: bold; 
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #edf2f7;
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)

        self.user_dropdown = QMenu(self)
        self.user_dropdown.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #cbd5e0;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                color: #2d3748;
            }
            QMenu::item:selected {
                background-color: #edf2f7;
                color: #2b6cb0;
            }
        """)
        self.logout_action = self.user_dropdown.addAction("🚪  Logout")
        user_menu.setMenu(self.user_dropdown)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(user_menu)
        main_layout.addWidget(top_bar)

        # Scroll Area for Dashboard Content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f8fafc; }")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #f8fafc;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 30, 40, 40)
        self.content_layout.setSpacing(25)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

    def load_data(self):
        """Fetches latest DB data and rebuilds the Dashboard widgets dynamically."""
        # Clear existing widgets from content layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear sub-layout items
                sub = item.layout()
                while sub.count():
                    sub_item = sub.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()

        service = DashboardService()
        data = service.get_dashboard_summary(self.user_info.get("user_id"))

        # 1. Greeting Header
        first_name = self.user_info.get("name", "Student").split()[0]
        greeting_label = QLabel(f"Good Morning, {first_name}!")
        greeting_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        greeting_label.setStyleSheet("color: #1a202c;")

        subtitle_label = QLabel("Here's your academic overview for today.")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: #718096;")

        self.content_layout.addWidget(greeting_label)
        self.content_layout.addWidget(subtitle_label)
        self.content_layout.addSpacing(10)

        # 2. Top Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # A. Today's Progress
        progress_card = self.create_card()
        prog_layout = QVBoxLayout(progress_card)

        icon_title = QHBoxLayout()
        icon_lbl = QLabel("✅")
        prog_title = QLabel("Progress")
        prog_title.setStyleSheet("color: #718096; font-weight: bold;")
        icon_title.addWidget(icon_lbl)
        icon_title.addWidget(prog_title)
        icon_title.addStretch()

        prog_val_text = f"{data['today_progress']['completed']} / {data['today_progress']['total']} Sessions Completed"
        prog_value = QLabel(prog_val_text)
        prog_value.setFont(QFont("Segoe UI", 14, QFont.Bold))
        prog_value.setStyleSheet("color: #1a202c; background-color: transparent;")

        prog_bar = QProgressBar()
        prog_bar.setValue(data['today_progress']['percentage'])
        prog_bar.setTextVisible(False)
        prog_bar.setFixedHeight(8)
        prog_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e2e8f0;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3182ce;
                border-radius: 4px;
            }
        """)

        prog_layout.addLayout(icon_title)
        prog_layout.addSpacing(5)
        prog_layout.addWidget(prog_value)
        prog_layout.addSpacing(10)
        prog_layout.addWidget(prog_bar)
        stats_layout.addWidget(progress_card)

        # B. Weekly Study Hours
        stats_card1 = self.create_card()
        s1_layout = QVBoxLayout(stats_card1)
        s1_title = QLabel("⏱ Study Hours This Week")
        s1_title.setStyleSheet("color: #718096; font-weight: bold;")
        s1_value = QLabel(f"{data['weekly_stats']['hours']} hrs")
        s1_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        s1_value.setStyleSheet("color: #1a202c; background-color: transparent;")
        s1_layout.addWidget(s1_title)
        s1_layout.addWidget(s1_value)
        s1_layout.addStretch()
        stats_layout.addWidget(stats_card1)

        # C. Completed Sessions
        stats_card2 = self.create_card()
        s2_layout = QVBoxLayout(stats_card2)
        s2_title = QLabel("📚 Completed Sessions")
        s2_title.setStyleSheet("color: #718096; font-weight: bold;")
        s2_value = QLabel(str(data['weekly_stats']['sessions']))
        s2_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        s2_value.setStyleSheet("color: #1a202c; background-color: transparent;")
        s2_layout.addWidget(s2_title)
        s2_layout.addWidget(s2_value)
        s2_layout.addStretch()
        stats_layout.addWidget(stats_card2)


        self.content_layout.addLayout(stats_layout)


        # 3. Middle Row (Schedule & Deadlines)
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(20)

        # B. Planner Card
        schedule_card = self.create_card()
        sched_layout = QVBoxLayout(schedule_card)

        sched_head = QHBoxLayout()
        sched_title = QLabel("Schedule")
        sched_title.setStyleSheet("color: #718096; font-weight: bold;")
        sched_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        view_plan = QPushButton("View Planner →")
        view_plan.setFlat(True)
        view_plan.setStyleSheet("color: #3182ce; font-weight: bold;")
        view_plan.setCursor(QCursor(Qt.PointingHandCursor))
        view_plan.clicked.connect(self.navigate_to_planner.emit)

        sched_head.addWidget(sched_title)
        sched_head.addStretch()
        sched_head.addWidget(view_plan)
        sched_layout.addLayout(sched_head)
        sched_layout.addSpacing(15)

        if not data.get('schedule'):
            no_sched_lbl = QLabel("No pending study sessions in planner.")
            no_sched_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 13px; padding: 10px;")
            sched_layout.addWidget(no_sched_lbl)

        else:
            for session in data['schedule']:
                item = QFrame()
                item.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
                item_layout = QVBoxLayout(item)
                item_layout.setContentsMargins(15, 12, 15, 12)
                item_layout.setSpacing(4)

                # Parse session type and course from topic string
                # topic format: "CT Preparation: CSE2101 (DM)" or "Assignment Work: ..."
                topic_str = session.get('topic', '')
                course_str = session.get('course', '')

                if ':' in topic_str:
                    session_type_raw = topic_str.split(':')[0].strip()
                else:
                    session_type_raw = "Study Session"

                # Determine color based on session type
                if "CT" in session_type_raw or "Class Test" in session_type_raw:
                    type_color = "#dd6b20"
                elif "Assignment" in session_type_raw:
                    type_color = "#2563eb"
                else:
                    type_color = "#7c3aed"  # purple for Revision

                # Sub-header: "CT PREPARATION • CSE2101"
                sub_text = f"{session_type_raw} • {course_str}".upper()
                sub_hdr = QLabel(sub_text)
                sub_hdr.setFont(QFont("Segoe UI", 9, QFont.Bold))
                sub_hdr.setStyleSheet(f"color: {type_color}; letter-spacing: 0.5px;")

                # Course label (bold)
                course_lbl = QLabel(course_str)
                course_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
                course_lbl.setStyleSheet("color: #1e293b;")
                course_lbl.setWordWrap(True)

                # Time label
                time_lbl = QLabel(f"📅 {session.get('time', '')}")
                time_lbl.setFont(QFont("Segoe UI", 10))
                time_lbl.setStyleSheet("color: #64748b;")

                item_layout.addWidget(sub_hdr)
                item_layout.addWidget(course_lbl)
                item_layout.addWidget(time_lbl)

                sched_layout.addWidget(item)

        sched_layout.addStretch()
        mid_layout.addWidget(schedule_card, 2)

        # C. CT and Assignments Card
        deadlines_card = self.create_card()
        dead_layout = QVBoxLayout(deadlines_card)

        dead_head = QHBoxLayout()
        dead_title = QLabel("📝CT and Assignments")
        dead_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        dead_title.setStyleSheet("color: #1e293b;")

        dead_head.addWidget(dead_title)
        dead_head.addStretch()
        dead_layout.addLayout(dead_head)
        dead_layout.addSpacing(12)

        if not data.get('deadlines'):
            empty_lbl = QLabel("No upcoming CT or assignments.")
            empty_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 13px; padding: 10px;")
            dead_layout.addWidget(empty_lbl)
        else:
            for deadline in data['deadlines']:
                item = QFrame()
                item.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
                item_layout = QVBoxLayout(item)
                item_layout.setContentsMargins(15, 12, 15, 12)
                item_layout.setSpacing(4)

                item_type = deadline.get("type") or ("Assignment" if "Assignment" in str(deadline.get("subtitle", "")) else "Class Test")
                course_code = deadline.get("course", "")
                sub_text = f"{item_type} • {course_code}" if course_code else item_type

                sub_hdr = QLabel(sub_text.upper())
                sub_hdr.setFont(QFont("Segoe UI", 9, QFont.Bold))
                sub_color = "#2563eb" if "Assignment" in item_type else "#dd6b20"
                sub_hdr.setStyleSheet(f"color: {sub_color}; letter-spacing: 0.5px;")

                topic_text = deadline.get("topic") or deadline.get("title", "")
                topic_lbl = QLabel(topic_text)
                topic_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
                topic_lbl.setStyleSheet("color: #1e293b;")
                topic_lbl.setWordWrap(True)

                date_text = deadline.get("date") or deadline.get("due", "")
                date_lbl = QLabel(f"📅 {date_text}")
                date_lbl.setFont(QFont("Segoe UI", 10))
                date_lbl.setStyleSheet("color: #64748b;")

                item_layout.addWidget(sub_hdr)
                item_layout.addWidget(topic_lbl)
                item_layout.addWidget(date_lbl)

                dead_layout.addWidget(item)

        dead_layout.addStretch()
        mid_layout.addWidget(deadlines_card, 1)

        self.content_layout.addLayout(mid_layout)
        self.content_layout.addStretch()

    def create_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        return card
