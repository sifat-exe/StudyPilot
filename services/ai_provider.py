"""
ai_provider.py
──────────────
Thin Gemini API wrapper for the StudyPilot service layer.

Responsibilities:
  - Build the AI prompt for topic identification.
  - Send text to the Gemini API and receive the response.
  - Parse the JSON response into a plain Python list.
  - Chunk long texts so no single request exceeds the practical limit.
  - Deduplicate near-identical topics across chunks.

The UI layer must NEVER import this file directly.
All AI calls go through topic_identification_service.py.
"""

import re
import json
from config import GEMINI_API_KEY

# ── SDK Import ─────────────────────────────────────────────────────────────────
# We use the modern google-genai SDK (>= 2.3.0).
# Install with:  pip install -U google-genai
try:
    from google import genai
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


# ── Configuration Constants ────────────────────────────────────────────────────
MODEL_NAME = "gemini-3.8-flash"          # Fast, 1M-token context model
CHUNK_SIZE = 12000                        # Max characters per API chunk
MAX_TOPICS_PER_CHUNK = 15                # Guard against runaway responses
SIMILARITY_THRESHOLD = 0.75              # Fuzzy-match ratio for deduplication


class GeminiProvider:
    """
    Handles all direct communication with the Gemini API.

    Usage (by topic_identification_service.py only):
        provider = GeminiProvider()
        topics = provider.identify_topics_from_text(extracted_text)
        # Returns: list of topic strings, e.g. ["DC Generator", "Faraday's Law"]
    """

    def __init__(self):
        if not _SDK_AVAILABLE:
            raise RuntimeError(
                "google-genai package is not installed.\n"
                "Run:  pip install -U google-genai"
            )
        # Create the Gemini client once; reuse it for all calls.
        self._client = genai.Client(api_key=GEMINI_API_KEY)

    # ── Public Method ──────────────────────────────────────────────────────────

    def identify_topics_from_text(self, text: str) -> list:
        """
        Given cleaned PDF text, returns a deduplicated list of main topic strings.

        Steps:
          1. Split the text into manageable chunks.
          2. Ask Gemini to identify topics from each chunk.
          3. Merge and deduplicate all topics across chunks.

        Parameters
        ----------
        text : str
            Full cleaned text produced by PDFExtractionService.

        Returns
        -------
        list[str]
            Deduplicated list of academic topic strings.
            Returns an empty list if nothing meaningful was found.

        Raises
        ------
        RuntimeError
            If the Gemini API call fails for all chunks.
        """
        if not text or not text.strip():
            return []

        chunks = self._split_into_chunks(text, CHUNK_SIZE)
        all_topics = []

        for chunk_index, chunk in enumerate(chunks, start=1):
            try:
                chunk_topics = self._call_gemini_for_topics(chunk, chunk_index, len(chunks))
                all_topics.extend(chunk_topics)
            except Exception as e:
                # If one chunk fails, log and continue with the rest.
                print(f"[GeminiProvider] Warning: chunk {chunk_index} failed — {e}")
                continue

        deduplicated = self._deduplicate_topics(all_topics)
        return deduplicated

    # ── Private Helpers ────────────────────────────────────────────────────────

    def _call_gemini_for_topics(self, text_chunk: str, chunk_index: int, total_chunks: int) -> list:
        """
        Sends one chunk of text to Gemini and parses the returned JSON topics list.
        """
        prompt = self._build_prompt(text_chunk, chunk_index, total_chunks)

        response = self._client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
            store=False,     # We do not need conversation history here.
        )

        raw_text = response.output_text or ""
        return self._parse_topics_json(raw_text)

    def _build_prompt(self, text_chunk: str, chunk_index: int, total_chunks: int) -> str:
        """
        Constructs the academic topic extraction prompt.

        The prompt instructs Gemini to:
          - Extract ONLY major academic/technical topics.
          - Return ONLY a JSON object with a "topics" array of strings.
          - Avoid vague or overly generic terms.
        """
        chunk_note = ""
        if total_chunks > 1:
            chunk_note = f" (this is part {chunk_index} of {total_chunks} of a larger document)"

        prompt = f"""You are an academic topic extractor for a university study assistant app.

Analyze the following PDF text{chunk_note} and identify all major academic or technical topics it covers.

RULES:
1. Return ONLY a JSON object in this exact format:
   {{"topics": ["Topic A", "Topic B", "Topic C"]}}
2. List only specific, meaningful academic/technical topics (e.g., "DC Generator", "Faraday's Law of Induction", "Armature Reaction").
3. Do NOT include vague phrases like "Introduction", "Summary", "Overview", or page numbers.
4. Do NOT include author names, university names, or course codes.
5. Limit your response to at most {MAX_TOPICS_PER_CHUNK} topics.
6. If the text contains no meaningful academic topics, return: {{"topics": []}}
7. Do NOT include any explanation, markdown, or text outside the JSON.

PDF TEXT:
{text_chunk}"""

        return prompt

    def _parse_topics_json(self, raw_response: str) -> list:
        """
        Parses Gemini's JSON response and extracts the topics list.

        Handles cases where Gemini wraps the JSON in markdown code fences.
        """
        if not raw_response:
            return []

        # Strip markdown code fences if Gemini wraps the JSON
        cleaned = raw_response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            topics = data.get("topics", [])
            # Ensure it is a list of strings
            if isinstance(topics, list):
                return [str(t).strip() for t in topics if t and str(t).strip()]
        except json.JSONDecodeError:
            # Try to extract a JSON object from anywhere in the response
            match = re.search(r'\{"topics"\s*:\s*\[.*?\]\s*\}', cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    topics = data.get("topics", [])
                    return [str(t).strip() for t in topics if t and str(t).strip()]
                except json.JSONDecodeError:
                    pass

        print(f"[GeminiProvider] Warning: could not parse topics JSON. Raw response:\n{raw_response[:300]}")
        return []

    def _split_into_chunks(self, text: str, chunk_size: int) -> list:
        """
        Splits text into chunks of at most `chunk_size` characters.
        Tries to split at paragraph boundaries (double newlines) to preserve context.
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit, save the current chunk
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk = (current_chunk + "\n\n" + paragraph).strip() if current_chunk else paragraph

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _deduplicate_topics(self, topics: list) -> list:
        """
        Removes near-duplicate topics from the merged list.

        Strategy:
          1. Normalize each topic (lowercase, remove punctuation).
          2. Compare each new topic against already-kept topics using
             character overlap (Jaccard-like word set similarity).
          3. Only keep a topic if it is sufficiently different from all
             already-kept topics.
        """
        if not topics:
            return []

        kept = []
        kept_normalized = []

        for topic in topics:
            norm = self._normalize_topic(topic)
            if not norm:
                continue

            is_duplicate = False
            for existing_norm in kept_normalized:
                if self._topics_are_similar(norm, existing_norm, SIMILARITY_THRESHOLD):
                    is_duplicate = True
                    break

            if not is_duplicate:
                kept.append(topic)
                kept_normalized.append(norm)

        return kept

    def _normalize_topic(self, topic: str) -> str:
        """Lowercases the topic and removes punctuation for comparison."""
        topic = topic.lower()
        topic = re.sub(r"[^\w\s]", "", topic)   # Remove punctuation
        topic = re.sub(r"\s+", " ", topic)       # Collapse spaces
        return topic.strip()

    def _topics_are_similar(self, a: str, b: str, threshold: float) -> bool:
        """
        Returns True if two normalized topic strings are similar enough
        to be considered duplicates.

        Uses word-set Jaccard similarity:
            similarity = |intersection| / |union|
        """
        words_a = set(a.split())
        words_b = set(b.split())

        if not words_a or not words_b:
            return False

        intersection = words_a & words_b
        union = words_a | words_b
        similarity = len(intersection) / len(union)

        return similarity >= threshold

