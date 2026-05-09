from fastapi import FastAPI

app = FastAPI(
    title="Movie Recommender API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Movie Recommender API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}