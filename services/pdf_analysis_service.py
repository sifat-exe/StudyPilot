"""
pdf_analysis_service.py
───────────────────────
Unified PDF Analysis Service for StudyPilot.

Orchestrates:
  1. PDF Text Extraction (Native PyMuPDF + automatic OCR fallback)
  2. Main Topic Identification (Gemini AI)
  3. Topic-wise Academic Summary & Key Points Generation (Gemini AI)

Returns a structured, database-ready PDFAnalysisResult object.
"""

from services.pdf_extraction_service import PDFExtractionService, PDFExtractionResult
from services.ai_provider import GeminiProvider
from services.pdf_analysis_models import PDFAnalysisResult, TopicSummary


class PDFAnalysisService:
    """
    Core service responsible for full PDF document analysis.

    Usage:
        service = PDFAnalysisService()
        result: PDFAnalysisResult = service.analyze_pdf(
            file_path="...",
            progress_callback=fn(current, total),
            status_callback=fn(status_str)
        )
    """

    def __init__(self):
        self.extraction_service = PDFExtractionService()
        self._ai_provider = None

    def _get_ai_provider(self) -> GeminiProvider:
        """Lazy initializer for Gemini AI Provider."""
        if self._ai_provider is None:
            self._ai_provider = GeminiProvider()
        return self._ai_provider

    def analyze_pdf(self, file_path: str, progress_callback=None, status_callback=None) -> PDFAnalysisResult:
        """
        Runs the full 3-stage PDF analysis pipeline:
          Stage 1: Extract text (Native / OCR).
          Stage 2: Identify main academic topics.
          Stage 3: Generate topic summaries and key points.

        Parameters
        ----------
        file_path : str
            Path to the local PDF file.
        progress_callback : callable(current_page, total_pages), optional
            Progress callback during OCR page processing.
        status_callback : callable(status_message), optional
            Status message callback for UI status updates.

        Returns
        -------
        PDFAnalysisResult
            Structured, database-ready result object.
        """
        # ── STAGE 1: PDF TEXT EXTRACTION ───────────────────────────────────────
        if status_callback:
            status_callback("Stage 1/3: Extracting PDF text...")

        extraction_res: PDFExtractionResult = self.extraction_service.extract_text(
            file_path, progress_callback=progress_callback
        )

        if not extraction_res.success or not extraction_res.extracted_text.strip():
            return PDFAnalysisResult(
                file_path=extraction_res.file_path,
                file_name=extraction_res.file_name,
                page_count=extraction_res.page_count,
                extraction_method=extraction_res.extraction_method,
                extracted_text=extraction_res.extracted_text,
                meaningful_pages=extraction_res.meaningful_pages,
                meaningful_ratio=extraction_res.meaningful_ratio,
                is_scanned=extraction_res.is_scanned,
                topics=[],
                success=False,
                error_message=extraction_res.error_message or "No readable text extracted from PDF."
            )

        # ── STAGES 2 & 3: TOPIC IDENTIFICATION & SUMMARY GENERATION ─────────────
        try:
            ai = self._get_ai_provider()

            # Stage 2: Topic Identification
            if status_callback:
                status_callback("Stage 2/3: Identifying main topics with AI...")

            topic_titles = ai.identify_topics_from_text(extraction_res.extracted_text)

            topic_summaries = []
            if topic_titles:
                # Stage 3: Summary & Key Points Generation
                if status_callback:
                    status_callback(f"Stage 3/3: Generating summaries for {len(topic_titles)} topic(s)...")

                raw_summaries = ai.generate_summaries_for_topics(
                    extraction_res.extracted_text,
                    topic_titles
                )

                for idx, item in enumerate(raw_summaries, start=1):
                    topic_summaries.append(
                        TopicSummary(
                            title=item.get("topic", f"Topic {idx}"),
                            summary=item.get("summary", "Summary unavailable."),
                            key_points=item.get("key_points", []),
                            order_index=idx
                        )
                    )

            return PDFAnalysisResult(
                file_path=extraction_res.file_path,
                file_name=extraction_res.file_name,
                page_count=extraction_res.page_count,
                extraction_method=extraction_res.extraction_method,
                extracted_text=extraction_res.extracted_text,
                meaningful_pages=extraction_res.meaningful_pages,
                meaningful_ratio=extraction_res.meaningful_ratio,
                is_scanned=extraction_res.is_scanned,
                topics=topic_summaries,
                success=True,
                error_message=""
            )

        except Exception as e:
            # If AI processing encounters an unexpected error, return extraction data + error details
            return PDFAnalysisResult(
                file_path=extraction_res.file_path,
                file_name=extraction_res.file_name,
                page_count=extraction_res.page_count,
                extraction_method=extraction_res.extraction_method,
                extracted_text=extraction_res.extracted_text,
                meaningful_pages=extraction_res.meaningful_pages,
                meaningful_ratio=extraction_res.meaningful_ratio,
                is_scanned=extraction_res.is_scanned,
                topics=[],
                success=False,
                error_message=f"AI analysis failed: {str(e)}"
            )

