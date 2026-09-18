import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # backend/app
REPO_ROOT = BASE_DIR.parents[1]  # grandhack/

DATA_DIR = Path(os.environ.get("CF_DATA_DIR", BASE_DIR / "data"))
SEED_FILE = DATA_DIR / "seed_graph.json"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("CF_GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT_S = float(os.environ.get("CF_GEMINI_TIMEOUT_S", "8"))

CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CF_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]

FRONTEND_DIR = Path(
    os.environ.get("CF_FRONTEND_DIR", REPO_ROOT / "frontend" / "out")
)

DEFAULT_WEEKS = 12
DEFAULT_WEEKLY_HOURS = 10
CACHE_TTL_S = int(os.environ.get("CF_CACHE_TTL_S", "3600"))