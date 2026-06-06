from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class RatingCreate(BaseModel):
    movie_id: UUID
    rating: float


class RatingResponse(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    rating: float
    created_at: datetime

    class Config:
        from_attributes = True


class MovieResponse(BaseModel):
    id: UUID
    tmdb_id: str
    title: str
    overview: Optional[str]
    genres: Optional[str]
    popularity: Optional[float]
    vote_average: Optional[float]

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str