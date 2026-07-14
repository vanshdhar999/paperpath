"""Public profile routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, UserProgress, Paper

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    """Get a user's public profile — completed papers and stats."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    completed = (
        db.query(UserProgress, Paper)
        .join(Paper, UserProgress.paper_id == Paper.id)
        .filter(UserProgress.user_id == user.id, UserProgress.status == "completed")
        .all()
    )

    # Build contribution data (date → count)
    contributions: dict[str, int] = {}
    for progress, paper in completed:
        if progress.completed_at:
            date_str = progress.completed_at.strftime("%Y-%m-%d")
            contributions[date_str] = contributions.get(date_str, 0) + 1

    completed_papers = [
        {
            "id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "difficulty_tier": paper.difficulty_tier,
            "venue": paper.venue,
            "quiz_score": progress.quiz_score,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        }
        for progress, paper in completed
    ]

    return {
        "username": user.username,
        "name": user.name,
        "domain_interests": user.domain_interests,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "stats": {
            "total_completed": len(completed_papers),
            "beginner": sum(1 for p in completed_papers if p["difficulty_tier"] == "beginner"),
            "intermediate": sum(1 for p in completed_papers if p["difficulty_tier"] == "intermediate"),
            "pro": sum(1 for p in completed_papers if p["difficulty_tier"] == "pro"),
        },
        "completed_papers": completed_papers,
        "contributions": contributions,
    }
