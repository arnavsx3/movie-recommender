import numpy as np
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.db.models import Rating, Movie


def _build_matrix(db: Session) -> tuple[dict, dict, np.ndarray]:
    """Build user-movie ratings matrix from DB."""
    all_ratings = db.query(Rating).all()

    if not all_ratings:
        return {}, {}, np.array([])

    user_ids = sorted(set(str(r.user_id) for r in all_ratings))
    movie_ids = sorted(set(str(r.movie_id) for r in all_ratings))

    user_idx = {uid: i for i, uid in enumerate(user_ids)}
    movie_idx = {mid: i for i, mid in enumerate(movie_ids)}

    matrix = np.zeros((len(user_ids), len(movie_ids)))

    for r in all_ratings:
        i = user_idx[str(r.user_id)]
        j = movie_idx[str(r.movie_id)]
        matrix[i][j] = r.rating

    return user_idx, movie_idx, matrix


def _cosine_similarity(matrix: np.ndarray) -> np.ndarray:
    """Compute user-user cosine similarity."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10  # avoid division by zero
    normalized = matrix / norms
    return normalized @ normalized.T


def recommend_collaborative(
    user_id: str,
    db: Session,
    n: int = 10,
) -> list[dict]:
    user_idx, movie_idx, matrix = _build_matrix(db)

    if not user_idx or user_id not in user_idx:
        return []

    idx_to_movie = {v: k for k, v in movie_idx.items()}
    sim_matrix = _cosine_similarity(matrix)

    u = user_idx[user_id]
    sim_scores = sim_matrix[u]

    sim_scores[u] = 0
    weighted_ratings = sim_scores @ matrix
    sim_sum = np.abs(sim_scores).sum()

    if sim_sum == 0:
        return []

    predicted = weighted_ratings / sim_sum

    already_rated = np.where(matrix[u] > 0)[0]
    predicted[already_rated] = -1

    top_indices = np.argsort(predicted)[::-1][:n] # checkpoint

    results = []
    for i in top_indices:
        if predicted[i] <= 0:
            continue
        movie_id = idx_to_movie[i]
        movie = db.query(Movie).filter(Movie.id == UUID(movie_id)).first()
        if movie:
            results.append(
                {
                    "id": str(movie.id),
                    "title": movie.title,
                    "genres": movie.genres,
                    "predicted_rating": round(float(predicted[i]), 2),
                }
            )

    return results
