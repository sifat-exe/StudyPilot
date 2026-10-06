import re
import json
import time
from config import GEMINI_API_KEY

# ── SDK Import ─────────────────────────────────────────────────────────────────
try:
    from google import genai
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


# ── Configuration Constants ────────────────────────────────────────────────────
MODEL_NAME = "gemini-3.8-flash"          # Primary fast 1M-context model
CHUNK_SIZE = 12000                        # Max characters per API chunk
MAX_TOPICS_PER_CHUNK = 15                # Guard against runaway responses
SIMILARITY_THRESHOLD = 0.75              # Fuzzy-match ratio for deduplication


def is_valid_summary_text(text: str) -> bool:
    """
    Validates that a summary string is usable and not an exception, error, or 503/429 message.
    """
    if not text or not text.strip():
        return False
    lower = text.lower().strip()
    invalid_patterns = [
        "service_unavailable",
        "503",
        "429",
        "quota",
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
        "authentication"
    ]
    for pattern in invalid_patterns:
        if pattern in lower:
            return False
    return True


class GeminiProvider:
    """
    Handles all direct communication with the Gemini API.
    """

    def __init__(self):
        if not _SDK_AVAILABLE:
            raise RuntimeError(
                "google-genai package is not installed.\n"
                "Run:  pip install -U google-genai"
            )
        self._client = genai.Client(api_key=GEMINI_API_KEY)

    # ── Public Methods ─────────────────────────────────────────────────────────

    def identify_topics_from_text(self, text: str) -> list:
        """
        Given cleaned PDF text, returns a deduplicated list of main topic strings.
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
                print(f"[GeminiProvider] Warning: chunk {chunk_index} failed — {e}")
                continue

        deduplicated = self._deduplicate_topics(all_topics)
        return deduplicated

    def generate_summaries_for_topics(self, text: str, topics: list) -> list:
        """
        Generates topic-wise academic summaries and main/key points for a list of
        already-identified topics using the extracted PDF text.
        """
        if not text or not text.strip() or not topics:
            return []

        text_context = text[:30000]

        try:
            return self._call_gemini_for_summaries(text_context, topics)
        except Exception as e:
            print(f"[GeminiProvider] Summary generation error: {e}")
            raise e

    # ── Private Helpers ────────────────────────────────────────────────────────

    def _call_interactions_with_retry(self, prompt: str):
        """
        Executes client.interactions.create with targeted exponential backoff retries for 503 transient errors,
        and immediate fail-fast handling for quota/rate limits or authentication errors.
        """
        max_attempts = 3
        backoff_delays = [2, 4, 8]  # Attempt 1 -> wait 2s, Attempt 2 -> wait 4s, Attempt 3 -> wait 8s

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._client.interactions.create(
                    model=MODEL_NAME,
                    input=prompt,
                    store=False,
                )
                if not response or not response.output_text or not response.output_text.strip():
                    if attempt < max_attempts:
                        time.sleep(backoff_delays[attempt - 1])
                        continue
                    raise RuntimeError("Received empty response from AI service.")
                return response
            except Exception as e:
                err_str = str(e).lower()
                print(f"[GeminiProvider] API Call attempt {attempt}/{max_attempts} error: {e}")

                # 1. Quota / Rate Limit (429, RESOURCE_EXHAUSTED): Fail fast immediately
                if any(term in err_str for term in ["quota", "resource_exhausted", "429", "rate limit", "requests per minute", "token limit"]):
                    raise RuntimeError("AI service limit reached. Please try again later.") from e

                # 2. Authentication / Permission / Invalid Key / Bad Request (401, 403, 400): Fail fast immediately
                if any(term in err_str for term in ["401", "403", "400", "invalid api key", "permission_denied", "authentication"]):
                    raise RuntimeError("AI configuration or authentication error. Please check your API key.") from e

                # 3. 503 / High Demand / Service Unavailable: Retry with exponential backoff (2s, 4s, 8s)
                if any(term in err_str for term in ["503", "unavailable", "service_unavailable", "high demand", "overload", "temporarily unavailable"]):
                    if attempt < max_attempts:
                        delay = backoff_delays[attempt - 1]
                        print(f"[GeminiProvider] 503 Service Unavailable / High demand detected. Retrying in {delay}s (Attempt {attempt}/{max_attempts})...")
                        time.sleep(delay)
                        continue
                    else:
                        raise RuntimeError("Summary generation is temporarily unavailable. Please try again.") from e

                # Other unexpected errors
                if attempt < max_attempts:
                    time.sleep(backoff_delays[attempt - 1])
                    continue
                raise RuntimeError(f"AI service error: {str(e)}") from e

    def _call_gemini_for_summaries(self, text_context: str, topics: list) -> list:
        """
        Sends topics and PDF text context to Gemini to generate topic-wise summaries.
        """
        prompt = self._build_summary_prompt(text_context, topics)
        response = self._call_interactions_with_retry(prompt)
        raw_text = response.output_text or ""
        return self._parse_summaries_json(raw_text, topics)

    def _build_summary_prompt(self, text_context: str, topics: list) -> str:
        """
        Constructs the academic topic summary + main points prompt.
        """
        topics_formatted = "\n".join([f"- {t}" for t in topics])

        prompt = f"""You are a university professor and academic summarizer.

Analyze the provided PDF text and generate a clear, informative academic summary and main points for EACH of the following identified topics.

IDENTIFIED TOPICS:
{topics_formatted}

RULES:
1. For EACH topic, provide:
   - "summary": A clear, informative 1-2 paragraph university-level academic summary explaining the topic based ONLY on information supported by the PDF text. Include important definitions, concepts, principles, equations, or mechanisms present in the PDF text.
   - "key_points": A list of approximately 3 to 7 concise, important main points/key facts for that topic mentioned in the PDF text. Each point must represent an important concept or fact and be easy to revise. Do NOT force exactly 5 points for every topic.
2. Return ONLY a JSON object in this exact format:
{{
  "summaries": [
    {{
      "topic": "Exact Topic Title",
      "summary": "Academic explanation paragraph(s)...",
      "key_points": [
        "Main point 1...",
        "Main point 2...",
        "Main point 3..."
      ]
    }}
  ]
}}
3. Stay strictly focused on each topic using ONLY facts supported by the PDF text.
4. Do NOT invent information or bring in outside unrelated knowledge.
5. Preserve technical terminology from the source material.
6. Do NOT wrap in explanation or extra text outside the JSON object.

PDF TEXT:
{text_context}"""

        return prompt

    def _parse_summaries_json(self, raw_response: str, expected_topics: list) -> list:
        """
        Parses Gemini's JSON summary response and aligns it with expected topics.
        Omits unreturned/failed topics so that error text is never produced.
        """
        if not raw_response or not raw_response.strip():
            raise RuntimeError("Summary generation is temporarily unavailable. Please try again.")

        cleaned = raw_response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        parsed_items = []
        try:
            data = json.loads(cleaned)
            parsed_items = data.get("summaries", [])
        except json.JSONDecodeError:
            match = re.search(r'\{"summaries"\s*:\s*\[.*?\]\s*\}', cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    parsed_items = data.get("summaries", [])
                except json.JSONDecodeError:
                    pass

        if not parsed_items or not isinstance(parsed_items, list):
            raise RuntimeError("Summary generation is temporarily unavailable. Please try again.")

        parsed_map = {}
        for item in parsed_items:
            if isinstance(item, dict) and "topic" in item:
                norm_title = self._normalize_topic(str(item["topic"]))
                parsed_map[norm_title] = item

        results = []
        for orig_topic in expected_topics:
            norm_topic = self._normalize_topic(orig_topic)
            matched = parsed_map.get(norm_topic)

            if not matched:
                for p_norm, p_dict in parsed_map.items():
                    if self._topics_are_similar(norm_topic, p_norm, 0.6):
                        matched = p_dict
                        break

            if matched:
                summary_text = str(matched.get("summary", "")).strip()
                if summary_text and is_valid_summary_text(summary_text):
                    raw_kp = matched.get("key_points", [])
                    kp_list = [str(k).strip() for k in raw_kp if k and str(k).strip()] if isinstance(raw_kp, list) else []
                    results.append({
                        "topic": orig_topic,
                        "summary": summary_text,
                        "key_points": kp_list
                    })

        return results

    def _call_gemini_for_topics(self, text_chunk: str, chunk_index: int, total_chunks: int) -> list:
        """
        Sends one chunk of text to Gemini and parses the returned JSON topics list.
        """
        prompt = self._build_prompt(text_chunk, chunk_index, total_chunks)
        response = self._call_interactions_with_retry(prompt)
        raw_text = response.output_text or ""
        return self._parse_topics_json(raw_text)

    def _build_prompt(self, text_chunk: str, chunk_index: int, total_chunks: int) -> str:
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
        if not raw_response:
            return []

        cleaned = raw_response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            topics = data.get("topics", [])
            if isinstance(topics, list):
                return [str(t).strip() for t in topics if t and str(t).strip()]
        except json.JSONDecodeError:
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
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for paragraph in paragraphs:
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk = (current_chunk + "\n\n" + paragraph).strip() if current_chunk else paragraph

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _deduplicate_topics(self, topics: list) -> list:
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
        topic = topic.lower()
        topic = re.sub(r"[^\w\s]", "", topic)
        topic = re.sub(r"\s+", " ", topic)
        return topic.strip()

    def _topics_are_similar(self, a: str, b: str, threshold: float) -> bool:
        words_a = set(a.split())
        words_b = set(b.split())

        if not words_a or not words_b:
            return False

        intersection = words_a & words_b
        union = words_a | words_b
        similarity = len(intersection) / len(union)

        return similarity >= threshold
