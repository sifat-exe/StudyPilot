import os

# config.py
# Application configuration

# Set to True to use dummy data without requiring a real database connection.
# Set to False when the real database is ready to be integrated.
USE_DUMMY_DATA = False

# ── Helper to load .env file manually if python-dotenv is not installed ───────
def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

# ── Gemini AI API Key ──────────────────────────────────────────────────────────
# Falls back to the hardcoded key when running as a bundled .exe (no .env available).
_FALLBACK_KEY = "AQ.Ab8RN6JGoi1kq_a9MiGb0ZknQkFCPyHCBwgNe02fXCTKu2IMGw"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or _FALLBACK_KEY

