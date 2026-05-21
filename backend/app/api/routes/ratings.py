from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.db.database import get_db
from backend.app.db.models import Rating, Movie
from backend.app.api.schemas import RatingCreate, RatingResponse
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("/", response_model=RatingResponse)
def submit_rating(
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not (0.5 <= payload.rating <= 5.0):
        raise HTTPException(
            status_code=400, detail="Rating must be between 0.5 and 5.0"
        )

    movie = db.query(Movie).filter(Movie.id == payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing = (
        db.query(Rating)
        .filter(Rating.user_id == current_user.id, Rating.movie_id == payload.movie_id)
        .first()
    )
    if existing:
        existing.rating = payload.rating  # type:ignore
        db.commit()
        db.refresh(existing)
        return existing

    new_rating = Rating(
        user_id=current_user.id,
        movie_id=payload.movie_id,
        rating=payload.rating,
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


@router.get("/{user_id}", response_model=list[RatingResponse])
def get_user_ratings(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these ratings"
        )

    ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    return ratings
