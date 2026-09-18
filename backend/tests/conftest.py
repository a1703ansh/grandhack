import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT / "app"))

from app import config  # noqa: E402
from app.graph.graph import KnowledgeGraph  # noqa: E402


@pytest.fixture(scope="session")
def seed_path() -> Path:
    if not config.SEED_FILE.exists():
        from scripts.build_seed import main as build_seed_main

        build_seed_main()
    return config.SEED_FILE


@pytest.fixture(scope="session")
def graph(seed_path: Path) -> KnowledgeGraph:
    return KnowledgeGraph.from_file(seed_path)