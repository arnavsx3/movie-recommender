from fastapi import APIRouter, HTTPException, Query
from backend.app.ml.recommender import recommend_by_title, recommend_by_text

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Movie title to get recommendations for"),
    n: int = Query(10, ge=1, le=50, description="Number of recommendations"),
):
    results = recommend_by_title(title=title, n=n)
    if not results:
        raise HTTPException(status_code=404, detail="No recommendations found")
    return {"title": title, "recommendations": results}


@router.get("/search")
def search_movies(
    q: str = Query(..., description="Free text to search movies by"),
    n: int = Query(10, ge=1, le=50, description="Number of results"),
):
    results = recommend_by_text(text=q, n=n)
    if not results:
        raise HTTPException(status_code=404, detail="No results found")
    return {"query": q, "results": results}
