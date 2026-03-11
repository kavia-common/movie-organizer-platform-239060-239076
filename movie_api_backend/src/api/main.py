from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Organizer API",
    description="Backend REST API for movie management, user lists, tags, notes, ratings, and moderation",
    version="0.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Movies", "description": "Movie management"},
        {"name": "Users", "description": "User management"},
        {"name": "Lists", "description": "Movie lists management"},
        {"name": "Tags", "description": "Tag management"},
        {"name": "Notes", "description": "Personal notes"},
        {"name": "Ratings", "description": "Movie ratings"},
        {"name": "Moderation", "description": "Admin/moderator endpoints"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Health"], summary="Health Check", description="Check API health/status")
def health_check():
    return {"message": "Healthy"}

# --------------------- User Endpoints --------------------- #

@app.post("/users/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Users"], summary="Register user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # NOTE: In a real app use password hashing (e.g. bcrypt)
    hashed_pw = "hashed_" + user.password  # Placeholder for real hashing
    user_obj = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@app.get("/users/{user_id}", response_model=schemas.UserOut, tags=["Users"], summary="Get user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --------------------- Movie Endpoints --------------------- #

@app.post("/movies/", response_model=schemas.MovieOut, status_code=status.HTTP_201_CREATED, tags=["Movies"], summary="Add a new movie")
def add_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """Add a new movie."""
    movie_obj = models.Movie(**movie.dict())
    db.add(movie_obj)
    db.commit()
    db.refresh(movie_obj)
    return movie_obj

@app.get("/movies/", response_model=List[schemas.MovieOut], tags=["Movies"], summary="List/search movies")
def list_movies(
    search: str = Query(None, description="Search by title"),
    skip: int = 0,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List or search movies by title."""
    query = db.query(models.Movie)
    if search:
        query = query.filter(models.Movie.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@app.get("/movies/{movie_id}", response_model=schemas.MovieOut, tags=["Movies"], summary="Get movie by ID")
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get a movie by ID."""
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.put("/movies/{movie_id}", response_model=schemas.MovieOut, tags=["Movies"], summary="Update movie")
def update_movie(movie_id: int, upd: schemas.MovieUpdate, db: Session = Depends(get_db)):
    """Update a movie."""
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    for k, v in upd.dict(exclude_unset=True).items():
        setattr(movie, k, v)
    db.commit()
    db.refresh(movie)
    return movie

@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Movies"], summary="Delete a movie")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """Delete a movie."""
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return

# --------------------- Lists Endpoints --------------------- #

@app.post("/lists/", response_model=schemas.MovieListOut, status_code=status.HTTP_201_CREATED, tags=["Lists"], summary="Create a movie list")
def create_list(list_in: schemas.MovieListCreate, db: Session = Depends(get_db)):
    """Create a new movie list. Owner must be set in a real implementation."""
    # For demo, assign to first user
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=400, detail="You must register at least one user first")
    list_obj = models.MovieList(name=list_in.name, owner_id=user.id)
    db.add(list_obj)
    db.commit()
    db.refresh(list_obj)
    return list_obj

@app.get("/lists/{list_id}", response_model=schemas.MovieListOut, tags=["Lists"], summary="Get list by ID")
def get_list(list_id: int, db: Session = Depends(get_db)):
    lst = db.query(models.MovieList).filter(models.MovieList.id == list_id).first()
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    return lst

# Additional endpoints for adding/removing movies from lists...

# --------------------- Tags Endpoints --------------------- #

@app.post("/tags/", response_model=schemas.TagOut, status_code=status.HTTP_201_CREATED, tags=["Tags"], summary="Create new tag")
def create_tag(tag_in: schemas.TagCreate, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_in.name).first()
    if tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = models.Tag(name=tag_in.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@app.get("/tags/", response_model=List[schemas.TagOut], tags=["Tags"], summary="List all tags")
def list_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).all()

# --------------------- Notes Endpoints --------------------- #

@app.post("/notes/", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED, tags=["Notes"], summary="Add personal note to a movie")
def add_note(note_in: schemas.NoteCreate, db: Session = Depends(get_db)):
    # For demo: assign to first user
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=400, detail="You must register a user first")
    movie = db.query(models.Movie).filter(models.Movie.id == note_in.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    note = models.Note(content=note_in.content, user_id=user.id, movie_id=note_in.movie_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.get("/notes/{user_id}", response_model=List[schemas.NoteOut], tags=["Notes"], summary="Get all notes for a user")
def list_notes(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.user_id == user_id).all()

# --------------------- Ratings Endpoints --------------------- #

@app.post("/ratings/", response_model=schemas.RatingOut, status_code=status.HTTP_201_CREATED, tags=["Ratings"], summary="Add a rating to a movie")
def add_rating(rating_in: schemas.RatingCreate, db: Session = Depends(get_db)):
    # For demo: assign to first user
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=400, detail="You must register a user first")
    movie = db.query(models.Movie).filter(models.Movie.id == rating_in.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    rating = models.Rating(score=rating_in.score, user_id=user.id, movie_id=rating_in.movie_id)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

@app.get("/ratings/{movie_id}", response_model=List[schemas.RatingOut], tags=["Ratings"], summary="Get all ratings for a movie")
def get_ratings_for_movie(movie_id: int, db: Session = Depends(get_db)):
    return db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
