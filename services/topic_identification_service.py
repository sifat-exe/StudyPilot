"""
topic_identification_service.py
────────────────────────────────
Service-layer orchestrator for the Main Topic Identification feature.

This module sits between the UI (study_materials_page.py) and the raw
Gemini API wrapper (ai_provider.py).

Responsibilities:
  - Accept the cleaned extracted text from PDFExtractionService.
  - Delegate AI communication to GeminiProvider.
  - Return a clean TopicResult dataclass to the caller.
  - Handle errors gracefully and report them in the result object.

The UI should ONLY import TopicIdentificationService and TopicResult.
"""

from dataclasses import dataclass, field
from services.ai_provider import GeminiProvider


@dataclass
class TopicResult:
    """
    Structured result returned to the UI after topic identification.

    Attributes
    ----------
    topics : list[str]
        Ordered, deduplicated list of main academic topic strings.
        Empty if identification failed or no topics were found.
    success : bool
        True if the AI call completed without a fatal error.
    error_message : str
        Human-readable error description if success is False.
    topic_count : int
        Convenience property — number of topics found.
    """
    topics: list = field(default_factory=list)
    success: bool = True
    error_message: str = ""

    @property
    def topic_count(self) -> int:
        return len(self.topics)


class TopicIdentificationService:
    """
    Orchestrates the full topic identification pipeline.

    Usage (called from a background QThread in study_materials_page.py):

        service = TopicIdentificationService()
        result = service.identify_topics(extracted_text)

        if result.success:
            for topic in result.topics:
                print(topic)
        else:
            print(result.error_message)
    """

    def __init__(self):
        # Lazy-initialize GeminiProvider to catch import errors early.
        self._provider = None

    def _get_provider(self) -> GeminiProvider:
        """Creates the GeminiProvider on first use."""
        if self._provider is None:
            self._provider = GeminiProvider()
        return self._provider

    def identify_topics(self, extracted_text: str) -> TopicResult:
        """
        Identifies the main academic topics from the given extracted PDF text.

        Parameters
        ----------
        extracted_text : str
            Full cleaned text produced by PDFExtractionService.extract_text().
            This is the `extracted_text` field of PDFExtractionResult.

        Returns
        -------
        TopicResult
            Contains the topics list and success status.
            Always returns a TopicResult — never raises an exception to the caller.
        """
        # Guard: nothing to analyze
        if not extracted_text or not extracted_text.strip():
            return TopicResult(
                topics=[],
                success=False,
                error_message="No extracted text available for topic identification."
            )

        try:
            provider = self._get_provider()
            topics = provider.identify_topics_from_text(extracted_text)

            if not topics:
                return TopicResult(
                    topics=[],
                    success=True,     # The call succeeded but found nothing
                    error_message=""
                )

            return TopicResult(
                topics=topics,
                success=True,
                error_message=""
            )

        except RuntimeError as e:
            # Typically: SDK not installed or API key missing
            return TopicResult(
                topics=[],
                success=False,
                error_message=f"AI setup error: {str(e)}"
            )

        except Exception as e:
            # Network failures, quota errors, unexpected responses, etc.
            return TopicResult(
                topics=[],
                success=False,
                error_message=f"Topic identification failed: {str(e)}"
            )

