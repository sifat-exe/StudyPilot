import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QFormLayout, QComboBox,
    QFileDialog, QMessageBox, QTextEdit, QProgressDialog
)
from PySide6.QtCore import Qt, QUrl, QThread, Signal
from PySide6.QtGui import QFont, QCursor, QDesktopServices
from services.study_material_service import StudyMaterialService
from services.pdf_extraction_service import PDFExtractionService
from services.topic_identification_service import TopicIdentificationService
from ui.dialog_helpers import setup_dark_dialog, show_dark_message_box


class PDFExtractionWorker(QThread):
    """Background worker thread to run PDF extraction/OCR without freezing the PySide6 main UI."""
    progress = Signal(int, int)
    finished = Signal(object)

    def __init__(self, pdf_service, file_path):
        super().__init__()
        self.pdf_service = pdf_service
        self.file_path = file_path

    def run(self):
        def on_progress(current, total):
            self.progress.emit(current, total)

        result = self.pdf_service.extract_text(self.file_path, progress_callback=on_progress)
        self.finished.emit(result)


class TopicIdentificationWorker(QThread):
    """
    Background worker thread to run Gemini topic identification
    without freezing the PySide6 main UI.

    Emits:
        finished(TopicResult) — when topic identification completes.
    """
    finished = Signal(object)

    def __init__(self, topic_service, extracted_text):
        super().__init__()
        self.topic_service = topic_service
        self.extracted_text = extracted_text

    def run(self):
        result = self.topic_service.identify_topics(self.extracted_text)
        self.finished.emit(result)


class StudyMaterialsPage(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"user_id": None}
        self.service = StudyMaterialService()
        self.pdf_service = PDFExtractionService()
        self.topic_service = TopicIdentificationService()
        self._active_worker = None        # PDF extraction worker reference
        self._active_topic_worker = None  # Topic identification worker reference
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header Area
        header_layout = QHBoxLayout()
        title = QLabel("📚 Study Materials")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")

        add_btn = QPushButton("+ Upload PDF")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.setStyleSheet(
            "background-color: #2563eb; color: white; border-radius: 6px; "
            "padding: 8px 16px; font-weight: bold;"
        )
        add_btn.clicked.connect(self.open_upload_dialog)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        # Scroll Area for Course Materials Sections
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

        user_id = self.user_info.get("user_id")
        user_courses = self.service.get_user_courses(user_id)
        all_materials = self.service.get_materials(user_id)

        # Handle empty states: No profile courses found
        if not user_courses:
            empty_card = QFrame()
            empty_card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1px solid #cbd5e0; }")
            card_layout = QVBoxLayout(empty_card)
            card_layout.setContentsMargins(20, 20, 20, 20)

            msg_label = QLabel("⚠️ No courses found.\nPlease add a course from your Profile first.")
            msg_label.setAlignment(Qt.AlignCenter)
            msg_label.setStyleSheet("color: #64748b; font-size: 14px; font-weight: bold; line-height: 1.5;")
            card_layout.addWidget(msg_label)

            self.scroll_layout.addWidget(empty_card)
            self.scroll_layout.addStretch()
            return

        # Overall material status banner if no materials uploaded across all courses
        if not all_materials:
            banner_card = QFrame()
            banner_card.setStyleSheet("QFrame { background-color: #eff6ff; border-radius: 8px; border: 1px solid #bfdbfe; }")
            banner_layout = QHBoxLayout(banner_card)
            banner_layout.setContentsMargins(15, 12, 15, 12)

            banner_lbl = QLabel("ℹ️ No study materials uploaded yet. Click '+ Upload PDF' to get started.")
            banner_lbl.setStyleSheet("color: #1e40af; font-size: 13px; font-weight: bold;")
            banner_layout.addWidget(banner_lbl)
            self.scroll_layout.addWidget(banner_card)

        # Build section card for each course from user's Profile
        for course in user_courses:
            course_id = course.get("course_id")
            course_code = (course.get("course_code") or "").strip()
            course_title = (course.get("course_title") or "").strip()
            course_label = f"{course_code} - {course_title}" if course_title else course_code

            # Find materials for this course
            course_materials = [
                m for m in all_materials
                if m.get("course_id") == course_id or m.get("course_code") == course_code
            ]

            course_card = QFrame()
            course_card.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1px solid #cbd5e0; }")
            card_layout = QVBoxLayout(course_card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            card_layout.setSpacing(10)

            # Course Header Banner
            card_header = QLabel(f"📖 {course_label}")
            card_header.setFont(QFont("Segoe UI", 13, QFont.Bold))
            card_header.setStyleSheet("color: #2563eb; background-color: #f1f5f9; padding: 6px 12px; border-radius: 6px;")
            card_layout.addWidget(card_header)

            if not course_materials:
                no_mat_lbl = QLabel("No materials uploaded.")
                no_mat_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 13px; padding: 6px 12px;")
                card_layout.addWidget(no_mat_lbl)
            else:
                for mat in course_materials:
                    item_frame = QFrame()
                    item_frame.setStyleSheet("QFrame { background-color: #f8fafc; border-radius: 6px; border: 1px solid #e2e8f0; }")
                    item_layout = QHBoxLayout(item_frame)
                    item_layout.setContentsMargins(12, 8, 12, 8)

                    file_lbl = QLabel(f"📄 {mat.get('file_name', 'Document.pdf')}")
                    file_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    file_lbl.setStyleSheet("color: #1e293b; background-color: transparent;")

                    # Extract / Analyze Text Action Button
                    extract_btn = QPushButton("🔍 Extract Text")
                    extract_btn.setCursor(QCursor(Qt.PointingHandCursor))
                    extract_btn.setStyleSheet(
                        "background-color: #0f172a; color: #38bdf8; border: 1px solid #334155; "
                        "border-radius: 5px; padding: 5px 12px; font-weight: bold; font-size: 12px;"
                    )
                    extract_btn.clicked.connect(lambda _, m=mat: self.analyze_material(m))

                    # Open PDF Button
                    open_btn = QPushButton("Open")
                    open_btn.setCursor(QCursor(Qt.PointingHandCursor))
                    open_btn.setStyleSheet(
                        "background-color: #2563eb; color: white; border-radius: 5px; "
                        "padding: 5px 14px; font-weight: bold; font-size: 12px;"
                    )
                    open_btn.clicked.connect(lambda _, m=mat: self.open_material(m))

                    item_layout.addWidget(file_lbl)
                    item_layout.addStretch()
                    item_layout.addWidget(extract_btn)
                    item_layout.addWidget(open_btn)

                    card_layout.addWidget(item_frame)

            self.scroll_layout.addWidget(course_card)

        self.scroll_layout.addStretch()

    def analyze_material(self, material):
        """
        Runs the full PDF Analysis pipeline:
          1. PDF text extraction (native / OCR) — background QThread.
          2. Main topic identification via Gemini AI — second background QThread.
        """
        file_path = material.get("file_path")
        if not file_path or not os.path.exists(file_path):
            show_dark_message_box(self, QMessageBox.Warning, "File Not Found", "The PDF file could not be found.")
            return

        # ── Stage 1: PDF Extraction Progress Dialog ────────────────────────────
        progress_dialog = QProgressDialog("Evaluating PDF text & preparing extraction...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("PDF Extraction Progress")
        progress_dialog.setWindowModality(Qt.WindowModal)
        setup_dark_dialog(progress_dialog)
        progress_dialog.setAutoClose(True)
        progress_dialog.show()

        extraction_worker = PDFExtractionWorker(self.pdf_service, file_path)

        def update_progress(current, total):
            progress_dialog.setMaximum(total)
            progress_dialog.setValue(current)
            progress_dialog.setLabelText(f"Processing Page {current} of {total}...\nPlease wait.")

        def on_extraction_finished(extraction_result):
            """Called when PDF extraction completes. Immediately starts topic identification."""
            progress_dialog.close()

            # If extraction itself failed, show the dialog now (no topics to fetch).
            if not extraction_result.success or not extraction_result.extracted_text.strip():
                self.show_extraction_preview_dialog(extraction_result, topic_result=None)
                return

            # ── Stage 2: Topic Identification Progress Dialog ──────────────────
            topic_dialog = QProgressDialog(
                "Identifying main topics using AI...\nThis may take a few seconds.",
                None,  # No cancel button — keep it simple
                0, 0,  # Indeterminate (spinner) mode
                self
            )
            topic_dialog.setWindowTitle("Topic Identification")
            topic_dialog.setWindowModality(Qt.WindowModal)
            setup_dark_dialog(topic_dialog)
            topic_dialog.show()

            topic_worker = TopicIdentificationWorker(self.topic_service, extraction_result.extracted_text)

            def on_topics_finished(topic_result):
                """Called when Gemini returns topics. Opens the combined preview dialog."""
                topic_dialog.close()
                self.show_extraction_preview_dialog(extraction_result, topic_result=topic_result)

            topic_worker.finished.connect(on_topics_finished)
            self._active_topic_worker = topic_worker  # Keep reference to prevent GC
            topic_worker.start()

        extraction_worker.progress.connect(update_progress)
        extraction_worker.finished.connect(on_extraction_finished)

        self._active_worker = extraction_worker  # Keep reference to prevent GC
        extraction_worker.start()


    def show_extraction_preview_dialog(self, result, topic_result=None):
        """
        Displays the PDF analysis results dialog.

        Shows:
          - File metadata (name, extraction method, page/char counts)
          - Identified main topics (if topic_result provided)
          - Read-only extracted text preview

        Parameters
        ----------
        result : PDFExtractionResult
            Returned by PDFExtractionService.
        topic_result : TopicResult or None
            Returned by TopicIdentificationService. None if skipped due to extraction failure.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF Analysis Results")
        dialog.resize(700, 680)
        setup_dark_dialog(dialog)

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 20, 20, 20)
        d_layout.setSpacing(14)

        # ── Title & Meta Info Card ─────────────────────────────────────────────
        meta_card = QFrame()
        meta_card.setStyleSheet("QFrame { background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; }")
        meta_layout = QVBoxLayout(meta_card)
        meta_layout.setContentsMargins(15, 12, 15, 12)

        file_label = QLabel(f"📄 {result.file_name}")
        file_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        file_label.setStyleSheet("color: #38bdf8; background-color: transparent;")

        stats_layout = QHBoxLayout()
        method_badge = f"Method: {result.extraction_method}"
        method_color = "#34d399" if result.extraction_method == "Native" else "#fbbf24"
        method_lbl = QLabel(f"<b>{method_badge}</b>")
        method_lbl.setStyleSheet(f"color: {method_color}; font-size: 13px; background-color: #1e293b; padding: 3px 8px; border-radius: 4px;")

        pages_lbl = QLabel(f"Pages: <b>{result.page_count}</b> (Meaningful: {result.meaningful_pages} / {int(result.meaningful_ratio*100)}%)")
        pages_lbl.setStyleSheet("color: #cbd5e0; font-size: 13px; background-color: transparent;")

        chars_lbl = QLabel(f"Characters: <b>{result.char_count:,}</b>")
        chars_lbl.setStyleSheet("color: #cbd5e0; font-size: 13px; background-color: transparent;")

        stats_layout.addWidget(method_lbl)
        stats_layout.addSpacing(15)
        stats_layout.addWidget(pages_lbl)
        stats_layout.addSpacing(15)
        stats_layout.addWidget(chars_lbl)
        stats_layout.addStretch()

        meta_layout.addWidget(file_label)
        meta_layout.addLayout(stats_layout)
        d_layout.addWidget(meta_card)

        # ── Status / Warning Banners ───────────────────────────────────────────
        if not result.success and result.error_message:
            err_card = QFrame()
            err_card.setStyleSheet("QFrame { background-color: #450a0a; border-radius: 6px; border: 1px solid #7f1d1d; }")
            err_layout = QHBoxLayout(err_card)
            err_layout.setContentsMargins(12, 10, 12, 10)
            err_lbl = QLabel(f"❌ {result.error_message}")
            err_lbl.setStyleSheet("color: #fca5a5; font-size: 12px; font-weight: bold; background-color: transparent;")
            err_lbl.setWordWrap(True)
            err_layout.addWidget(err_lbl)
            d_layout.addWidget(err_card)

        # ── Main Topics Card ───────────────────────────────────────────────────
        # Always show the topics section (even if empty / errored) so the user
        # can see that the AI step ran.
        topics_card = QFrame()
        topics_card.setStyleSheet(
            "QFrame { background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; }"
        )
        topics_layout = QVBoxLayout(topics_card)
        topics_layout.setContentsMargins(15, 12, 15, 14)
        topics_layout.setSpacing(6)

        topics_header = QLabel("🧠 Main Topics Identified")
        topics_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        topics_header.setStyleSheet("color: #a78bfa; background-color: transparent;")
        topics_layout.addWidget(topics_header)

        if topic_result is None:
            # Extraction failed before topics could be identified
            skip_lbl = QLabel("Topic identification was skipped (extraction unsuccessful).")
            skip_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic; background-color: transparent;")
            topics_layout.addWidget(skip_lbl)

        elif not topic_result.success:
            # Gemini call failed
            ai_err_lbl = QLabel(f"⚠️ {topic_result.error_message}")
            ai_err_lbl.setStyleSheet("color: #fbbf24; font-size: 12px; background-color: transparent;")
            ai_err_lbl.setWordWrap(True)
            topics_layout.addWidget(ai_err_lbl)

        elif not topic_result.topics:
            # Success but Gemini found nothing
            none_lbl = QLabel("No distinct academic topics were identified in this document.")
            none_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic; background-color: transparent;")
            topics_layout.addWidget(none_lbl)

        else:
            # ✅ Display numbered topic list
            count_lbl = QLabel(f"{topic_result.topic_count} topic(s) found")
            count_lbl.setStyleSheet("color: #64748b; font-size: 11px; background-color: transparent;")
            topics_layout.addWidget(count_lbl)

            for index, topic in enumerate(topic_result.topics, start=1):
                topic_lbl = QLabel(f"  {index}.  {topic}")
                topic_lbl.setStyleSheet(
                    "color: #e2e8f0; font-size: 13px; background-color: #1e293b; "
                    "padding: 5px 10px; border-radius: 4px; border-left: 3px solid #a78bfa;"
                )
                topic_lbl.setWordWrap(True)
                topics_layout.addWidget(topic_lbl)

        d_layout.addWidget(topics_card)

        # ── Extracted Text Preview ─────────────────────────────────────────────
        preview_header = QLabel("Extracted Text Preview")
        preview_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        preview_header.setStyleSheet("color: #ffffff;")
        d_layout.addWidget(preview_header)

        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setPlainText(result.preview_text if result.preview_text else "No text extracted.")
        text_area.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: "Consolas", "Segoe UI", monospace;
                font-size: 13px;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        d_layout.addWidget(text_area, 1)

        # ── Close Button ───────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet(
            "background-color: #2563eb; color: white; border-radius: 6px; "
            "padding: 8px 22px; font-weight: bold;"
        )
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        d_layout.addLayout(btn_layout)

        dialog.exec()

    def open_material(self, material):
        file_path = material.get("file_path")
        if not file_path or not os.path.exists(file_path):
            show_dark_message_box(self, QMessageBox.Warning, "File Not Found", "The PDF file could not be found.")
            return

        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        if not opened:
            show_dark_message_box(self, QMessageBox.Warning, "Error", "Could not open the selected PDF file.")

    def open_upload_dialog(self):
        user_id = self.user_info.get("user_id")
        course_labels = self.service.get_course_labels(user_id)
        user_courses = self.service.get_user_courses(user_id)

        if not course_labels or not user_courses:
            show_dark_message_box(
                self, QMessageBox.Warning, "No Courses Found",
                "Please add a course from your Profile first."
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Upload Study Material")
        dialog.setFixedWidth(450)
        setup_dark_dialog(dialog)

        d_layout = QFormLayout(dialog)
        d_layout.setSpacing(14)

        # 1. Course Dropdown
        course_combo = QComboBox()
        course_combo.addItems(course_labels)

        # 2. PDF Selector
        selected_file_path = {"path": ""}

        pdf_select_btn = QPushButton("Choose PDF...")
        pdf_select_btn.setCursor(QCursor(Qt.PointingHandCursor))
        pdf_select_btn.setStyleSheet(
            "background-color: #334155; color: #ffffff; border-radius: 6px; "
            "padding: 8px 12px; font-weight: bold; font-size: 13px;"
        )

        file_label = QLabel("No file selected")
        file_label.setStyleSheet("color: #cbd5e0; font-size: 12px; font-style: italic;")

        def choose_file():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog,
                "Select PDF File",
                "",
                "PDF Files (*.pdf)"
            )
            if file_path:
                selected_file_path["path"] = file_path
                file_label.setText(f"Selected: {os.path.basename(file_path)}")
                file_label.setStyleSheet("color: #38bdf8; font-size: 12px; font-weight: bold;")

        pdf_select_btn.clicked.connect(choose_file)

        pdf_picker_layout = QVBoxLayout()
        pdf_picker_layout.addWidget(pdf_select_btn)
        pdf_picker_layout.addWidget(file_label)

        d_layout.addRow("Course:", course_combo)
        d_layout.addRow("PDF File:", pdf_picker_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet(
            "background-color: #475569; color: white; border-radius: 6px; "
            "padding: 8px 16px; font-weight: bold;"
        )
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton("Save PDF")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setStyleSheet(
            "background-color: #2563eb; color: white; border-radius: 6px; "
            "padding: 8px 16px; font-weight: bold;"
        )

        def save():
            file_path = selected_file_path["path"].strip()
            if not file_path:
                show_dark_message_box(dialog, QMessageBox.Warning, "Input Error", "Please select a PDF file.")
                return

            if not file_path.lower().endswith(".pdf"):
                show_dark_message_box(dialog, QMessageBox.Warning, "Input Error", "Please select a valid PDF file.")
                return

            selected_idx = course_combo.currentIndex()
            if selected_idx < 0 or selected_idx >= len(user_courses):
                show_dark_message_box(dialog, QMessageBox.Warning, "Input Error", "Please select a course.")
                return

            selected_course = user_courses[selected_idx]
            course_id = selected_course.get("course_id")
            course_code = selected_course.get("course_code", "")

            try:
                self.service.upload_material(
                    user_id=user_id,
                    course_id=course_id,
                    source_file_path=file_path,
                    course_code=course_code
                )
                dialog.accept()
                self.load_data()
                show_dark_message_box(self, QMessageBox.Information, "Success", "PDF uploaded successfully!")
            except Exception as e:
                show_dark_message_box(dialog, QMessageBox.Critical, "Upload Failed", str(e))

        save_btn.clicked.connect(save)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        d_layout.addRow(btn_layout)

        dialog.exec()
