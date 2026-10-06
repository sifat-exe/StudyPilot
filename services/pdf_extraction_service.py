import os
import re
import gc
from dataclasses import dataclass
import pymupdf

# Try importing RapidOCR / pytesseract for OCR fallback
HAS_RAPID_OCR = False
try:
    from rapidocr_onnxruntime import RapidOCR
    import numpy as np
    HAS_RAPID_OCR = True
except ImportError:
    HAS_RAPID_OCR = False

HAS_PYTESSERACT = False
try:
    import pytesseract
    from PIL import Image
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False


@dataclass
class PDFExtractionResult:
    file_path: str
    file_name: str
    page_count: int = 0
    char_count: int = 0
    extracted_text: str = ""
    preview_text: str = ""
    extraction_method: str = "Native"  # "Native" or "OCR"
    meaningful_pages: int = 0
    meaningful_ratio: float = 0.0
    is_scanned: bool = False
    error_message: str = ""
    success: bool = True


class PDFExtractionService:
    """
    Modular PDF Text Extraction Service with Quality Evaluation and OCR Fallback.

    Pipeline:
    1. Native PyMuPDF text extraction.
    2. Meaningful-text quality evaluation per page and document-wide ratio.
    3. If native extraction is insufficient (scanned / image-only / page-numbers only):
       Automatically triggers page-by-page OCR fallback.
    4. Text cleaning and preview formatting.
    """

    # Configurable Threshold Constants
    MIN_MEANINGFUL_CHARS_PER_PAGE: int = 40   # Minimum meaningful chars for a page
    MIN_MEANINGFUL_PAGE_RATIO: float = 0.35    # 35% ratio threshold to trigger OCR
    PREVIEW_CHAR_LIMIT: int = 15000            # UI preview display limit

    def __init__(self, min_chars_per_page: int = None, min_page_ratio: float = None):
        if min_chars_per_page is not None:
            self.MIN_MEANINGFUL_CHARS_PER_PAGE = min_chars_per_page
        if min_page_ratio is not None:
            self.MIN_MEANINGFUL_PAGE_RATIO = min_page_ratio

        # Initialize OCR Engine if available
        self.rapid_ocr = None
        if HAS_RAPID_OCR:
            try:
                self.rapid_ocr = RapidOCR()
            except Exception as e:
                print(f"[PDFExtractionService] RapidOCR init notice: {e}")

    def extract_text(self, file_path: str, progress_callback=None) -> PDFExtractionResult:
        """
        Main extraction entry point.
        Attempts native extraction first, evaluates quality, and falls back to OCR if needed.
        """
        file_name = os.path.basename(file_path) if file_path else "Unknown"

        # 1. Validation: File Existence
        if not file_path or not os.path.exists(file_path):
            return PDFExtractionResult(
                file_path=file_path or "",
                file_name=file_name,
                success=False,
                error_message="The specified PDF file does not exist."
            )

        # 2. Validation: File Extension
        if not file_path.lower().endswith(".pdf"):
            return PDFExtractionResult(
                file_path=file_path,
                file_name=file_name,
                success=False,
                error_message="The selected file is not a PDF document."
            )

        doc = None
        try:
            doc = pymupdf.open(file_path)
            page_count = len(doc)

            if page_count == 0:
                return PDFExtractionResult(
                    file_path=file_path,
                    file_name=file_name,
                    page_count=0,
                    success=False,
                    error_message="The PDF file contains 0 pages."
                )

            # --- STAGE 1: NATIVE EXTRACTION & EVALUATION ---
            native_page_texts = []
            meaningful_page_count = 0

            for page_num in range(page_count):
                page = doc[page_num]
                raw_text = page.get_text("text") or ""
                cleaned_text = self._clean_text(raw_text)

                meaningful_chars = self._count_meaningful_chars(cleaned_text)
                is_meaningful = meaningful_chars >= self.MIN_MEANINGFUL_CHARS_PER_PAGE

                if is_meaningful:
                    meaningful_page_count += 1

                native_page_texts.append(cleaned_text)

            meaningful_ratio = round(meaningful_page_count / page_count, 3)

            # Evaluate Native Extraction Sufficiency
            is_native_sufficient = (meaningful_ratio >= self.MIN_MEANINGFUL_PAGE_RATIO) and (meaningful_page_count > 0)

            if is_native_sufficient:
                # --- NATIVE EXTRACTION SUFFICIENT ---
                full_text = self._format_page_texts(native_page_texts)
                char_count = len(full_text)
                preview_text = self._build_preview(full_text, char_count)

                return PDFExtractionResult(
                    file_path=file_path,
                    file_name=file_name,
                    page_count=page_count,
                    char_count=char_count,
                    extracted_text=full_text,
                    preview_text=preview_text,
                    extraction_method="Native",
                    meaningful_pages=meaningful_page_count,
                    meaningful_ratio=meaningful_ratio,
                    is_scanned=False,
                    success=True
                )

            # --- STAGE 2: OCR FALLBACK ---
            print(f"[PDFExtractionService] Native extraction insufficient (ratio: {meaningful_ratio*100:.1f}%). Triggering OCR fallback...")
            
            if not self._is_ocr_available():
                # Report clear missing OCR dependency notice
                full_text = self._format_page_texts(native_page_texts)
                char_count = len(full_text)
                preview_text = self._build_preview(full_text, char_count)

                return PDFExtractionResult(
                    file_path=file_path,
                    file_name=file_name,
                    page_count=page_count,
                    char_count=char_count,
                    extracted_text=full_text,
                    preview_text=preview_text,
                    extraction_method="Native (Insufficient)",
                    meaningful_pages=meaningful_page_count,
                    meaningful_ratio=meaningful_ratio,
                    is_scanned=True,
                    success=False,
                    error_message="Native text extraction was insufficient, and no OCR engine (RapidOCR / Tesseract) was available to process scanned pages."
                )

            # Perform Page-by-Page OCR
            ocr_page_texts = []
            ocr_meaningful_count = 0

            for page_num in range(page_count):
                if progress_callback:
                    progress_callback(page_num + 1, page_count)

                page = doc[page_num]
                page_text = self._ocr_page(page, page_num + 1)
                cleaned_text = self._clean_text(page_text)

                meaningful_chars = self._count_meaningful_chars(cleaned_text)
                if meaningful_chars >= self.MIN_MEANINGFUL_CHARS_PER_PAGE:
                    ocr_meaningful_count += 1

                ocr_page_texts.append(cleaned_text)

                # Garbage collection per page to keep memory usage low
                gc.collect()

            ocr_ratio = round(ocr_meaningful_count / page_count, 3)
            full_ocr_text = self._format_page_texts(ocr_page_texts)
            char_count = len(full_ocr_text)
            preview_text = self._build_preview(full_ocr_text, char_count)

            return PDFExtractionResult(
                file_path=file_path,
                file_name=file_name,
                page_count=page_count,
                char_count=char_count,
                extracted_text=full_ocr_text,
                preview_text=preview_text,
                extraction_method="OCR",
                meaningful_pages=ocr_meaningful_count,
                meaningful_ratio=ocr_ratio,
                is_scanned=True,
                success=True
            )

        except Exception as e:
            return PDFExtractionResult(
                file_path=file_path,
                file_name=file_name,
                success=False,
                error_message=f"An error occurred during extraction: {str(e)}"
            )
        finally:
            if doc:
                try:
                    doc.close()
                except Exception:
                    pass

    def _is_ocr_available(self) -> bool:
        """Checks if RapidOCR or pytesseract with tesseract binary is ready."""
        if self.rapid_ocr is not None:
            return True
        if HAS_PYTESSERACT:
            try:
                pytesseract.get_tesseract_version()
                return True
            except Exception:
                return False
        return False

    def _ocr_page(self, page, page_number: int) -> str:
        """
        Renders a single PyMuPDF page to pixmap image and runs OCR.
        Prevents memory leaks by freeing pixmap immediately.
        """
        try:
            pix = page.get_pixmap(dpi=150)
            
            # Method 1: RapidOCR (ONNX runtime)
            if self.rapid_ocr is not None:
                img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                if pix.n == 4:  # RGBA to RGB
                    img_np = img_np[:, :, :3]
                
                res, _ = self.rapid_ocr(img_np)
                pix = None  # Release pixmap
                
                if res:
                    lines = [item[1] for item in res if item and len(item) > 1 and item[1]]
                    return "\n".join(lines)
                return ""

            # Method 2: Pytesseract Fallback
            elif HAS_PYTESSERACT:
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                pix = None
                text = pytesseract.image_to_string(img)
                return text or ""

        except Exception as e:
            print(f"[PDFExtractionService] OCR warning on page {page_number}: {e}")
            return ""

        return ""

    def _count_meaningful_chars(self, text: str) -> int:
        """
        Counts meaningful alphabetic/alphanumeric characters,
        filtering out page-number-only lines and whitespace.
        """
        if not text:
            return 0

        # Remove standalone page-number-only lines e.g. "1", "2", "Page 3"
        filtered_lines = []
        for line in text.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            if re.match(r"^(?:Page\s*)?\d+$", line_str, re.IGNORECASE):
                continue
            filtered_lines.append(line_str)

        combined = " ".join(filtered_lines)
        # Count words / alphanumeric characters
        meaningful_chars = len(re.sub(r"[^\w]", "", combined))
        return meaningful_chars

    def _clean_text(self, text: str) -> str:
        """
        Applies academic text cleaning:
        - Normalizes line breaks
        - Removes excessive horizontal spaces
        - Removes excessive blank lines
        - Removes isolated page-number-only lines
        - Preserves headings, paragraphs, math notation
        """
        if not text:
            return ""

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Remove isolated page number lines
        text = re.sub(r"(?m)^\s*(?:Page\s*)?\d+\s*$", "", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _format_page_texts(self, page_texts: list) -> str:
        """
        Combines page texts while preserving page boundaries:
        --- Page 1 ---
        text...
        """
        formatted = []
        for idx, page_text in enumerate(page_texts, start=1):
            if page_text.strip():
                formatted.append(f"--- Page {idx} ---\n{page_text}")
        return "\n\n".join(formatted).strip()

    def _build_preview(self, full_text: str, char_count: int) -> str:
        """Builds preview string up to PREVIEW_CHAR_LIMIT."""
        if not full_text:
            return "No text extracted."
        preview = full_text[:self.PREVIEW_CHAR_LIMIT]
        if char_count > self.PREVIEW_CHAR_LIMIT:
            preview += f"\n\n--- [Preview truncated at {self.PREVIEW_CHAR_LIMIT:,} characters. Total characters: {char_count:,}] ---"
        return preview
