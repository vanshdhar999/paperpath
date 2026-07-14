import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, ARRAY, DateTime, Date, Integer,
    ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, nullable=False)
    name = Column(String)
    username = Column(String, unique=True)
    domain_interests = Column(ARRAY(String), default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress = relationship("UserProgress", back_populates="user")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    arxiv_id = Column(String, unique=True, nullable=False)
    semantic_scholar_id = Column(String)
    title = Column(Text, nullable=False)
    authors = Column(ARRAY(String), default=list)
    abstract = Column(Text)
    pdf_url = Column(String)
    published_date = Column(Date)
    venue = Column(String)
    full_text = Column(Text)
    journey_cache = Column(JSON)
    quiz_cache = Column(JSON)
    embedding = Column(Vector(384))
    difficulty_tier = Column(String, nullable=False)  # beginner|intermediate|pro
    created_at = Column(DateTime, default=datetime.utcnow)

    prerequisites = relationship(
        "Prerequisite", foreign_keys="Prerequisite.paper_id", back_populates="paper"
    )
    required_by = relationship(
        "Prerequisite", foreign_keys="Prerequisite.prerequisite_paper_id",
        back_populates="prerequisite_paper"
    )
    progress = relationship("UserProgress", back_populates="paper")
    quiz = relationship("Quiz", back_populates="paper", uselist=False)


class Prerequisite(Base):
    __tablename__ = "prerequisites"

    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)
    prerequisite_paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)

    paper = relationship("Paper", foreign_keys=[paper_id], back_populates="prerequisites")
    prerequisite_paper = relationship(
        "Paper", foreign_keys=[prerequisite_paper_id], back_populates="required_by"
    )


class Track(Base):
    __tablename__ = "tracks"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    domain = Column(String, nullable=False)  # "ML/AI"
    name = Column(String, nullable=False)    # "Beginner" | "Intermediate" | "Pro"

    track_papers = relationship("TrackPaper", back_populates="track")


class TrackPaper(Base):
    __tablename__ = "track_papers"

    track_id = Column(UUID(as_uuid=False), ForeignKey("tracks.id"), primary_key=True)
    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)
    order_hint = Column(Integer, default=0)

    track = relationship("Track", back_populates="track_papers")
    paper = relationship("Paper")


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), primary_key=True)
    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)
    status = Column(String, default="locked")  # locked|unlocked|in_progress|completed
    quiz_score = Column(Integer)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="progress")
    paper = relationship("Paper", back_populates="progress")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), unique=True, nullable=False)
    questions = Column(JSON, nullable=False)  # [{question, options[], correct_index, explanation}]
    generated_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="quiz")
