"""SQLAlchemy ORM models for the movie organizer backend."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Table, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Association Table for many-to-many Movie <-> Tag
movie_tags = Table(
    "movie_tags",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

# Association Table for many-to-many List <-> Movie
list_membership = Table(
    "list_membership",
    Base.metadata,
    Column("list_id", Integer, ForeignKey("lists.id", ondelete="CASCADE"), primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lists = relationship("MovieList", back_populates="owner", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    year = Column(Integer)
    director = Column(String(128))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    tags = relationship("Tag", secondary=movie_tags, back_populates="movies")
    notes = relationship("Note", back_populates="movie", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    lists = relationship("MovieList", secondary=list_membership, back_populates="movies")

class MovieList(Base):
    __tablename__ = "lists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    is_custom = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    owner = relationship("User", back_populates="lists")
    movies = relationship("Movie", secondary=list_membership, back_populates="lists")

    __table_args__ = (UniqueConstraint("name", "owner_id", name="_uniq_user_list_name"),)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)

    movies = relationship("Movie", secondary=movie_tags, back_populates="tags")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="notes")
    movie = relationship("Movie", back_populates="notes")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    score = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")

class ModerationAction(Base):
    __tablename__ = "moderation_actions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Moderator/admin
    target_user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(128), nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
