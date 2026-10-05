"""
pdf_analysis_models.py
──────────────────────
Structured, database-ready data models for the StudyPilot PDF Analysis pipeline.

These dataclasses represent PURE DATA and must not contain any UI elements,
PySide6 widgets, or UI-specific logic.

Future Database Mapping:
  - PDFAnalysisResult -> PDFDocument table
  - TopicSummary      -> Topic & TopicSummary tables
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TopicSummary:
    """
    Represents an identified academic topic along with its generated summary and key points.

    Attributes
    ----------
    title : str
        The main academic topic title (e.g., "Working Principle of DC Generator").
    summary : str
        Concise, academic explanation based strictly on the PDF text.
    key_points : list[str]
        List of bullet key points highlighting important concepts/formulas.
    order_index : int
        1-based position of the topic in the document analysis sequence.
    """
    title: str
    summary: str
    key_points: List[str] = field(default_factory=list)
    order_index: int = 1


@dataclass
class PDFAnalysisResult:
    """
    Complete analysis result for a PDF document, including metadata, extracted text,
    and structured topic summaries.

    Attributes
    ----------
    file_path : str
        Absolute local path to the PDF file.
    file_name : str
        Base filename (e.g., "DC Generator.pdf").
    page_count : int
        Total number of pages in the PDF.
    extraction_method : str
        Method used for extraction: "Native" or "OCR".
    extracted_text : str
        Full cleaned text extracted from the PDF document.
    meaningful_pages : int
        Count of pages containing sufficient meaningful text.
    meaningful_ratio : float
        Ratio of meaningful pages to total page count (0.0 to 1.0).
    is_scanned : bool
        True if native text was insufficient and OCR fallback was required.
    topics : list[TopicSummary]
        List of TopicSummary objects for all identified topics.
    success : bool
        True if analysis succeeded without critical errors.
    error_message : str
        Error description if success is False.
    """
    file_path: str
    file_name: str
    page_count: int = 0
    extraction_method: str = "Native"
    extracted_text: str = ""
    meaningful_pages: int = 0
    meaningful_ratio: float = 0.0
    is_scanned: bool = False
    topics: List[TopicSummary] = field(default_factory=list)
    success: bool = True
    error_message: str = ""

    @property
    def topic_count(self) -> int:
        return len(self.topics)

    @property
    def char_count(self) -> int:
        return len(self.extracted_text)

