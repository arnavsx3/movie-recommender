# backend/app/api/routes/movies.py

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from backend.app.ml.hybrid import hybrid_recommend_by_title, hybrid_recommend_by_text
from backend.app.db.database import get_db
from backend.app.api.dependencies import get_current_user_optional

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Movie title to get recommendations for"),
    n: int = Query(10, ge=1, le=50),
    alpha: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="Blend weight: 1.0=content only, 0.0=collaborative only",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = str(current_user.id) if current_user else None
    results = hybrid_recommend_by_title(
        title=title, n=n, user_id=user_id, db=db, alpha=alpha
    )
    if not results:
        raise HTTPException(status_code=404, detail="No recommendations found")
    return {"title": title, "recommendations": results}


@router.get("/search")
def search_movies(
    q: str = Query(..., description="Free text to search movies by"),
    n: int = Query(10, ge=1, le=50),
    alpha: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = str(current_user.id) if current_user else None
    results = hybrid_recommend_by_text(text=q, n=n, user_id=user_id, db=db, alpha=alpha)
    if not results:
        raise HTTPException(status_code=404, detail="No results found")
    return {"query": q, "results": results}
