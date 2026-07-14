"""Track and paper listing routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Track, TrackPaper, Paper, Prerequisite, UserProgress, User
from app.auth import get_current_user

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("")
def list_tracks(db: Session = Depends(get_db)):
    """List all tracks."""
    tracks = db.query(Track).all()
    return [
        {
            "id": t.id,
            "domain": t.domain,
            "name": t.name,
            "paper_count": db.query(TrackPaper).filter(TrackPaper.track_id == t.id).count(),
        }
        for t in tracks
    ]


@router.get("/{track_id}/papers")
async def get_track_papers(track_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all papers in a track with the user's unlock status."""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    track_papers = (
        db.query(TrackPaper, Paper)
        .join(Paper, TrackPaper.paper_id == Paper.id)
        .filter(TrackPaper.track_id == track_id)
        .order_by(TrackPaper.order_hint)
        .all()
    )

    result = []
    for tp, paper in track_papers:
        # Get user progress
        progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == user.id, UserProgress.paper_id == paper.id)
            .first()
        )

        # Determine status
        if progress:
            status = progress.status
        else:
            # Check prerequisites
            prereqs = db.query(Prerequisite).filter(Prerequisite.paper_id == paper.id).all()
            if not prereqs:
                status = "unlocked"  # No prerequisites = unlocked
            else:
                all_complete = all(
                    db.query(UserProgress)
                    .filter(
                        UserProgress.user_id == user.id,
                        UserProgress.paper_id == p.prerequisite_paper_id,
                        UserProgress.status == "completed",
                    )
                    .first()
                    is not None
                    for p in prereqs
                )
                status = "unlocked" if all_complete else "locked"

        # Get prerequisite paper IDs for graph visualization
        prereq_ids = [
            p.prerequisite_paper_id
            for p in db.query(Prerequisite).filter(Prerequisite.paper_id == paper.id).all()
        ]

        result.append({
            "id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract[:200] + "..." if paper.abstract and len(paper.abstract) > 200 else paper.abstract,
            "difficulty_tier": paper.difficulty_tier,
            "venue": paper.venue,
            "status": status,
            "quiz_score": progress.quiz_score if progress else None,
            "prerequisite_ids": prereq_ids,
            "order": tp.order_hint,
        })

    return {"track": {"id": track.id, "domain": track.domain, "name": track.name}, "papers": result}
