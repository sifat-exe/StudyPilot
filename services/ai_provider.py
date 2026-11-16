import re
import json
import time
from config import GEMINI_API_KEY

try:
    from google import genai
    from google.genai import types
    _SDK_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    _SDK_AVAILABLE = False


# Working models for this API key. gemini-3.8-flash currently 504s/hangs.
MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]

MAX_SOURCE_CHARS = 6000
MAX_TOPICS = 8
HTTP_TIMEOUT_MS = 45000
MAX_OUTPUT_TOKENS = 4096


def is_valid_summary_text(text: str) -> bool:
    """Reject empty text and obvious API/error messages, not academic content."""
    if not text or not text.strip():
        return False
    lower = text.lower().strip()
    if len(lower) < 20:
        return False
    invalid_phrases = [
        "service_unavailable",
        "resource_exhausted",
        "rate limit",
        "daily limit",
        "service limit",
        "limit reached",
        "encountered an error",
        "failed to generate",
        "try again later",
        "summary unavailable",
        "ai analysis failed",
        "gemini api error",
        "could not parse ai summary",
        "no response received from ai",
        "temporarily unavailable",
        "invalid api key",
        "deadline_exceeded",
        "deadline expired",
    ]
    return not any(phrase in lower for phrase in invalid_phrases)


class GeminiProvider:
    """Handles communication with the Gemini API for PDF topic summaries."""

    def __init__(self):
        if not _SDK_AVAILABLE:
            raise RuntimeError(
                "google-genai package is not installed.\n"
                "Run:  pip install -U google-genai"
            )
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add it to StudyPilot/.env"
            )
        self._client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=HTTP_TIMEOUT_MS),
        )
        self._working_model = None

    def identify_topics_from_text(self, text: str) -> list:
        if not text or not text.strip():
            return []
        result = self.analyze_document_from_text(text)
        return [item["topic"] for item in result if item.get("topic")]

    def generate_summaries_for_topics(self, text: str, topics: list) -> list:
        if not text or not text.strip() or not topics:
            return []
        excerpt = self._prepare_excerpt(text)
        prompt = self._build_summary_prompt(excerpt, topics[:MAX_TOPICS])
        raw = self._generate_json_text(prompt)
        parsed = self._parse_summaries_json(raw, topics[:MAX_TOPICS])
        if parsed:
            return parsed
        return self.analyze_document_from_text(text)

    def analyze_document_from_text(self, text: str) -> list:
        """
        One-shot topic identification + summaries from a short PDF excerpt.
        Uses model knowledge to fill gaps when the excerpt is incomplete.
        """
        if not text or not text.strip():
            return []

        excerpt = self._prepare_excerpt(text)
        last_error = None

        for excerpt_size in (len(excerpt), min(2500, len(excerpt)), min(1200, len(excerpt))):
            clipped = excerpt[:excerpt_size]
            prompt = self._build_combined_prompt(clipped)
            try:
                raw = self._generate_json_text(prompt)
                parsed = self._parse_summaries_json(raw, expected_topics=None)
                if parsed:
                    return parsed[:MAX_TOPICS]
            except Exception as e:
                last_error = e
                print(f"[GeminiProvider] Combined analysis failed ({excerpt_size} chars): {e}")
                continue

        fallback = self._local_fallback_summaries(text)
        if fallback:
            return fallback
        if last_error:
            raise last_error
        return []

    def _prepare_excerpt(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", (text or "")).strip()
        if len(cleaned) <= MAX_SOURCE_CHARS:
            return cleaned
        head = cleaned[: int(MAX_SOURCE_CHARS * 0.75)]
        tail = cleaned[-int(MAX_SOURCE_CHARS * 0.25):]
        return head + "\n...\n" + tail

    def _build_combined_prompt(self, excerpt: str) -> str:
        return f"""You are a university study assistant creating exam revision notes.

You receive only a SHORT excerpt from a PDF, not the full document.
1. Identify 3 to {MAX_TOPICS} main academic topics from the excerpt.
2. For each topic write a clear 1-2 paragraph academic summary and 3 to 6 revision key points.
3. Prefer facts from the excerpt. If the excerpt is incomplete, finish the explanation using well-established academic knowledge for those topics. Do not refuse and do not say the text is insufficient.
4. Return ONLY JSON in this shape:
{{
  "summaries": [
    {{
      "topic": "Topic Title",
      "summary": "Academic paragraph(s)...",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ]
}}

PDF EXCERPT:
{excerpt}"""

    def _build_summary_prompt(self, text_context: str, topics: list) -> str:
        topics_formatted = "\n".join([f"- {t}" for t in topics])
        return f"""You are a university professor and academic summarizer.

Write a revision summary for EACH identified topic.
You only have a short PDF excerpt. Prefer the excerpt, but use standard academic knowledge to complete any gaps so every topic has a useful summary. Do not refuse.

IDENTIFIED TOPICS:
{topics_formatted}

Return ONLY JSON:
{{
  "summaries": [
    {{
      "topic": "Exact Topic Title",
      "summary": "Academic explanation paragraph(s)...",
      "key_points": ["Main point 1", "Main point 2", "Main point 3"]
    }}
  ]
}}

PDF EXCERPT:
{text_context}"""

    def _generate_json_text(self, prompt: str) -> str:
        models = []
        if self._working_model:
            models.append(self._working_model)
        for name in MODEL_CANDIDATES:
            if name not in models:
                models.append(name)

        last_error = None
        for model in models:
            try:
                text = self._call_generate_content(model, prompt)
                if text and text.strip():
                    self._working_model = model
                    return text
            except Exception as e:
                last_error = e
                err = str(e).lower()
                print(f"[GeminiProvider] model {model} failed: {e}")
                if any(term in err for term in ["quota", "resource_exhausted", "429", "rate limit"]):
                    raise RuntimeError("AI service limit reached. Please try again later.") from e
                if any(term in err for term in ["invalid api key", "permission_denied", "401", "403"]):
                    raise RuntimeError("AI configuration or authentication error. Please check your API key.") from e
                continue

        if last_error:
            raise RuntimeError(f"AI service error: {last_error}") from last_error
        raise RuntimeError("No response received from AI.")

    def _call_generate_content(self, model: str, prompt: str) -> str:
        max_attempts = 2
        delays = [1.5, 3]
        config = types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                text = (getattr(response, "text", None) or "").strip()
                if text:
                    return text
                raise RuntimeError("Received empty response from AI service.")
            except Exception as e:
                err = str(e).lower()
                retryable = any(
                    term in err
                    for term in ["503", "unavailable", "overload", "deadline", "504", "timed out", "timeout", "empty response"]
                )
                if retryable and attempt < max_attempts:
                    time.sleep(delays[attempt - 1])
                    continue
                raise

    def _parse_summaries_json(self, raw_response: str, expected_topics: list | None) -> list:
        if not raw_response or not raw_response.strip():
            return []

        cleaned = raw_response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        parsed_items = []
        data = None
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    match_list = re.search(r"\[.*\]", cleaned, re.DOTALL)
                    if match_list:
                        try:
                            data = json.loads(match_list.group())
                        except json.JSONDecodeError:
                            data = None

        if isinstance(data, list):
            parsed_items = data
        elif isinstance(data, dict):
            parsed_items = data.get("summaries") or data.get("topics") or []
            if isinstance(parsed_items, dict):
                parsed_items = [parsed_items]

        if not isinstance(parsed_items, list):
            return []

        normalized = []
        for item in parsed_items:
            if isinstance(item, str):
                continue
            if not isinstance(item, dict):
                continue
            topic = str(item.get("topic") or item.get("title") or "").strip()
            summary = str(item.get("summary") or item.get("text") or "").strip()
            raw_kp = item.get("key_points") or item.get("keyPoints") or item.get("points") or []
            if not isinstance(raw_kp, list):
                raw_kp = []
            key_points = [str(k).strip() for k in raw_kp if k and str(k).strip()]
            if topic and is_valid_summary_text(summary):
                normalized.append({
                    "topic": topic,
                    "summary": summary,
                    "key_points": key_points,
                })

        if not normalized:
            return []

        if not expected_topics:
            return normalized

        parsed_map = {self._normalize_topic(item["topic"]): item for item in normalized}
        results = []
        for orig_topic in expected_topics:
            norm_topic = self._normalize_topic(orig_topic)
            matched = parsed_map.get(norm_topic)
            if not matched:
                for p_norm, p_dict in parsed_map.items():
                    if self._topics_are_similar(norm_topic, p_norm, 0.5):
                        matched = p_dict
                        break
            if matched:
                results.append({
                    "topic": orig_topic,
                    "summary": matched["summary"],
                    "key_points": matched["key_points"],
                })
            else:
                # Keep AI-invented extra topics only after mapping expected ones.
                continue

        if not results:
            return normalized
        return results

    def _local_fallback_summaries(self, text: str) -> list:
        excerpt = (text or "").strip()
        if not excerpt:
            return []
        snippet = excerpt[:900].strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", snippet) if s.strip()]
        key_points = sentences[:5] or [snippet[:180]]
        return [{
            "topic": "Document Overview",
            "summary": snippet if len(snippet) > 40 else (
                "The PDF excerpt was too short for a detailed AI summary. "
                "This overview is based on the extracted text that was available."
            ),
            "key_points": key_points,
        }]

    def _normalize_topic(self, topic: str) -> str:
        topic = topic.lower()
        topic = re.sub(r"[^\w\s]", "", topic)
        topic = re.sub(r"\s+", " ", topic)
        return topic.strip()

    def _topics_are_similar(self, a: str, b: str, threshold: float) -> bool:
        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a or not words_b:
            return False
        similarity = len(words_a & words_b) / len(words_a | words_b)
        return similarity >= threshold
