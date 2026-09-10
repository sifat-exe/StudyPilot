from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QCursor
from services.academic_service import AcademicService
from ui.dialog_helpers import DUMMY_COURSES, setup_dark_dialog, TABLE_STYLE

class ClassTestPage(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"user_id": None}
        self.service = AcademicService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        title = QLabel("📋 Class Tests & Exams")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        
        add_btn = QPushButton("+ Add Class Test")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.setStyleSheet("background-color: #2563eb; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold;")
        add_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Course No", "CT Topic / Title", "CT Date", "CT Time", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 90)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        tests = self.service.get_class_tests(self.user_info.get("user_id"))
        self.table.setRowCount(len(tests))

        for row, t in enumerate(tests):
            raw_course = t.get("course_title", "")
            raw_exam_title = t.get("exam_title", "")

            # If course_code is embedded in topic/exam_title e.g. "CSE 2101 - Midterm"
            if " - " in raw_exam_title:
                course_code = raw_exam_title.split(" - ")[0]
                exam_topic = raw_exam_title.split(" - ", 1)[1]
            else:
                course_code = raw_course.split(" - ")[0] if " - " in raw_course else raw_course
                exam_topic = raw_exam_title

            # Date and Time split
            full_date_time = str(t.get("exam_date", ""))
            parts = full_date_time.split(" ")
            date_str = parts[0] if parts else ""
            time_str = " ".join(parts[1:]) if len(parts) > 1 else ""

            self.table.setItem(row, 0, QTableWidgetItem(course_code))
            self.table.setItem(row, 1, QTableWidgetItem(exam_topic))
            self.table.setItem(row, 2, QTableWidgetItem(date_str))
            self.table.setItem(row, 3, QTableWidgetItem(time_str))

            del_btn = QPushButton("Delete")
            del_btn.setCursor(QCursor(Qt.PointingHandCursor))
            del_btn.setStyleSheet("background-color: #ef4444; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 12px;")
            item_id = t.get("exam_id", row)
            del_btn.clicked.connect(lambda _, target_id=item_id: self.delete_class_test(target_id))
            self.table.setCellWidget(row, 4, del_btn)

    def delete_class_test(self, item_id):
        self.service.delete_class_test(item_id)
        self.load_data()

    def open_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Class Test")
        dialog.setFixedWidth(420)
        setup_dark_dialog(dialog)
        
        d_layout = QFormLayout(dialog)
        d_layout.setSpacing(12)

        # 1. Course dropdown
        course_combo = QComboBox()
        course_combo.addItems(DUMMY_COURSES)

        # 2. Topic
        topic_in = QLineEdit()
        topic_in.setPlaceholderText("Enter CT topic or title")

        # 3. Calendar date picker
        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")

        # 4. Time input (Manual time + AM/PM dropdown)
        time_layout = QHBoxLayout()
        time_in = QLineEdit()
        time_in.setPlaceholderText("e.g. 8.00")
        
        ampm_combo = QComboBox()
        ampm_combo.addItems(["AM", "PM"])
        
        time_layout.addWidget(time_in, 2)
        time_layout.addWidget(ampm_combo, 1)

        d_layout.addRow("Course No:", course_combo)
        d_layout.addRow("Topic:", topic_in)
        d_layout.addRow("CT Date:", date_edit)
        d_layout.addRow("CT Time:", time_layout)

        save_btn = QPushButton("Save Test")
        
        def save():
            if not topic_in.text().strip() or not time_in.text().strip():
                QMessageBox.warning(dialog, "Input Error", "Please fill in both Topic and Time.")
                return
            
            selected_course = course_combo.currentText().split(" - ")[0]
            topic = f"{selected_course} - {topic_in.text().strip()}"
            formatted_date = date_edit.date().toString("yyyy-MM-dd")
            formatted_time = f"{time_in.text().strip()} {ampm_combo.currentText()}"
            date_time_combined = f"{formatted_date} {formatted_time}"

            self.service.add_class_test(
                self.user_info.get("user_id"),
                topic,
                date_time_combined
            )
            dialog.accept()
            self.load_data()

        save_btn.clicked.connect(save)
        d_layout.addRow(save_btn)
        dialog.exec()
