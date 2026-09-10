from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QCursor
from services.academic_service import AcademicService
from ui.dialog_helpers import DUMMY_COURSES, setup_dark_dialog, TABLE_STYLE

class AssignmentPage(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"user_id": None}
        self.service = AcademicService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        title = QLabel("📝 Assignments")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        
        add_btn = QPushButton("+ Add Assignment")
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
        self.table.setHorizontalHeaderLabels(["Course No", "Assignment Topic", "Deadline Date", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 90)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        assignments = self.service.get_assignments(self.user_info.get("user_id"))
        self.table.setRowCount(len(assignments))

        for row, a in enumerate(assignments):
            raw_course = a.get("course_title", "")
            course_code = raw_course.split(" - ")[0] if " - " in raw_course else raw_course
            
            raw_title = a.get("title", "")
            topic_title = raw_title.split(" - ", 1)[1] if " - " in raw_title else raw_title

            self.table.setItem(row, 0, QTableWidgetItem(course_code))
            self.table.setItem(row, 1, QTableWidgetItem(topic_title))
            self.table.setItem(row, 2, QTableWidgetItem(str(a.get("deadline", ""))))
            
            status_text = "Completed" if a.get("completed") else "Pending"
            self.table.setItem(row, 3, QTableWidgetItem(status_text))

            del_btn = QPushButton("Delete")
            del_btn.setCursor(QCursor(Qt.PointingHandCursor))
            del_btn.setStyleSheet("background-color: #ef4444; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 12px;")
            item_id = a.get("assignment_id", row)
            del_btn.clicked.connect(lambda _, target_id=item_id: self.delete_assignment(target_id))
            self.table.setCellWidget(row, 4, del_btn)

    def delete_assignment(self, item_id):
        self.service.delete_assignment(item_id)
        self.load_data()

    def open_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Assignment")
        dialog.setFixedWidth(420)
        setup_dark_dialog(dialog)

        d_layout = QFormLayout(dialog)
        d_layout.setSpacing(12)

        # 1. Course No dropdown
        course_combo = QComboBox()
        course_combo.addItems(DUMMY_COURSES)

        # 2. Topic
        topic_in = QLineEdit()
        topic_in.setPlaceholderText("Enter assignment topic")

        # 3. Calendar date picker
        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")

        d_layout.addRow("Course No:", course_combo)
        d_layout.addRow("Topic:", topic_in)
        d_layout.addRow("Deadline Date:", date_edit)

        save_btn = QPushButton("Save Assignment")
        
        def save():
            if not topic_in.text().strip():
                QMessageBox.warning(dialog, "Input Error", "Please enter assignment topic.")
                return
            
            selected_course = course_combo.currentText().split(" - ")[0]
            topic = f"{selected_course} - {topic_in.text().strip()}"
            formatted_date = date_edit.date().toString("yyyy-MM-dd")

            self.service.add_assignment(
                self.user_info.get("user_id"),
                topic,
                formatted_date
            )
            dialog.accept()
            self.load_data()

        save_btn.clicked.connect(save)
        d_layout.addRow(save_btn)
        dialog.exec()
