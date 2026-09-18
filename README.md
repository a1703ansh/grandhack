# Credential-Free Learning Path Finder

Turn a goal and a starting level into an **ordered, week-by-week roadmap** of
free courses — with a prerequisite graph, a "why this order" explanation for
every stage, and Markdown / calendar / print exports.

**Demo query:** *"I know basic Python. I want to master Deep Learning in 12
weeks."* → the engine resolves the goal, skips the Python foundations you
already know, walks the prerequisite graph, and produces a sequenced plan
(e.g. Python data tooling → calculus → probability & statistics → linear
algebra → machine learning → neural networks → deep learning).

It works **fully offline** from a curated seed graph. If a `GEMINI_API_KEY` is
present, one batched LLM call enriches the stage narratives; without it,
template narratives are used and everything still works.

---

## How it works

```
goal + level + time budget
        │
        ▼
 topic resolution (alias / word-boundary match)
        │
        ▼
 prerequisite closure  ──►  drop already-known topics
        │                    drop ancestors of known topics
        ▼
 topological order  ──►  group into stages  ──►  allocate weeks
        │
        ▼
 rank free courses per topic (TF-IDF keyword, optional embeddings)
        │
        ▼
 (optional) Gemini: "why this comes next" + effort calibration
        │
        ▼
 Roadmap JSON  ──►  UI graph + timeline  +  Markdown / .ics export
```

- **Graph engine** — pure-dict adjacency, no external graph library.
- **Ranking** — TF-IDF keyword ranker by default; a `fastembed` ONNX ranker is
  available optionally (`CF_USE_EMBEDDINGS=1`).
- **LLM** — exactly one batched call per roadmap, never per course, and always
  optional.

## Project layout

```
grandhack/
├── backend/
│   ├── app/
│   │   ├── config.py              # env-driven settings
│   │   ├── schemas.py             # Pydantic models (mirror the TS contract)
│   │   ├── graph/                 # knowledge graph + pathfinder
│   │   ├── nlp/                   # ranker, optional embedder, Gemini client
│   │   ├── services/              # roadmap orchestrator + exporters
│   │   ├── routers/               # /api/{roadmap,graph,courses,export,topics}
│   │   └── data/seed_graph.json   # curated topics, edges, courses
│   ├── scripts/
│   │   ├── build_seed.py          # regenerates the seed graph
│   │   └── demo.ps1               # one-command single-port demo
│   └── tests/                     # pytest suite
└── frontend/                      # Next.js 16 + React 19 + Tailwind v4
    └── src/
        ├── types/index.ts         # the shared data contract
        ├── lib/api.ts             # typed API client + export URLs
        ├── app/                   # landing, /login, /roadmap
        └── components/ui/         # timeline, course card, graph
```

## Quickstart

### Single-port demo (recommended)

```powershell
powershell -ExecutionPolicy Bypass -File backend\scripts\demo.ps1
```

This creates the venv, installs deps, builds the seed graph, builds the
frontend as a static export with a same-origin API URL, then serves everything
at <http://localhost:8000> and opens your browser.

### Development (two servers + CORS)

```powershell
# terminal 1 - API
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\build_seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# terminal 2 - web
cd frontend
npm install
npm run dev            # http://localhost:3000  (defaults to API on :8000)
```

### Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -q
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/roadmap` | Build a roadmap from `{goal, currentKnowledge, weeksAvailable, weeklyHours}` |
| `GET`  | `/api/topics` | List known topics |
| `GET`  | `/api/graph/{topic}` | Prerequisite subgraph for visualization |
| `GET`  | `/api/courses?topic=&limit=` | Ranked free courses for a topic |
| `GET`  | `/api/export/{roadmap_id}?format=markdown\|ics` | Download the roadmap |
| `GET`  | `/api/health` | Status, seed info, whether Gemini is configured |

Interactive docs: <http://localhost:8000/docs>.

## Configuration

All optional; see `backend/.env.example`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | *(empty)* | Enables LLM-enriched narratives |
| `CF_GEMINI_MODEL` | `gemini-2.0-flash` | Model name |
| `CF_RANKER` | `keyword` | `keyword` or `embedding` |
| `CF_USE_EMBEDDINGS` | *(off)* | Set to `1` to enable ONNX embeddings (needs `fastembed`) |
| `CF_CORS_ORIGINS` | `localhost:3000,127.0.0.1:3000` | Dev CORS origins |
| `CF_FRONTEND_DIR` | `frontend/out` | Static build served in demo mode |
| `CF_CACHE_TTL_S` | `3600` | In-memory roadmap cache TTL |

## Notes

- Course entries point to free/auditable sources (MIT OCW, Khan Academy,
  NPTEL, Coursera audit, YouTube); always verify current availability and
  terms on the provider site.
- The roadmap provides guidance, not academic credit — that is the point.
