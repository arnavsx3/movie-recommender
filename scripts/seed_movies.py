# scripts/seed_movies.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from sqlalchemy.orm import Session
from backend.app.db.database import engine
from backend.app.db.models import Movie

CSV_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "processed" / "movies_processed.csv"
)


def seed_movies():
    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=["title"])

    with Session(engine) as session:
        existing = {m.tmdb_id for m in session.query(Movie.tmdb_id).all()}
        inserted = 0

        for _, row in df.iterrows():
            tmdb_id = str(row["movie_id"])
            if tmdb_id in existing:
                continue

            movie = Movie(
                tmdb_id=tmdb_id,
                title=row["title"],
                overview=None,
                genres=None,
                keywords=None,
                cast=None,
                director=None,
                popularity=None,
                vote_average=None,
            )
            session.add(movie)
            inserted += 1

        session.commit()
        print(f"Inserted {inserted} movies.")


if __name__ == "__main__":
    seed_movies()
