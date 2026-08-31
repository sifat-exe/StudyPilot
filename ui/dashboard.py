from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QScrollArea, QProgressBar, QGridLayout,
                               QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor

class Dashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Student", "user_id": None}
        
        # Fetch data via Service
        from services.dashboard_service import DashboardService
        service = DashboardService()
        data = service.get_dashboard_summary(self.user_info["user_id"])
        
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
        user_menu.setStyleSheet("color: #4a5568; font-weight: bold; border: none;")
        
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(user_menu)
        
        main_layout.addWidget(top_bar)
        
        # Scroll Area for Dashboard Content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f8fafc; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f8fafc;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 30, 40, 40)
        content_layout.setSpacing(25)
        
        # Greeting
        greeting_label = QLabel(f"Good Morning, {self.user_info['name'].split()[0]}! 👋")
        greeting_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        greeting_label.setStyleSheet("color: #1a202c;")
        
        subtitle_label = QLabel("Here's your academic overview for today.")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: #718096;")
        
        content_layout.addWidget(greeting_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addSpacing(10)
        
        # Top Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # A. Today's Study Progress
        progress_card = self.create_card()
        prog_layout = QVBoxLayout(progress_card)
        
        icon_title = QHBoxLayout()
        icon_lbl = QLabel("✅")
        prog_title = QLabel("Today's Progress")
        prog_title.setStyleSheet("color: #718096; font-weight: bold;")
        icon_title.addWidget(icon_lbl)
        icon_title.addWidget(prog_title)
        icon_title.addStretch()
        
        prog_value = QLabel(f"{data['today_progress']['completed']} / {data['today_progress']['total']} Sessions Completed")
        prog_value.setFont(QFont("Segoe UI", 16, QFont.Bold))
        
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
        
        # E. Weekly Study Statistics
        stats_card1 = self.create_card()
        s1_layout = QVBoxLayout(stats_card1)
        s1_title = QLabel("⏱ Study Hours This Week")
        s1_title.setStyleSheet("color: #718096; font-weight: bold;")
        s1_value = QLabel(f"{data['weekly_stats']['hours']} hrs")
        s1_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        s1_layout.addWidget(s1_title)
        s1_layout.addWidget(s1_value)
        s1_layout.addStretch()
        stats_layout.addWidget(stats_card1)
        
        stats_card2 = self.create_card()
        s2_layout = QVBoxLayout(stats_card2)
        s2_title = QLabel("📚 Completed Sessions")
        s2_title.setStyleSheet("color: #718096; font-weight: bold;")
        s2_value = QLabel(str(data['weekly_stats']['sessions']))
        s2_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        s2_layout.addWidget(s2_title)
        s2_layout.addWidget(s2_value)
        s2_layout.addStretch()
        stats_layout.addWidget(stats_card2)
        
        stats_card3 = self.create_card()
        s3_layout = QVBoxLayout(stats_card3)
        s3_title = QLabel("🔥 Current Streak")
        s3_title.setStyleSheet("color: #718096; font-weight: bold;")
        s3_value = QLabel(f"{data['weekly_stats']['streak']} days")
        s3_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        s3_value.setStyleSheet("color: #dd6b20;")
        s3_layout.addWidget(s3_title)
        s3_layout.addWidget(s3_value)
        s3_layout.addStretch()
        stats_layout.addWidget(stats_card3)
        
        content_layout.addLayout(stats_layout)
        
        # Middle Row (Schedule & Deadlines)
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(20)
        
        # B. Today's Schedule
        schedule_card = self.create_card()
        sched_layout = QVBoxLayout(schedule_card)
        
        sched_head = QHBoxLayout()
        sched_title = QLabel("Today's Study Schedule")
        sched_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        view_plan = QPushButton("View Planner →")
        view_plan.setFlat(True)
        view_plan.setStyleSheet("color: #3182ce; font-weight: bold;")
        view_plan.setCursor(QCursor(Qt.PointingHandCursor))
        
        sched_head.addWidget(sched_title)
        sched_head.addStretch()
        sched_head.addWidget(view_plan)
        sched_layout.addLayout(sched_head)
        sched_layout.addSpacing(15)
        
        for session in data['schedule']:
            item = QFrame()
            item.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(15, 15, 15, 15)
            
            dot = QLabel("🔵")
            time_lbl = QLabel(session['time'])
            time_lbl.setFixedWidth(120)
            time_lbl.setStyleSheet("color: #4a5568; font-weight: bold;")
            
            course_topic = QVBoxLayout()
            c_lbl = QLabel(session['course'])
            c_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
            top_lbl = QLabel(session['topic'])
            top_lbl.setStyleSheet("color: #718096;")
            course_topic.addWidget(c_lbl)
            course_topic.addWidget(top_lbl)
            
            status_lbl = QLabel(session['status'])
            status_lbl.setStyleSheet("background-color: #feebc8; color: #dd6b20; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;")
            
            item_layout.addWidget(dot)
            item_layout.addWidget(time_lbl)
            item_layout.addLayout(course_topic)
            item_layout.addStretch()
            item_layout.addWidget(status_lbl)
            
            sched_layout.addWidget(item)
            
        sched_layout.addStretch()
        mid_layout.addWidget(schedule_card, 2)
        
        # C. Upcoming Deadlines
        deadlines_card = self.create_card()
        dead_layout = QVBoxLayout(deadlines_card)
        
        dead_head = QHBoxLayout()
        dead_title = QLabel("Upcoming Deadlines")
        dead_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        view_all = QPushButton("View All →")
        view_all.setFlat(True)
        view_all.setStyleSheet("color: #3182ce; font-weight: bold;")
        view_all.setCursor(QCursor(Qt.PointingHandCursor))
        
        dead_head.addWidget(dead_title)
        dead_head.addStretch()
        dead_head.addWidget(view_all)
        dead_layout.addLayout(dead_head)
        dead_layout.addSpacing(15)
        
        for deadline in data['deadlines']:
            item = QFrame()
            item.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(15, 15, 15, 15)
            
            icon = QLabel("📄")
            icon.setFont(QFont("Segoe UI", 16))
            
            info = QVBoxLayout()
            t_lbl = QLabel(deadline['title'])
            t_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            sub_lbl = QLabel(deadline['subtitle'])
            sub_lbl.setStyleSheet("color: #718096; font-size: 11px;")
            info.addWidget(t_lbl)
            info.addWidget(sub_lbl)
            
            d_lbl = QLabel(deadline['due'])
            d_lbl.setStyleSheet(f"color: {deadline['color']}; font-weight: bold;")
            
            item_layout.addWidget(icon)
            item_layout.addLayout(info)
            item_layout.addStretch()
            item_layout.addWidget(d_lbl)
            
            dead_layout.addWidget(item)
            
        dead_layout.addStretch()
        mid_layout.addWidget(deadlines_card, 1)
        
        content_layout.addLayout(mid_layout)
        
        # D. Course Progress
        courses_card = self.create_card()
        course_layout = QVBoxLayout(courses_card)
        
        course_head = QHBoxLayout()
        course_title = QLabel("Course Progress")
        course_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        view_courses = QPushButton("View Courses →")
        view_courses.setFlat(True)
        view_courses.setStyleSheet("color: #3182ce; font-weight: bold;")
        view_courses.setCursor(QCursor(Qt.PointingHandCursor))
        course_head.addWidget(course_title)
        course_head.addStretch()
        course_head.addWidget(view_courses)
        
        course_layout.addLayout(course_head)
        course_layout.addSpacing(15)
        
        courses = [
            ("Data Structures", 70, "#3182ce"),
            ("Object Oriented Programming", 55, "#38a169"),
            ("Discrete Mathematics", 80, "#805ad5"),
            ("Electrical Machines", 45, "#dd6b20")
        ]
        
        c_grid = QGridLayout()
        c_grid.setSpacing(20)
        
        for i, (name, prog, color) in enumerate(courses):
            row = i // 2
            col = i % 2
            
            item = QWidget()
            item_lay = QVBoxLayout(item)
            item_lay.setContentsMargins(0, 0, 0, 0)
            
            top_lay = QHBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            
            p_lbl = QLabel(f"{prog}%")
            p_lbl.setStyleSheet("color: #718096; font-weight: bold;")
            
            top_lay.addWidget(n_lbl)
            top_lay.addStretch()
            top_lay.addWidget(p_lbl)
            
            p_bar = QProgressBar()
            p_bar.setValue(prog)
            p_bar.setTextVisible(False)
            p_bar.setFixedHeight(8)
            p_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background-color: #e2e8f0;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)
            
            item_lay.addLayout(top_lay)
            item_lay.addWidget(p_bar)
            
            c_grid.addWidget(item, row, col)
            
        course_layout.addLayout(c_grid)
        content_layout.addWidget(courses_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
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

