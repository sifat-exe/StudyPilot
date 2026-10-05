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
from services.pdf_analysis_service import PDFAnalysisService
from services.pdf_analysis_models import PDFAnalysisResult, TopicSummary
from ui.dialog_helpers import setup_dark_dialog, show_dark_message_box


class PDFAnalysisWorker(QThread):
    """
    Background worker thread running the complete 3-stage PDF Analysis pipeline
    without freezing the PySide6 UI loop.
    """
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(object)

    def __init__(self, analysis_service, file_path):
        super().__init__()
        self.analysis_service = analysis_service
        self.file_path = file_path

    def run(self):
        def on_progress(current, total):
            self.progress.emit(current, total)

        def on_status(message):
            self.status.emit(message)

        result = self.analysis_service.analyze_pdf(
            self.file_path,
            progress_callback=on_progress,
            status_callback=on_status
        )
        self.finished.emit(result)


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
        self.analysis_service = PDFAnalysisService()
        self._active_worker = None
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

                    # Check if AI analysis exists in DB for this material
                    material_id = mat.get("material_id")
                    existing_analysis = self.service.get_analysis(material_id) if material_id else None

                    if existing_analysis and existing_analysis.get("topics"):
                        action_btn = QPushButton("📋 Summary")
                        action_btn.setCursor(QCursor(Qt.PointingHandCursor))
                        action_btn.setStyleSheet(
                            "background-color: #7c3aed; color: white; border: 1px solid #6d28d9; "
                            "border-radius: 5px; padding: 5px 14px; font-weight: bold; font-size: 12px;"
                        )
                        action_btn.clicked.connect(lambda _, m=mat, a=existing_analysis: self.show_saved_summary_dialog(m, a))
                    else:
                        action_btn = QPushButton("🔍 Extract Text")
                        action_btn.setCursor(QCursor(Qt.PointingHandCursor))
                        action_btn.setStyleSheet(
                            "background-color: #0f172a; color: #38bdf8; border: 1px solid #334155; "
                            "border-radius: 5px; padding: 5px 12px; font-weight: bold; font-size: 12px;"
                        )
                        action_btn.clicked.connect(lambda _, m=mat: self.analyze_material(m))

                    # Open PDF Button
                    open_btn = QPushButton("Open")
                    open_btn.setCursor(QCursor(Qt.PointingHandCursor))
                    open_btn.setStyleSheet(
                        "background-color: #2563eb; color: white; border-radius: 5px; "
                        "padding: 5px 14px; font-weight: bold; font-size: 12px;"
                    )
                    open_btn.clicked.connect(lambda _, m=mat: self.open_material(m))

                    # Delete PDF Button
                    del_btn = QPushButton("Delete")
                    del_btn.setCursor(QCursor(Qt.PointingHandCursor))
                    del_btn.setStyleSheet(
                        "background-color: #ef4444; color: white; border-radius: 5px; "
                        "padding: 5px 12px; font-weight: bold; font-size: 12px;"
                    )
                    del_btn.clicked.connect(lambda _, m=mat: self.confirm_and_delete_material(m))

                    item_layout.addWidget(file_lbl)
                    item_layout.addStretch()
                    item_layout.addWidget(action_btn)
                    item_layout.addWidget(open_btn)
                    item_layout.addWidget(del_btn)

                    card_layout.addWidget(item_frame)

            self.scroll_layout.addWidget(course_card)

        self.scroll_layout.addStretch()

    def confirm_and_delete_material(self, material: dict):
        """
        Prompts confirmation and deletes material from DB, storage folder, and UI.
        """
        file_name = material.get("file_name", "this material")
        reply = QMessageBox.question(
            self,
            "Delete Study Material",
            f"Are you sure you want to delete '{file_name}'?\nThis will remove the file, database records, and AI summaries.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.delete_material(material)
                self.load_data()
                show_dark_message_box(
                    self, QMessageBox.Information, "Deleted",
                    f"'{file_name}' has been successfully deleted."
                )
            except Exception as e:
                show_dark_message_box(
                    self, QMessageBox.Critical, "Delete Failed", str(e)
                )


    def analyze_material(self, material):
        """
        Runs the full 3-stage PDF Analysis pipeline (Extraction, Topic Identification, Summary & Main Points Generation)
        in a background QThread, persists the result to the database, and displays the summary.
        """
        file_path = material.get("file_path")
        if not file_path or not os.path.exists(file_path):
            show_dark_message_box(self, QMessageBox.Warning, "File Not Found", "The PDF file could not be found.")
            return

        progress_dialog = QProgressDialog("Initializing PDF Analysis...", None, 0, 100, self)
        progress_dialog.setWindowTitle("PDF Analysis Pipeline")
        progress_dialog.setWindowModality(Qt.WindowModal)
        setup_dark_dialog(progress_dialog)
        progress_dialog.show()

        worker = PDFAnalysisWorker(self.analysis_service, file_path)

        def update_progress(current, total):
            progress_dialog.setMaximum(total)
            progress_dialog.setValue(current)

        def update_status(msg):
            progress_dialog.setLabelText(f"{msg}\nPlease wait...")

        def on_finished(result: PDFAnalysisResult):
            progress_dialog.close()
            material_id = material.get("material_id")

            # Persist successful analysis result to database ONLY if result.success is True
            # and result contains valid topics.
            saved_id = None
            if result and result.success and result.topics and material_id:
                try:
                    saved_id = self.service.save_analysis(material_id, result)
                except Exception as e:
                    print(f"Error saving analysis to DB: {e}")

            # Reload data to immediately update action button to '📋 Summary' if saved
            self.load_data()

            if not result or not result.success:
                err_msg = (result.error_message if result else None) or "Summary generation is temporarily unavailable. Please try again."
                show_dark_message_box(
                    self, QMessageBox.Warning, "PDF Analysis Status", err_msg
                )
            else:
                saved_analysis = self.service.get_analysis(material_id) if material_id else None
                if saved_analysis and saved_analysis.get("topics"):
                    self.show_saved_summary_dialog(material, saved_analysis)
                elif result.topics:
                    self.show_analysis_result_dialog(result)
                else:
                    show_dark_message_box(
                        self, QMessageBox.Warning, "PDF Analysis Status",
                        "Summary generation is temporarily unavailable. Please try again."
                    )


        worker.progress.connect(update_progress)
        worker.status.connect(update_status)
        worker.finished.connect(on_finished)

        self._active_worker = worker
        worker.start()

    def show_saved_summary_dialog(self, material: dict, analysis: dict):
        """
        Displays saved topic summaries retrieved from database (excluding extracted text preview).
        """
        dialog = QDialog(self)
        file_name = material.get("file_name", "Document.pdf")
        dialog.setWindowTitle(f"PDF Summary — {file_name}")
        dialog.resize(720, 560)
        setup_dark_dialog(dialog)

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 20, 20, 20)
        d_layout.setSpacing(14)

        # Header Metadata Card
        meta_card = QFrame()
        meta_card.setStyleSheet("QFrame { background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; }")
        meta_layout = QVBoxLayout(meta_card)
        meta_layout.setContentsMargins(15, 12, 15, 12)

        file_label = QLabel(f"📄 {file_name}")
        file_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        file_label.setStyleSheet("color: #38bdf8; background-color: transparent;")

        stats_layout = QHBoxLayout()
        method_badge = f"Method: {analysis.get('extraction_method', 'Native')}"
        method_color = "#34d399" if analysis.get('extraction_method') == "Native" else "#fbbf24"
        method_lbl = QLabel(f"<b>{method_badge}</b>")
        method_lbl.setStyleSheet(f"color: {method_color}; font-size: 13px; background-color: #1e293b; padding: 3px 8px; border-radius: 4px;")

        pages_lbl = QLabel(f"Pages: <b>{analysis.get('page_count', 1)}</b>")
        pages_lbl.setStyleSheet("color: #cbd5e0; font-size: 13px; background-color: transparent;")

        stats_layout.addWidget(method_lbl)
        stats_layout.addSpacing(15)
        stats_layout.addWidget(pages_lbl)
        stats_layout.addStretch()

        meta_layout.addWidget(file_label)
        meta_layout.addLayout(stats_layout)
        d_layout.addWidget(meta_card)

        # Topics & Summaries Section
        topics = analysis.get("topics", [])
        topics_card = QFrame()
        topics_card.setStyleSheet("QFrame { background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; }")
        topics_card_layout = QVBoxLayout(topics_card)
        topics_card_layout.setContentsMargins(15, 14, 15, 14)
        topics_card_layout.setSpacing(10)

        topics_header = QLabel(f"🧠 Main Topics & Summaries ({len(topics)} topics)")
        topics_header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        topics_header.setStyleSheet("color: #a78bfa; background-color: transparent;")
        topics_card_layout.addWidget(topics_header)

        if not topics:
            no_topics_lbl = QLabel("No saved topics available.")
            no_topics_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic; background-color: transparent;")
            topics_card_layout.addWidget(no_topics_lbl)
        else:
            topics_scroll = QScrollArea()
            topics_scroll.setWidgetResizable(True)
            topics_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

            topics_container = QWidget()
            topics_vbox = QVBoxLayout(topics_container)
            topics_vbox.setContentsMargins(0, 0, 0, 0)
            topics_vbox.setSpacing(12)

            for topic_item in topics:
                t_frame = QFrame()
                t_frame.setStyleSheet(
                    "QFrame { background-color: #1e293b; border-radius: 6px; "
                    "border-left: 4px solid #a78bfa; border-top: 1px solid #334155; "
                    "border-right: 1px solid #334155; border-bottom: 1px solid #334155; }"
                )
                t_layout = QVBoxLayout(t_frame)
                t_layout.setContentsMargins(12, 10, 12, 10)
                t_layout.setSpacing(6)

                t_title = QLabel(f"<b>{topic_item.get('order_index', 1)}. {topic_item.get('title', 'Topic')}</b>")
                t_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
                t_title.setStyleSheet("color: #38bdf8; background-color: transparent;")
                t_layout.addWidget(t_title)

                if topic_item.get("summary"):
                    summary_hdr = QLabel("Summary:")
                    summary_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    summary_hdr.setStyleSheet("color: #cbd5e0; background-color: transparent;")
                    t_layout.addWidget(summary_hdr)

                    summary_txt = QLabel(topic_item.get("summary"))
                    summary_txt.setWordWrap(True)
                    summary_txt.setStyleSheet("color: #f8fafc; font-size: 12px; background-color: transparent; line-height: 1.4;")
                    t_layout.addWidget(summary_txt)

                key_points = topic_item.get("key_points", [])
                if key_points:
                    kp_hdr = QLabel("Main Points:")
                    kp_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    kp_hdr.setStyleSheet("color: #cbd5e0; background-color: transparent; padding-top: 4px;")
                    t_layout.addWidget(kp_hdr)

                    for kp in key_points:
                        kp_lbl = QLabel(f"  • {kp}")
                        kp_lbl.setWordWrap(True)
                        kp_lbl.setStyleSheet("color: #e2e8f0; font-size: 12px; background-color: transparent;")
                        t_layout.addWidget(kp_lbl)

                topics_vbox.addWidget(t_frame)

            topics_scroll.setWidget(topics_container)
            topics_card_layout.addWidget(topics_scroll)

        d_layout.addWidget(topics_card)

        # Close Button
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

    def show_analysis_result_dialog(self, result: PDFAnalysisResult):
        """Fallback dialog for fresh analysis results if DB save fails."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"PDF Analysis Results — {result.file_name}")
        dialog.resize(720, 560)
        setup_dark_dialog(dialog)

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 20, 20, 20)
        d_layout.setSpacing(14)

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

        pages_lbl = QLabel(f"Pages: <b>{result.page_count}</b>")
        pages_lbl.setStyleSheet("color: #cbd5e0; font-size: 13px; background-color: transparent;")

        stats_layout.addWidget(method_lbl)
        stats_layout.addSpacing(15)
        stats_layout.addWidget(pages_lbl)
        stats_layout.addStretch()

        meta_layout.addWidget(file_label)
        meta_layout.addLayout(stats_layout)
        d_layout.addWidget(meta_card)

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

        topics_card = QFrame()
        topics_card.setStyleSheet("QFrame { background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; }")
        topics_card_layout = QVBoxLayout(topics_card)
        topics_card_layout.setContentsMargins(15, 14, 15, 14)
        topics_card_layout.setSpacing(10)

        topics_header = QLabel(f"🧠 Main Topics & Summaries ({result.topic_count} topics)")
        topics_header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        topics_header.setStyleSheet("color: #a78bfa; background-color: transparent;")
        topics_card_layout.addWidget(topics_header)

        if not result.topics:
            no_topics_lbl = QLabel("No topics identified or AI summary generation was unavailable.")
            no_topics_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic; background-color: transparent;")
            topics_card_layout.addWidget(no_topics_lbl)
        else:
            topics_scroll = QScrollArea()
            topics_scroll.setWidgetResizable(True)
            topics_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

            topics_container = QWidget()
            topics_vbox = QVBoxLayout(topics_container)
            topics_vbox.setContentsMargins(0, 0, 0, 0)
            topics_vbox.setSpacing(12)

            for topic_item in result.topics:
                t_frame = QFrame()
                t_frame.setStyleSheet(
                    "QFrame { background-color: #1e293b; border-radius: 6px; "
                    "border-left: 4px solid #a78bfa; border-top: 1px solid #334155; "
                    "border-right: 1px solid #334155; border-bottom: 1px solid #334155; }"
                )
                t_layout = QVBoxLayout(t_frame)
                t_layout.setContentsMargins(12, 10, 12, 10)
                t_layout.setSpacing(6)

                t_title = QLabel(f"<b>{topic_item.order_index}. {topic_item.title}</b>")
                t_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
                t_title.setStyleSheet("color: #38bdf8; background-color: transparent;")
                t_layout.addWidget(t_title)

                if topic_item.summary:
                    summary_hdr = QLabel("Summary:")
                    summary_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    summary_hdr.setStyleSheet("color: #cbd5e0; background-color: transparent;")
                    t_layout.addWidget(summary_hdr)

                    summary_txt = QLabel(topic_item.summary)
                    summary_txt.setWordWrap(True)
                    summary_txt.setStyleSheet("color: #f8fafc; font-size: 12px; background-color: transparent; line-height: 1.4;")
                    t_layout.addWidget(summary_txt)

                if topic_item.key_points:
                    kp_hdr = QLabel("Main Points:")
                    kp_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    kp_hdr.setStyleSheet("color: #cbd5e0; background-color: transparent; padding-top: 4px;")
                    t_layout.addWidget(kp_hdr)

                    for kp in topic_item.key_points:
                        kp_lbl = QLabel(f"  • {kp}")
                        kp_lbl.setWordWrap(True)
                        kp_lbl.setStyleSheet("color: #e2e8f0; font-size: 12px; background-color: transparent;")
                        t_layout.addWidget(kp_lbl)

                topics_vbox.addWidget(t_frame)

            topics_scroll.setWidget(topics_container)
            topics_card_layout.addWidget(topics_scroll)

        d_layout.addWidget(topics_card)

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
