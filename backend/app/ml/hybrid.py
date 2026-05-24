from sqlalchemy.orm import Session
from backend.app.ml.recommender import recommend_by_title, recommend_by_text
from backend.app.ml.collaborative import recommend_collaborative
from backend.app.db.models import Rating


def _has_ratings(user_id: str, db: Session) -> bool:
    return db.query(Rating).filter(Rating.user_id == user_id).count() > 0


def _blend(
    content_results: list[dict],
    collab_results: list[dict],
    alpha: float = 0.5,
) -> list[dict]:
    """
    Blend content and collaborative scores.
    alpha controls weight: 1.0 = pure content, 0.0 = pure collaborative.
    """
    max_rating = 5.0

    collab_map = {
        r["title"]: r["predicted_rating"] / max_rating for r in collab_results
    }

    blended = []
    for item in content_results:
        title = item["title"]
        content_score = item["score"]  # already 0–1
        collab_score = collab_map.get(title, 0.0)

        final_score = alpha * content_score + (1 - alpha) * collab_score
        blended.append(
            {
                "title": title,
                "score": round(final_score, 4),
                "source": "hybrid" if collab_score > 0 else "content",
            }
        )

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
        return content_results

    collab_results = recommend_collaborative(user_id=user_id, db=db, n=n)

    if not collab_results:
        for r in content_results:
            r["source"] = "content"
        return content_results

    return _blend(content_results, collab_results, alpha=alpha)

