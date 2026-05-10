# movie-recommender

A hybrid movie recommendation system using content-based and collaborative filtering.

## Tech Stack

- **Frontend** — Streamlit
- **Backend** — FastAPI + Uvicorn
- **ML** — Scikit-learn, Pandas, NumPy, NLTK, ChromaDB
- **Database** — PostgreSQL (NeonDB)

## Project Structure

```
movie-recommender/
├── frontend/
├── backend/
│   └── app/
│       ├── api/
│       ├── ml/
│       ├── db/
│       ├── services/
│       └── utils/
├── data/
├── notebooks/
├── models/
└── scripts/
```

## Setup

```bash
uv sync
uv run uvicorn backend.app.main:app --reload
```

## Features

- Content-based filtering (genres, overview, cast, keywords)
- Collaborative filtering (user ratings)
- Hybrid recommendation with tunable weights
- Cold start strategy for new users