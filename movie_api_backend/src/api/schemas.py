"""Pydantic schemas for API input/output."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ---------- User ----------
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserOut(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

# ---------- Movie ----------
class MovieBase(BaseModel):
    title: str
    year: Optional[int]
    director: Optional[str]
    description: Optional[str]

class MovieCreate(MovieBase):
    pass

class MovieUpdate(MovieBase):
    pass

class MovieOut(MovieBase):
    id: int
    tags: List[str] = []
    created_at: datetime

    class Config:
        orm_mode = True

# ---------- List ----------
class MovieListBase(BaseModel):
    name: str

class MovieListCreate(MovieListBase):
    pass

class MovieListOut(MovieListBase):
    id: int
    is_custom: bool
    owner_id: int
    movies: Optional[List[int]] = []
    created_at: datetime

    class Config:
        orm_mode = True

# ---------- Tag ----------
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int

    class Config:
        orm_mode = True

# ---------- Note ----------
class NoteBase(BaseModel):
    content: str

class NoteCreate(NoteBase):
    movie_id: int

class NoteOut(NoteBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ---------- Rating ----------
class RatingBase(BaseModel):
    score: float

class RatingCreate(RatingBase):
    movie_id: int

class RatingOut(RatingBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime

    class Config:
        orm_mode = True
