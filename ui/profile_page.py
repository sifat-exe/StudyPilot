from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QScrollArea, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor
from services.profile_service import ProfileService
from ui.dialog_helpers import show_dark_message_box

YEAR_OPTIONS = ["1st", "2nd", "3rd", "4th"]
SEMESTER_OPTIONS = ["Odd", "Even"]
COURSE_SLOT_COUNT = 5

INPUT_STYLE = """
    QLineEdit, QComboBox {
        background-color: #ffffff;
        color: #1e293b;
        border: 1px solid #cbd5e0;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 13px;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #3b82f6;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #1e293b;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
    }
"""


class ProfilePage(QWidget):
    profile_saved = Signal(dict)

    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"user_id": None, "name": ""}
        self.service = ProfileService()
        self.course_ids = [None] * COURSE_SLOT_COUNT
        self.init_ui()
        self.load_data()

    def init_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(30, 30, 30, 30)

        header = QHBoxLayout()
        title = QLabel("👤 Student Profile")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        header.addWidget(title)
        header.addStretch()
        page_layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 10, 0, 10)
        content_layout.setSpacing(20)

        personal_card = self._card()
        personal_layout = QVBoxLayout(personal_card)
        personal_layout.setContentsMargins(20, 18, 20, 20)
        personal_layout.setSpacing(12)

        personal_title = QLabel("Personal Information")
        personal_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        personal_title.setStyleSheet("color: #1e293b;")
        personal_layout.addWidget(personal_title)

        form = QGridLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.university_input = QLineEdit()
        self.university_input.setPlaceholderText("University name")
        self.roll_input = QLineEdit()
        self.roll_input.setPlaceholderText("e.g. 2023123")
        self.year_combo = QComboBox()
        self.year_combo.addItems(YEAR_OPTIONS)
        self.semester_combo = QComboBox()
        self.semester_combo.addItems(SEMESTER_OPTIONS)

        for widget in (
            self.name_input, self.university_input, self.roll_input,
            self.year_combo, self.semester_combo
        ):
            widget.setStyleSheet(INPUT_STYLE)
            widget.setMinimumHeight(36)

        form.addWidget(self._field_label("Name"), 0, 0)
        form.addWidget(self.name_input, 1, 0)
        form.addWidget(self._field_label("University"), 0, 1)
        form.addWidget(self.university_input, 1, 1)
        form.addWidget(self._field_label("Roll"), 2, 0)
        form.addWidget(self.roll_input, 3, 0)
        form.addWidget(self._field_label("Year"), 2, 1)
        form.addWidget(self.year_combo, 3, 1)
        form.addWidget(self._field_label("Semester"), 4, 0)
        form.addWidget(self.semester_combo, 5, 0)
        personal_layout.addLayout(form)
        content_layout.addWidget(personal_card)

        courses_card = self._card()
        courses_layout = QVBoxLayout(courses_card)
        courses_layout.setContentsMargins(20, 18, 20, 20)
        courses_layout.setSpacing(12)

        courses_title = QLabel("Courses")
        courses_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        courses_title.setStyleSheet("color: #1e293b;")
        courses_hint = QLabel(
            "These courses are used in Class Tests, Assignments, and Class Routine."
        )
        courses_hint.setStyleSheet("color: #64748b; font-size: 12px;")
        courses_layout.addWidget(courses_title)
        courses_layout.addWidget(courses_hint)

        self.course_code_inputs = []
        self.course_name_inputs = []
        for index in range(COURSE_SLOT_COUNT):
            row_label = QLabel(f"Course {index + 1}")
            row_label.setStyleSheet("color: #334155; font-weight: bold; font-size: 13px;")
            courses_layout.addWidget(row_label)

            row = QHBoxLayout()
            row.setSpacing(12)
            code_input = QLineEdit()
            code_input.setPlaceholderText("Course code (e.g. CSE 2100)")
            name_input = QLineEdit()
            name_input.setPlaceholderText("Course name")
            for widget in (code_input, name_input):
                widget.setStyleSheet(INPUT_STYLE)
                widget.setMinimumHeight(36)
            row.addWidget(code_input, 1)
            row.addWidget(name_input, 2)
            courses_layout.addLayout(row)
            self.course_code_inputs.append(code_input)
            self.course_name_inputs.append(name_input)

        content_layout.addWidget(courses_card)

        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("Save Profile")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet(
            "background-color: #2563eb; color: white; border-radius: 6px; "
            "padding: 8px 22px; font-weight: bold;"
        )
        save_btn.clicked.connect(self.save_profile)
        save_row.addWidget(save_btn)
        content_layout.addLayout(save_row)
        content_layout.addStretch()

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

    def _card(self):
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #ffffff; border-radius: 10px; "
            "border: 1px solid #cbd5e0; }"
        )
        return card

    def _field_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")
        return label

    def load_data(self):
        profile = self.service.get_profile(self.user_info.get("user_id"))
        name = profile.get("name") or self.user_info.get("name") or ""
        self.name_input.setText(name)
        self.university_input.setText(profile.get("university") or "")
        self.roll_input.setText(profile.get("roll") or "")

        year = profile.get("year") or "1st"
        if year in YEAR_OPTIONS:
            self.year_combo.setCurrentText(year)
        semester = profile.get("semester") or "Odd"
        if semester in SEMESTER_OPTIONS:
            self.semester_combo.setCurrentText(semester)

        self.course_ids = [None] * COURSE_SLOT_COUNT
        for input_widget in self.course_code_inputs + self.course_name_inputs:
            input_widget.clear()

        for index, course in enumerate(profile.get("courses", [])[:COURSE_SLOT_COUNT]):
            self.course_ids[index] = course.get("course_id")
            self.course_code_inputs[index].setText(course.get("course_code") or "")
            self.course_name_inputs[index].setText(course.get("course_title") or "")

    def save_profile(self):
        name = self.name_input.text().strip()
        if not name:
            show_dark_message_box(self, QMessageBox.Warning, "Input Error", "Please enter your name.")
            return

        courses = []
        for index in range(COURSE_SLOT_COUNT):
            code = self.course_code_inputs[index].text().strip()
            title = self.course_name_inputs[index].text().strip()
            if code and not title:
                show_dark_message_box(
                    self, QMessageBox.Warning, "Input Error",
                    f"Please enter a course name for Course {index + 1}."
                )
                return
            if title and not code:
                show_dark_message_box(
                    self, QMessageBox.Warning, "Input Error",
                    f"Please enter a course code for Course {index + 1}."
                )
                return
            courses.append({
                "course_id": self.course_ids[index],
                "course_code": code,
                "course_title": title,
            })

        filled_courses = [c for c in courses if c["course_code"] and c["course_title"]]
        if not filled_courses:
            show_dark_message_box(
                self, QMessageBox.Warning, "Input Error",
                "Please add at least one course. Courses are required for "
                "Class Tests, Assignments, and Class Routine."
            )
            return

        profile = {
            "name": name,
            "university": self.university_input.text().strip(),
            "roll": self.roll_input.text().strip(),
            "year": self.year_combo.currentText(),
            "semester": self.semester_combo.currentText(),
            "courses": courses,
        }

        try:
            self.service.save_profile(self.user_info.get("user_id"), profile)
        except Exception as exc:
            show_dark_message_box(self, QMessageBox.Critical, "Save Failed", str(exc))
            return

        self.user_info["name"] = name
        self.load_data()
        self.profile_saved.emit(profile)
        show_dark_message_box(self, QMessageBox.Information, "Saved", "Profile saved successfully.")
