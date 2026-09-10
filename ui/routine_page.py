from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QComboBox, QMessageBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor
from services.academic_service import AcademicService
from ui.dialog_helpers import DUMMY_COURSES, CLASS_SLOTS, LAB_SLOTS, setup_dark_dialog, TABLE_STYLE

DAYS_ORDER = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

class RoutinePage(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"user_id": None}
        self.service = AcademicService()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header Area
        header_layout = QHBoxLayout()
        title = QLabel("📅 Class Routine")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        
        add_btn = QPushButton("+ Add Class")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.setStyleSheet("background-color: #2563eb; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold;")
        add_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        # Scroll Area for Daywise Sections
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 10, 0, 10)
        self.scroll_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.load_data()

    def load_data(self):
        # Clear existing widgets from scroll layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        all_routines = self.service.get_routines(self.user_info.get("user_id"))

        # Group routines by day
        routines_by_day = {day: [] for day in DAYS_ORDER}
        for r in all_routines:
            day = r.get("day_of_week", "Saturday")
            if day not in routines_by_day:
                routines_by_day[day] = []
            routines_by_day[day].append(r)

        # Build day sections
        has_any = False
        for day in DAYS_ORDER:
            day_items = routines_by_day[day]
            if not day_items and day not in ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"]:
                continue # Skip empty weekend days if no routines

            has_any = True
            day_card = QFrame()
            day_card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1px solid #cbd5e0; }")
            day_layout = QVBoxLayout(day_card)
            day_layout.setContentsMargins(15, 15, 15, 15)

            # Day Section Header Banner
            day_header = QLabel(f"🗓 {day.upper()}")
            day_header.setFont(QFont("Segoe UI", 13, QFont.Bold))
            day_header.setStyleSheet("color: #2563eb; background-color: #eff6ff; padding: 6px 12px; border-radius: 6px; font-weight: bold;")
            day_layout.addWidget(day_header)

            if not day_items:
                no_class_lbl = QLabel("No classes scheduled")
                no_class_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 13px; padding: 10px;")
                day_layout.addWidget(no_class_lbl)
            else:
                from PySide6.QtWidgets import QAbstractItemView
                table = QTableWidget()
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(["Course No", "Time Slot", "Teacher's Name", "Room No", "Action"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
                table.setColumnWidth(4, 90)
                table.verticalHeader().setDefaultSectionSize(45)
                table.setStyleSheet(TABLE_STYLE)
                table.setRowCount(len(day_items))

                for row, item in enumerate(day_items):
                    raw_course = item.get("course_title", "")
                    # Extract Course No e.g. "CSE 2101" from "CSE 2101 - Data Structures & Algorithms (Class)"
                    course_code = raw_course.split(" - ")[0].split(" (")[0] if " - " in raw_course else raw_course.split(" (")[0]

                    time_slot = item.get("start_time", "")
                    teacher_info = item.get("end_time", "")
                    
                    # Parsing teacher / room if embedded
                    teacher_name = teacher_info
                    room_no = "-"
                    if "|" in teacher_info:
                        parts = teacher_info.split("|")
                        teacher_name = parts[0].replace("Teacher:", "").strip()
                        if len(parts) > 1 and "Room:" in parts[1]:
                            room_no = parts[1].replace("Room:", "").strip()
                        if len(parts) > 2 and "Slot:" in parts[2]:
                            time_slot = parts[2].replace("Slot:", "").strip()

                    table.setItem(row, 0, QTableWidgetItem(course_code))
                    table.setItem(row, 1, QTableWidgetItem(time_slot))
                    table.setItem(row, 2, QTableWidgetItem(teacher_name))
                    table.setItem(row, 3, QTableWidgetItem(room_no))

                    del_btn = QPushButton("Delete")
                    del_btn.setCursor(QCursor(Qt.PointingHandCursor))
                    del_btn.setStyleSheet("background-color: #ef4444; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 12px;")
                    routine_id = item.get("routine_id")
                    del_btn.clicked.connect(lambda _, rid=routine_id: self.delete_routine(rid))
                    table.setCellWidget(row, 4, del_btn)

                # Set table height dynamically based on rows
                table.setFixedHeight(50 + len(day_items) * 48)
                day_layout.addWidget(table)

            self.scroll_layout.addWidget(day_card)

        self.scroll_layout.addStretch()

    def delete_routine(self, routine_id):
        if routine_id:
            self.service.delete_routine(routine_id)
            self.load_data()

    def open_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Class / Lab Routine")
        dialog.setFixedWidth(450)
        setup_dark_dialog(dialog)

        d_layout = QFormLayout(dialog)
        d_layout.setSpacing(12)

        # 1. Day dropdown (Sat-Wed)
        day_combo = QComboBox()
        day_combo.addItems(["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"])

        # 2. Type dropdown (Class or Lab)
        type_combo = QComboBox()
        type_combo.addItems(["Class", "Lab"])

        # 3. Dynamic Time slot dropdown
        slot_combo = QComboBox()
        slot_combo.addItems(CLASS_SLOTS)

        def update_slots(index):
            slot_combo.clear()
            if type_combo.currentText() == "Class":
                slot_combo.addItems(CLASS_SLOTS)
            else:
                slot_combo.addItems(LAB_SLOTS)

        type_combo.currentIndexChanged.connect(update_slots)

        # 4. Course No dropdown
        course_combo = QComboBox()
        course_combo.addItems(DUMMY_COURSES)

        # 5. Teacher's name
        teacher_in = QLineEdit()
        teacher_in.setPlaceholderText("Teacher's Name")

        # 6. Room No (Optional)
        room_in = QLineEdit()
        room_in.setPlaceholderText("Room No (Optional)")

        d_layout.addRow("Select Day:", day_combo)
        d_layout.addRow("Class / Lab:", type_combo)
        d_layout.addRow("Select Time:", slot_combo)
        d_layout.addRow("Course No:", course_combo)
        d_layout.addRow("Teacher's Name:", teacher_in)
        d_layout.addRow("Room No:", room_in)

        save_btn = QPushButton("Save Routine")
        
        def save():
            if not teacher_in.text().strip():
                QMessageBox.warning(dialog, "Input Error", "Please enter Teacher's Name.")
                return

            selected_course = course_combo.currentText()
            session_type = type_combo.currentText()
            course_title = f"{selected_course} ({session_type})"
            day = day_combo.currentText()
            time_slot = slot_combo.currentText()
            
            teacher = teacher_in.text().strip()
            room = room_in.text().strip()
            extra_details = f"Teacher: {teacher}" + (f" | Room: {room}" if room else "") + f" | Slot: {time_slot}"

            self.service.add_routine(
                self.user_info.get("user_id"),
                course_title,
                day,
                time_slot,
                extra_details
            )
            dialog.accept()
            self.load_data()

        save_btn.clicked.connect(save)
        d_layout.addRow(save_btn)
        dialog.exec()
