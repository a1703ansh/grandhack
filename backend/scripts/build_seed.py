"""Generates data/seed_graph.json — the curated syllabus knowledge graph.

Run:  python scripts/build_seed.py
Writes: backend/app/data/seed_graph.json

The graph models *learning order*, not keyword relevance. Every edge is a
"requires" relationship tagged with its provenance (source + confidence):

  explicit syllabus  -> taken from a real course's "Prerequisites:" section
  khan order         -> follows Khan Academy's published topic-tree ordering
  inferred           -> derived from topic semantics (lowest confidence)

Embeddings: if fastembed is importable, per-course embedding vectors are
appended (Tier-2). Otherwise the graph ships keyword-rankable without them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"

# ---------------------------------------------------------------- topics
# topic_id -> {name, description, difficulty, hours (effort to complete),
#              why (reason this belongs in the chain toward advanced goals)}
TOPICS: dict[str, dict] = {
    "python_core": {
        "name": "Python Basics",
        "description": "Core Python programming: syntax, data structures, functions, and reading/writing code comfortably.",
        "difficulty": "Beginner",
        "hours": 30,
        "why": "The lingua franca of AI — every ML library (NumPy, PyTorch, scikit-learn) is Python-first.",
    },
    "python_data_tools": {
        "name": "Python for Data (NumPy/Pandas)",
        "description": "Vectorized computation and tabular data with NumPy, Pandas, Matplotlib — the data plumbing of ML.",
        "difficulty": "Beginner",
        "hours": 20,
        "why": "Models eat matrices and tables; this is the vocabulary every pipeline is written in.",
    },
    "linear_algebra": {
        "name": "Linear Algebra",
        "description": "Vectors, matrices, eigenvalues, and linear transformations — the math deep learning is built on.",
        "difficulty": "Intermediate",
        "hours": 40,
        "why": "A neural network IS matrix multiplication; backprop is a chain rule over weighted sums.",
    },
    "calculus": {
        "name": "Calculus",
        "description": "Derivatives, integrals, and optimization from a single-variable standpoint.",
        "difficulty": "Intermediate",
        "hours": 40,
        "why": "Gradient descent is pure calculus — you need derivatives to understand how models learn.",
    },
    "probability_stats": {
        "name": "Probability & Statistics",
        "description": "Distributions, Bayes' theorem, expectation, and statistical inference.",
        "difficulty": "Intermediate",
        "hours": 35,
        "why": "Learning algorithms reason under uncertainty; probability is their language.",
    },
    "algorithms_data_structures": {
        "name": "Algorithms & Data Structures",
        "description": "Big-O analysis, trees, graphs, sorting, and dynamic programming.",
        "difficulty": "Intermediate",
        "hours": 35,
        "why": "Sharpens the systematic thinking that makes the harder ML theory tractable.",
    },
    "machine_learning_fundamentals": {
        "name": "Machine Learning Fundamentals",
        "description": "Supervised/unsupervised learning, regression, classification, bias-variance, and evaluation.",
        "difficulty": "Intermediate",
        "hours": 30,
        "why": "Gives you the model-building workflow and evaluation mindset before neural networks.",
    },
    "neural_networks": {
        "name": "Neural Networks",
        "description": "Perceptrons, activation functions, forward/backward propagation, and optimization.",
        "difficulty": "Intermediate",
        "hours": 25,
        "why": "The core architecture — understand one neuron-to-network before you scale up.",
    },
    "deep_learning": {
        "name": "Deep Learning",
        "description": "CNNs, RNNs, regularization at scale, and modern architectures.",
        "difficulty": "Advanced",
        "hours": 40,
        "why": "The full stack: training deep nets on real data with modern tools.",
    },
    "deep_learning_cv": {
        "name": "Deep Learning for Computer Vision",
        "description": "Convolutional architectures, object detection, segmentation, and transfer learning.",
        "difficulty": "Advanced",
        "hours": 30,
        "why": "Concretizes deep learning on image tasks — the most intuitive visual domain.",
    },
    "natural_language_processing": {
        "name": "Natural Language Processing",
        "description": "Tokenization, embeddings, RNNs/attention, and transformers for text.",
        "difficulty": "Advanced",
        "hours": 30,
        "why": "Applies the same toolkit to language, the other half of modern AI.",
    },
    "data_science": {
        "name": "Data Science",
        "description": "End-to-end analysis: cleaning, exploration, modeling, and communicating findings.",
        "difficulty": "Intermediate",
        "hours": 25,
        "why": "Turns the tools into a complete analytical workflow.",
    },
}

# ---------------------------------------------------------------- edges
# from -> to : "topic A requires topic B"
# source/confidence provenance per edge, so the UI can cite evidence.
EDGES: list[dict] = [
    # ---- foundational python chain (MIT 6.0002 explicitly requires 6.0001)
    {"from": "python_core", "to": "python_data_tools", "source": "explicit syllabus", "confidence": 0.95},
    {"from": "python_core", "to": "algorithms_data_structures", "source": "explicit syllabus", "confidence": 0.9},
    # ---- math branch (MIT 18.06's 'Prerequisites:' nothing beyond HS math;
    #      calculus is the textbook prerequisite for probability)
    {"from": "calculus", "to": "probability_stats", "source": "inferred", "confidence": 0.7},
    # ---- ML gate (Ng/MIT 6.036 list programming + linear algebra + probability)
    {"from": "python_data_tools", "to": "machine_learning_fundamentals", "source": "explicit syllabus", "confidence": 0.9},
    {"from": "linear_algebra", "to": "machine_learning_fundamentals", "source": "explicit syllabus", "confidence": 0.9},
    {"from": "probability_stats", "to": "machine_learning_fundamentals", "source": "explicit syllabus", "confidence": 0.85},
    # ---- NN gate (Coursera "Neural Networks & Deep Learning" requires Python + basic ML)
    {"from": "machine_learning_fundamentals", "to": "neural_networks", "source": "explicit syllabus", "confidence": 0.9},
    # ---- DL follows the NN course by construction of the specialization
    {"from": "neural_networks", "to": "deep_learning", "source": "explicit syllabus", "confidence": 0.95},
    # ---- specialist tracks
    {"from": "deep_learning", "to": "deep_learning_cv", "source": "inferred", "confidence": 0.8},
    {"from": "deep_learning", "to": "natural_language_processing", "source": "inferred", "confidence": 0.8},
    {"from": "python_data_tools", "to": "data_science", "source": "khan order", "confidence": 0.8},
    {"from": "probability_stats", "to": "data_science", "source": "khan order", "confidence": 0.75},
]

# ---------------------------------------------------------------- courses
# topic_id -> list of candidate free courses. `keywords` powers the
# deterministic keyword ranker; embedding vectors (if fastembed present)
# are appended into the emitted JSON under `embeddings`.
COURSES: dict[str, list[dict]] = {
    "python_core": [
        {
            "id": "mit_6_0001",
            "title": "Introduction to Computer Science and Programming in Python (6.0001)",
            "source": "MIT OCW",
            "difficulty": "Beginner",
            "durationHours": 40,
            "rating": 4.9,
            "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/",
            "tags": ["Python", "CS101"],
            "keywords": "intro computer science programming python mit ocw fundamentals",
        },
        {
            "id": "khan_intro_python",
            "title": "Intro to Python Programming",
            "source": "Khan Academy",
            "difficulty": "Beginner",
            "durationHours": 20,
            "rating": 4.8,
            "url": "https://www.khanacademy.org/computing/intro-to-python-fundamentals",
            "tags": ["Python", "Programming"],
            "keywords": "python programming interactive khan academy beginner coding",
        },
        {
            "id": "nptel_joy_python",
            "title": "The Joy of Computing using Python (NPTEL)",
            "source": "NPTEL",
            "difficulty": "Beginner",
            "durationHours": 25,
            "rating": 4.6,
            "url": "https://nptel.ac.in/courses/106106182",
            "tags": ["Python", "Programming"],
            "keywords": "python joy computing nptel programming course",
        },
    ],
    "python_data_tools": [
        {
            "id": "mit_6_0002",
            "title": "Introduction to Computational Thinking and Data Science (6.0002)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 35,
            "rating": 4.8,
            "url": "https://ocw.mit.edu/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016/",
            "tags": ["Data Science", "Python"],
            "keywords": "computational thinking data science numpy matplotlib mit ocw python",
        },
        {
            "id": "nptel_python_ds",
            "title": "Python for Data Science (NPTEL, IITM)",
            "source": "NPTEL",
            "difficulty": "Beginner",
            "durationHours": 20,
            "rating": 4.6,
            "url": "https://nptel.ac.in/courses/106106308",
            "tags": ["Data Science", "Python"],
            "keywords": "python data science pandas numpy nptel iit madras",
        },
        {
            "id": "youtube_freecodecamp_da",
            "title": "Data Analysis with Python — Full Course (NumPy, Pandas, Seaborn)",
            "source": "YouTube",
            "difficulty": "Beginner",
            "durationHours": 10,
            "rating": 4.8,
            "url": "https://www.youtube.com/watch?v=GPVsHOlRBBI",
            "tags": ["NumPy", "Pandas", "Data Science"],
            "keywords": "data analysis python numpy pandas seaborn freecodecamp youtube",
        },
    ],
    "linear_algebra": [
        {
            "id": "mit_18_06",
            "title": "Linear Algebra (18.06, Gilbert Strang)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 40,
            "rating": 4.9,
            "url": "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/",
            "tags": ["Math", "Linear Algebra"],
            "keywords": "linear algebra matrices strang mit ocw vectors eigenvalues",
        },
        {
            "id": "youtube_3b1b_la",
            "title": "Essence of Linear Algebra (3Blue1Brown)",
            "source": "YouTube",
            "difficulty": "Beginner",
            "durationHours": 8,
            "rating": 4.9,
            "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
            "tags": ["Math", "Linear Algebra"],
            "keywords": "linear algebra visual intuition 3blue1brown youtube essence",
        },
        {
            "id": "khan_linear_algebra",
            "title": "Linear Algebra (precalculus to eigenvectors)",
            "source": "Khan Academy",
            "difficulty": "Beginner",
            "durationHours": 25,
            "rating": 4.8,
            "url": "https://www.khanacademy.org/math/linear-algebra",
            "tags": ["Math", "Linear Algebra"],
            "keywords": "linear algebra vectors matrices khan academy eigenvalues",
        },
    ],
    "calculus": [
        {
            "id": "mit_18_01",
            "title": "Single Variable Calculus (18.01)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 40,
            "rating": 4.9,
            "url": "https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/",
            "tags": ["Math", "Calculus"],
            "keywords": "calculus single variable derivatives integrals mit ocw",
        },
        {
            "id": "youtube_3b1b_calc",
            "title": "Essence of Calculus (3Blue1Brown)",
            "source": "YouTube",
            "difficulty": "Beginner",
            "durationHours": 7,
            "rating": 4.9,
            "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr",
            "tags": ["Math", "Calculus"],
            "keywords": "calculus intuition derivatives integrals 3blue1brown youtube",
        },
        {
            "id": "khan_calculus1",
            "title": "Calculus 1 (limits, derivatives, integrals)",
            "source": "Khan Academy",
            "difficulty": "Beginner",
            "durationHours": 30,
            "rating": 4.8,
            "url": "https://www.khanacademy.org/math/calculus-1",
            "tags": ["Math", "Calculus"],
            "keywords": "calculus limits derivatives integrals khan academy",
        },
    ],
    "probability_stats": [
        {
            "id": "mit_6_041",
            "title": "Probabilistic Systems Analysis and Applied Probability (6.041)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 35,
            "rating": 4.8,
            "url": "https://ocw.mit.edu/courses/6-041sc-probabilistic-systems-analysis-and-applied-probability-fall-2013/",
            "tags": ["Math", "Probability"],
            "keywords": "probability random variables expectation systems analysis mit ocw",
        },
        {
            "id": "khan_stats_prob",
            "title": "Statistics and Probability",
            "source": "Khan Academy",
            "difficulty": "Beginner",
            "durationHours": 20,
            "rating": 4.8,
            "url": "https://www.khanacademy.org/math/statistics-probability",
            "tags": ["Math", "Statistics", "Probability"],
            "keywords": "statistics probability distributions khan academy bayes",
        },
        {
            "id": "youtube_stat110",
            "title": "Statistics 110: Probability (Harvard)",
            "source": "YouTube",
            "difficulty": "Intermediate",
            "durationHours": 25,
            "rating": 4.7,
            "url": "https://www.youtube.com/playlist?list=PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo",
            "tags": ["Math", "Probability"],
            "keywords": "probability harvard stat110 statistics joe blitzstein youtube",
        },
    ],
    "algorithms_data_structures": [
        {
            "id": "mit_6_006",
            "title": "Introduction to Algorithms (6.006)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 40,
            "rating": 4.8,
            "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
            "tags": ["Algorithms", "Data Structures"],
            "keywords": "algorithms data structures big-o graphs mit ocw programming",
        },
        {
            "id": "coursera_algo_spec",
            "title": "Algorithms Specialization (Stanford, audit)",
            "source": "Coursera Audit",
            "difficulty": "Intermediate",
            "durationHours": 40,
            "rating": 4.9,
            "url": "https://www.coursera.org/specializations/algorithms",
            "tags": ["Algorithms", "Data Structures"],
            "keywords": "algorithms divide conquer graphs greedy dynamic programming coursera stanford",
        },
        {
            "id": "nptel_algos",
            "title": "Design and Analysis of Algorithms (NPTEL)",
            "source": "NPTEL",
            "difficulty": "Intermediate",
            "durationHours": 35,
            "rating": 4.6,
            "url": "https://nptel.ac.in/courses/106106131",
            "tags": ["Algorithms", "Data Structures"],
            "keywords": "algorithms design analysis nptel complexity searching sorting",
        },
    ],
    "machine_learning_fundamentals": [
        {
            "id": "coursera_ml_ng",
            "title": "Machine Learning (Andrew Ng)",
            "source": "Coursera Audit",
            "difficulty": "Intermediate",
            "durationHours": 30,
            "rating": 4.9,
            "url": "https://www.coursera.org/learn/machine-learning",
            "tags": ["Machine Learning", "Regression"],
            "keywords": "machine learning regression classification andrew ng coursera supervised",
        },
        {
            "id": "mit_6_036",
            "title": "Introduction to Machine Learning (6.036)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 35,
            "rating": 4.8,
            "url": "https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-fall-2020/",
            "tags": ["Machine Learning", "Python"],
            "keywords": "machine learning mit ocw supervised deep learning python algorithms",
        },
        {
            "id": "nptel_ml",
            "title": "Machine Learning (NPTEL, IITM)",
            "source": "NPTEL",
            "difficulty": "Intermediate",
            "durationHours": 30,
            "rating": 4.6,
            "url": "https://nptel.ac.in/courses/106106139",
            "tags": ["Machine Learning"],
            "keywords": "machine learning nptel bayes svm clustering supervised learning",
        },
    ],
    "neural_networks": [
        {
            "id": "youtube_3b1b_nn",
            "title": "Neural Networks (3Blue1Brown)",
            "source": "YouTube",
            "difficulty": "Beginner",
            "durationHours": 5,
            "rating": 4.9,
            "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi",
            "tags": ["Neural Networks", "Deep Learning"],
            "keywords": "neural networks backpropagation intuition 3blue1brown youtube gradients",
        },
        {
            "id": "coursera_nndl",
            "title": "Neural Networks and Deep Learning (deeplearning.ai)",
            "source": "Coursera Audit",
            "difficulty": "Intermediate",
            "durationHours": 20,
            "rating": 4.9,
            "url": "https://www.coursera.org/learn/neural-networks-deep-learning",
            "tags": ["Neural Networks", "Deep Learning"],
            "keywords": "neural networks deep learning backpropagation coursera andrew ng python",
        },
        {
            "id": "nptel_dl1",
            "title": "Deep Learning — Part 1 (NPTEL)",
            "source": "NPTEL",
            "difficulty": "Intermediate",
            "durationHours": 20,
            "rating": 4.6,
            "url": "https://nptel.ac.in/courses/106106184",
            "tags": ["Deep Learning", "Neural Networks"],
            "keywords": "deep learning neural networks nptel perceptron gradient descent",
        },
    ],
    "deep_learning": [
        {
            "id": "coursera_dl_spec",
            "title": "Deep Learning Specialization (deeplearning.ai)",
            "source": "Coursera Audit",
            "difficulty": "Advanced",
            "durationHours": 40,
            "rating": 4.9,
            "url": "https://www.coursera.org/specializations/deep-learning",
            "tags": ["Deep Learning", "CNN", "RNN"],
            "keywords": "deep learning cnn rnn tensorflow pytorch coursera specialization",
        },
        {
            "id": "mit_6_s191",
            "title": "Introduction to Deep Learning (6.S191)",
            "source": "MIT OCW",
            "difficulty": "Advanced",
            "durationHours": 20,
            "rating": 4.8,
            "url": "https://ocw.mit.edu/courses/6-s191-introduction-to-deep-learning-spring-2020/",
            "tags": ["Deep Learning", "TensorFlow"],
            "keywords": "deep learning mit ocw tensorflow keras neural networks labs",
        },
        {
            "id": "fastai_practical_dl",
            "title": "Practical Deep Learning for Coders (fast.ai)",
            "source": "YouTube",
            "difficulty": "Intermediate",
            "durationHours": 30,
            "rating": 4.8,
            "url": "https://course.fast.ai/",
            "tags": ["Deep Learning", "PyTorch"],
            "keywords": "practical deep learning fastai pytorch vision nlp top-down",
        },
        {
            "id": "nptel_dl2",
            "title": "Deep Learning (NPTEL, 8-week)",
            "source": "NPTEL",
            "difficulty": "Advanced",
            "durationHours": 40,
            "rating": 4.5,
            "url": "https://nptel.ac.in/courses/106106224",
            "tags": ["Deep Learning"],
            "keywords": "deep learning nptel convolutional recurrent neural networks",
        },
    ],
    "deep_learning_cv": [
        {
            "id": "stanford_cs231n",
            "title": "CS231n: Deep Learning for Computer Vision (Stanford)",
            "source": "YouTube",
            "difficulty": "Advanced",
            "durationHours": 30,
            "rating": 4.7,
            "url": "https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv",
            "tags": ["Computer Vision", "CNN"],
            "keywords": "convolutional neural networks computer vision stanford cs231n CNN transfer learning",
        },
        {
            "id": "fastai_cv",
            "title": "Fast.ai Practical Deep Learning — Vision Track",
            "source": "YouTube",
            "difficulty": "Intermediate",
            "durationHours": 25,
            "rating": 4.8,
            "url": "https://course.fast.ai/",
            "tags": ["Computer Vision", "PyTorch"],
            "keywords": "computer vision transfer learning pytorch fastai image classification",
        },
    ],
    "natural_language_processing": [
        {
            "id": "coursera_nlp_spec",
            "title": "Natural Language Processing Specialization (deeplearning.ai)",
            "source": "Coursera Audit",
            "difficulty": "Advanced",
            "durationHours": 30,
            "rating": 4.8,
            "url": "https://www.coursera.org/specializations/natural-language-processing",
            "tags": ["NLP", "Transformers"],
            "keywords": "natural language processing nlp embeddings rnn transformers coursera",
        },
        {
            "id": "nptel_nlp",
            "title": "Natural Language Processing (NPTEL, IIT KGP)",
            "source": "NPTEL",
            "difficulty": "Advanced",
            "durationHours": 30,
            "rating": 4.5,
            "url": "https://nptel.ac.in/courses/106105158",
            "tags": ["NLP"],
            "keywords": "natural language processing nptel syntax parsing semantics morphology",
        },
        {
            "id": "stanford_cs224n",
            "title": "CS224n: Natural Language Processing with Deep Learning (Stanford)",
            "source": "YouTube",
            "difficulty": "Advanced",
            "durationHours": 35,
            "rating": 4.7,
            "url": "https://www.youtube.com/playlist?list=PLoROMvodv4rPP6kXogAlqzoD8eJGDBio1",
            "tags": ["NLP", "Deep Learning"],
            "keywords": "natural language processing deep learning stanford cs224n transformers",
        },
    ],
    "data_science": [
        {
            "id": "coursera_ibm_ds",
            "title": "IBM Data Science Professional Certificate (audit)",
            "source": "Coursera Audit",
            "difficulty": "Intermediate",
            "durationHours": 25,
            "rating": 4.8,
            "url": "https://www.coursera.org/professional-certificates/ibm-data-science",
            "tags": ["Data Science", "Python"],
            "keywords": "data science data analysis python sql ibm coursera certificate",
        },
        {
            "id": "mit_15_071",
            "title": "The Analytics Edge (15.071)",
            "source": "MIT OCW",
            "difficulty": "Intermediate",
            "durationHours": 25,
            "rating": 4.7,
            "url": "https://ocw.mit.edu/courses/15-071-the-analytics-edge-spring-2017/",
            "tags": ["Data Science", "Analytics"],
            "keywords": "analytics edge data science mit ocw regression visualization case studies",
        },
        {
            "id": "nptel_data_science_eng",
            "title": "Data Science for Engineers (NPTEL)",
            "source": "NPTEL",
            "difficulty": "Intermediate",
            "durationHours": 20,
            "rating": 4.5,
            "url": "https://nptel.ac.in/courses/106106179",
            "tags": ["Data Science", "Statistics"],
            "keywords": "data science engineers nptel statistics machine learning R",
        },
    ],
}

# ---------------------------------------------------------------- aliases
# User free-text ("I know numpy, some calculus") -> canonical topic ids.
ALIASES: dict[str, list[str]] = {
    "python_core": [
        "python", "python basics", "basic python", "python fundamentals",
        "python programming", "intro to python", "python syntax", "py",
        "i know python", "know python", "python3",
    ],
    "python_data_tools": [
        "numpy", "pandas", "python data", "python for data", "data tools",
        "python data tools", "dataframes", "matplotlib",
    ],
    "linear_algebra": [
        "linear algebra", "lin alg", "lin-alg", "matrices", "linearmath",
        "vectors and matrices",
    ],
    "calculus": ["calculus", "calc", "differential calculus", "integral calculus", "derivatives"],
    "probability_stats": [
        "probability", "statistics", "stats", "prob stats", "probstats",
        "probability and statistics", "bayes",
    ],
    "algorithms_data_structures": [
        "algorithms", "data structures", "dsa", "algo", "ds", "gate cs",
        "gate cs prep", "analysis of algorithms",
    ],
    "machine_learning_fundamentals": [
        "machine learning", "ml", "ml basics", "learn ml", "supervised learning",
        "basic ml", "machine learning fundamentals", "ai basics",
    ],
    "neural_networks": [
        "neural networks", "nn", "neural nets", "backpropagation", "backprop",
    ],
    "deep_learning": [
        "deep learning", "dl", "deeplearning", "deep neural networks",
        "master deep learning", "learn deep learning", "deep learning specialization",
    ],
    "deep_learning_cv": [
        "computer vision", "cv", "deep learning for computer vision", "image recognition",
        "cnn", "convolutional neural networks",
    ],
    "natural_language_processing": [
        "nlp", "natural language processing", "text mining", "language models",
    ],
    "data_science": [
        "data science", "data analyst", "data analytics", "analytics",
        "data analysis", "become data scientist",
    ],
}

GOAL_ID_ORDER = [
    "deep_learning",
    "deep_learning_cv",
    "natural_language_processing",
    "machine_learning_fundamentals",
    "data_science",
    "neural_networks",
    "algorithms_data_structures",
    "linear_algebra",
    "calculus",
    "probability_stats",
    "python_data_tools",
    "python_core",
]


def try_embeddings() -> dict[str, list[float]]:
    """Best-effort per-course embeddings via fastembed (Tier-2, seed-time).
    Returns {} when fastembed is unavailable so the graph stays rankable
    with the pure-Python keyword ranker."""
    try:
        from fastembed import TextEmbedding

        model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
        items = []
        for courses in COURSES.values():
            for c in courses:
                items.append((c["id"], c["title"] + ". " + c["keywords"]))
        ids = [i[0] for i in items]
        vectors = list(model.embed([i[1] for i in items]))
        vectors = [v.tolist() for v in vectors]
        return {iid: vec for iid, vec in zip(ids, vectors)}
    except Exception as exc:  # noqa: BLE001 - graceful seed-time degradation
        print(f"[build_seed] embeddings skipped (fastembed unavailable): {exc}", file=sys.stderr)
        return {}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = try_embeddings()

    flat_courses = []
    for topic_id, courses in COURSES.items():
        for c in courses:
            flat_courses.append({**c, "topic": topic_id})

    seed = {
        "topics": TOPICS,
        "edges": EDGES,
        "courses": flat_courses,
        "aliases": ALIASES,
        "goal_id_order": GOAL_ID_ORDER,
        "embeddings": embeddings,
        "embedding_dim": len(next(iter(embeddings.values()))) if embeddings else 0,
    }

    out = DATA_DIR / "seed_graph.json"
    out.write_text(json.dumps(seed, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"seed written: {out} ({len(TOPICS)} topics, {len(EDGES)} edges, "
          f"{len(flat_courses)} courses, embedding_dim={seed['embedding_dim']})")


if __name__ == "__main__":
    main()