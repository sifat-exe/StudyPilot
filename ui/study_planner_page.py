import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor
from services.planner_service import PlannerService
from ui.dialog_helpers import show_dark_message_box


class StudyPlannerPage(QWidget):
    """
    Study Planner UI page adhering to StudyPilot design language.
    Renders top summary metrics, plan configuration controls, and generated session cards.
    """

    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"user_id": None}
        self.service = PlannerService()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ── 1. Page Header ────────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        title = QLabel("📅 Autonomous Study Planner")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # ── 2. Top Summary Banner Card ─────────────────────────────────────────
        self.summary_card = QFrame()
        self.summary_card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1px solid #cbd5e0; }")
        self.summary_layout = QVBoxLayout(self.summary_card)
        self.summary_layout.setContentsMargins(20, 16, 20, 16)
        self.summary_layout.setSpacing(10)
        main_layout.addWidget(self.summary_card)

        # ── 3. Planner Configuration & Setup Bar ──────────────────────────────
        config_card = QFrame()
        config_card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1px solid #cbd5e0; }")
        config_layout = QHBoxLayout(config_card)
        config_layout.setContentsMargins(15, 14, 15, 14)
        config_layout.setSpacing(12)

        # Period Combo
        period_lbl = QLabel("Period:")
        period_lbl.setStyleSheet("color: #475569; font-weight: bold;")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Next 7 days", "Today"])

        # Daily Hours Combo
        hours_lbl = QLabel("Daily Hours:")
        hours_lbl.setStyleSheet("color: #475569; font-weight: bold;")
        self.hours_combo = QComboBox()
        self.hours_combo.addItems(["3 hours/day", "2 hours/day", "4 hours/day", "5 hours/day"])

        # Session Length Combo
        length_lbl = QLabel("Session Length:")
        length_lbl.setStyleSheet("color: #475569; font-weight: bold;")
        self.length_combo = QComboBox()
        self.length_combo.addItems(["60 minutes", "30 minutes", "45 minutes", "90 minutes"])

        # Preferred Time Combo
        time_lbl = QLabel("Preferred Time:")
        time_lbl.setStyleSheet("color: #475569; font-weight: bold;")
        self.pref_time_combo = QComboBox()
        self.pref_time_combo.addItems(["Any time", "Morning", "Afternoon", "Evening"])

        combo_style = """
            QComboBox {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1e293b;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
        """
        for combo in (self.period_combo, self.hours_combo, self.length_combo, self.pref_time_combo):
            combo.setStyleSheet(combo_style)

        # Generate Button
        self.gen_btn = QPushButton("⚡ Generate Plan")
        self.gen_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.gen_btn.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; border-radius: 6px; "
            "padding: 8px 18px; font-weight: bold; font-size: 13px; } "
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.gen_btn.clicked.connect(self.generate_schedule)

        config_layout.addWidget(period_lbl)
        config_layout.addWidget(self.period_combo)
        config_layout.addWidget(hours_lbl)
        config_layout.addWidget(self.hours_combo)
        config_layout.addWidget(length_lbl)
        config_layout.addWidget(self.length_combo)
        config_layout.addWidget(time_lbl)
        config_layout.addWidget(self.pref_time_combo)
        config_layout.addStretch()
        config_layout.addWidget(self.gen_btn)

        main_layout.addWidget(config_card)

        # ── 4. Scroll Area for Generated Schedule Cards ──────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 10, 0, 10)
        self.scroll_layout.setSpacing(14)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.load_data()

    def load_data(self):
        """Loads saved study plans and updates top summary metrics."""
        user_id = self.user_info.get("user_id")
        summary_data = self.service.get_planner_summary(user_id)

        # ── Update Summary Banner ─────────────────────────────────────────────
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        top_stats_layout = QHBoxLayout()
        h_val = summary_data["total_hours"]
        s_val = summary_data["total_sessions"]

        hrs_lbl = QLabel(f"⏱ <b>Total Study Hours:</b> {h_val}h")
        hrs_lbl.setStyleSheet("color: #1e293b; font-size: 14px;")

        sess_lbl = QLabel(f"📚 <b>Total Sessions:</b> {s_val}")
        sess_lbl.setStyleSheet("color: #1e293b; font-size: 14px;")

        top_stats_layout.addWidget(hrs_lbl)
        top_stats_layout.addSpacing(25)
        top_stats_layout.addWidget(sess_lbl)
        top_stats_layout.addStretch()

        self.summary_layout.addLayout(top_stats_layout)

        # Per-course breakdown chips
        if summary_data["course_breakdown"]:
            breakdown_layout = QHBoxLayout()
            b_hdr = QLabel("Allocation:")
            b_hdr.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px;")
            breakdown_layout.addWidget(b_hdr)

            for c_code, hrs in summary_data["course_breakdown"].items():
                chip = QLabel(f"{c_code}: {hrs}h")
                chip.setStyleSheet("background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;")
                breakdown_layout.addWidget(chip)
            breakdown_layout.addStretch()
            self.summary_layout.addLayout(breakdown_layout)

        # ── Update Schedule Cards List ────────────────────────────────────────
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        plans = summary_data["plans"]
        if not plans:
            empty_card = QFrame()
            empty_card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1px solid #cbd5e0; }")
            e_lay = QVBoxLayout(empty_card)
            e_lay.setContentsMargins(20, 20, 20, 20)
            e_lbl = QLabel("ℹ️ No study plan generated yet. Select your preferences above and click '⚡ Generate Plan'.")
            e_lbl.setAlignment(Qt.AlignCenter)
            e_lbl.setStyleSheet("color: #64748b; font-weight: bold; font-size: 13px;")
            e_lay.addWidget(e_lbl)
            self.scroll_layout.addWidget(empty_card)
            self.scroll_layout.addStretch()
            return

        # Change generate button text to Regenerate Plan when plans exist
        self.gen_btn.setText("⚡ Regenerate Plan")

        for p in plans:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e0; }")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)

            # Left Info Column
            left_col = QVBoxLayout()
            left_col.setSpacing(4)

            time_lbl = QLabel(f"📅 {p['study_date']} ({p['duration_minutes']} mins)")
            time_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            time_lbl.setStyleSheet("color: #2563eb;")

            course_lbl = QLabel(f"📖 {p['course_code']} — {p['course_title']}")
            course_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
            course_lbl.setStyleSheet("color: #0f172a;")

            task_lbl = QLabel(p['task'])
            task_lbl.setStyleSheet("color: #475569; font-size: 13px;")

            left_col.addWidget(time_lbl)
            left_col.addWidget(course_lbl)
            left_col.addWidget(task_lbl)

            # Right Controls Column: Status Dropdown
            right_col = QVBoxLayout()
            right_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            status_combo = QComboBox()
            status_combo.addItems(["Pending", "Completed", "Skipped"])
            status_combo.setCursor(QCursor(Qt.PointingHandCursor))
            status_combo.setStyleSheet("""
                QComboBox {
                    background-color: #f8fafc;
                    color: #0f172a;
                    border: 1px solid #cbd5e0;
                    border-radius: 6px;
                    padding: 5px 10px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 110px;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #0f172a;
                    selection-background-color: #2563eb;
                    selection-color: #ffffff;
                }
            """)

            # Set current index
            status_idx = p.get("completed", 0)
            if status_idx in (0, 1, 2):
                status_combo.setCurrentIndex(status_idx)

            plan_id = p["plan_id"]
            status_combo.currentIndexChanged.connect(
                lambda idx, pid=plan_id: self.on_status_changed(pid, idx)
            )

            right_col.addWidget(status_combo)

            card_layout.addLayout(left_col)
            card_layout.addStretch()
            card_layout.addLayout(right_col)

            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def generate_schedule(self):
        """Triggers deterministic schedule generation based on UI settings."""
        user_id = self.user_info.get("user_id")
        period = self.period_combo.currentText()

        # Parse hours
        hrs_str = self.hours_combo.currentText().split(" ")[0]
        try:
            hrs_val = float(hrs_str)
        except ValueError:
            hrs_val = 3.0

        # Parse session length
        len_str = self.length_combo.currentText().split(" ")[0]
        try:
            len_val = int(len_str)
        except ValueError:
            len_val = 60

        pref_time = self.pref_time_combo.currentText()

        generated = self.service.generate_and_save_plan(
            user_id=user_id,
            planning_period=period,
            hours_per_day=hrs_val,
            session_length_mins=len_val,
            preferred_time=pref_time
        )

        if not generated:
            show_dark_message_box(
                self, QMessageBox.Warning, "No Courses Found",
                "Please add your courses in the Profile page first before generating a study plan."
            )
            return

        self.load_data()
        show_dark_message_box(
            self, QMessageBox.Information, "Plan Generated",
            f"Successfully generated {len(generated)} study session(s)!"
        )

    def on_status_changed(self, plan_id: int, status_index: int):
        """Persists completion status change to database (0=Pending, 1=Completed, 2=Skipped)."""
        self.service.update_session_completion(plan_id, status_index)
