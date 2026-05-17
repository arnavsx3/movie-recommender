from pathlib import Path
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_PATH = Path(__file__).resolve().parents[3] / "data" / "chromadb"

_client = None
_collection = None
_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = _client.get_collection(name="movies")
    return _collection

def recommend_by_title(title: str, n: int = 10) -> list[dict]:
    collection = _get_collection()
    model = _get_model()

    query_embedding = model.encode(title).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n + 1,
    )

    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    recommendations = []
    for meta, distance in zip(metadatas, distances):
        if str(meta.get("title", "")).lower() == title.lower():
            continue
        recommendations.append({
            "title": meta["title"],
            "score": round(1 - distance, 4),
        })

    return recommendations[:n]


def recommend_by_text(text: str, n: int = 10) -> list[dict]:
    collection = _get_collection()
    model = _get_model()

    query_embedding = model.encode(text).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
    )

    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    return [
        {"title": meta["title"], "score": round(1 - distance, 4)}
        for meta, distance in zip(metadatas, distances)
    ]