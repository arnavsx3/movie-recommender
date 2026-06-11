from sqlalchemy.orm import Session
from backend.app.ml.recommender import recommend_by_title, recommend_by_text
from backend.app.ml.collaborative import recommend_collaborative
from backend.app.ml.recommender import _get_collection, _get_model
from backend.app.db.models import Rating, Movie
from uuid import UUID


def _has_ratings(user_id: str, db: Session) -> bool:
    return db.query(Rating).filter(Rating.user_id == user_id).count() > 0

def _get_user_rated_titles(
    user_id: str, db: Session, min_rating: float = 3.5
) -> list[str]:
    """Return titles the user rated at or above min_rating."""
    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user_id, Rating.rating >= min_rating)
        .all()
    )
    titles = []
    for r in ratings:
        movie = db.query(Movie).filter(Movie.id == r.movie_id).first()
        if movie:
            titles.append(movie.title)
    return titles

def _find_because_of(rec_title: str, rated_titles: list[str]) -> str | None:
    """Find which rated movie is most similar to the recommendation via ChromaDB."""
    if not rated_titles:
        return None

    collection = _get_collection()
    model = _get_model()

    best_title = None
    best_score = -1.0

    for rated_title in rated_titles:
        rated_embedding = model.encode(rated_title).tolist()
        results = collection.query(
            query_embeddings=[rated_embedding],
            n_results=20,
        )
        metadatas = results.get("metadatas") or []
        distances = results.get("distances") or []

        if not metadatas:
            continue

        for t, d in zip(metadatas[0], distances[0]):
            if str(t).lower() == rec_title.lower():
                score = 1 - d
                if score > best_score:
                    best_score = score
                    best_title = rated_title
                break

    return best_title if best_score > 0.1 else None

def _blend(
    content_results: list[dict],
    collab_results: list[dict],
    rated_titles: list[str],
    alpha: float = 0.5,
) -> list[dict]:
    max_rating = 5.0

    collab_map = {
        r["title"]: r["predicted_rating"] / max_rating for r in collab_results
    }

    blended = []
    for item in content_results:
        title = item["title"]
        content_score = item["score"]
        collab_score = collab_map.get(title, 0.0)

        final_score = alpha * content_score + (1 - alpha) * collab_score
        is_hybrid = collab_score > 0

        entry = {
            "title": title,
            "score": round(final_score, 4),
            "source": "hybrid" if is_hybrid else "content",
            "because_of": None,
        }

        if is_hybrid:
            entry["because_of"] = _find_because_of(title, rated_titles)

        blended.append(entry)

    blended.sort(key=lambda x: x["score"], reverse=True)
    return blended

def hybrid_recommend_by_title(
    title: str,
    n: int = 10,
    user_id: str | None = None,
    db: Session | None = None,
    alpha: float = 0.5,
) -> list[dict]:
    content_results = recommend_by_title(title=title, n=n)

    if not user_id or not db or not _has_ratings(user_id, db):
        for r in content_results:
            r["source"] = "content"
            r["because_of"] = None
        return content_results

    collab_results = recommend_collaborative(user_id=user_id, db=db, n=n)

    if not collab_results:
        for r in content_results:
            r["source"] = "content"
            r["because_of"] = None
        return content_results

    rated_titles = _get_user_rated_titles(user_id, db)
    return _blend(content_results, collab_results, rated_titles, alpha=alpha)
