from fastapi import FastAPI
from .api.routes.auth import router as auth_router
from .api.routes.movies import router as movies_router
from backend.app.api.routes.ratings import router as ratings_router

app = FastAPI(
    title="Movie Recommender API",
    version="0.1.0"
)

app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(ratings_router)

@app.get("/")
def root():
    return {"message": "Movie Recommender API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}