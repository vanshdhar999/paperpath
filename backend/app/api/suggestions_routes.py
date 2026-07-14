"""Suggestion routes — papers ranked by embedding similarity to user interests."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.models import User, Paper, UserProgress
from app.auth import get_current_user

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.get("")
async def get_suggestions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get paper suggestions ranked by embedding similarity to user's completed papers.
    Returns papers the user hasn't completed, ordered by relevance.
    """
    # Get completed paper IDs
    completed = (
        db.query(UserProgress.paper_id)
        .filter(UserProgress.user_id == user.id, UserProgress.status == "completed")
        .all()
    )
    completed_ids = {row[0] for row in completed}

    if not completed_ids:
        # No completed papers — suggest beginner papers
        papers = (
            db.query(Paper)
            .filter(Paper.difficulty_tier == "beginner", Paper.embedding.isnot(None))
            .limit(10)
            .all()
        )
        return [
            {
                "id": p.id,
                "arxiv_id": p.arxiv_id,
                "title": p.title,
                "authors": p.authors,
                "abstract": p.abstract[:200] + "..." if p.abstract and len(p.abstract) > 200 else p.abstract,
                "difficulty_tier": p.difficulty_tier,
                "venue": p.venue,
                "similarity": 0.0,
                "reason": "Recommended beginner paper",
            }
            for p in papers
        ]

    # Compute average embedding of completed papers
    completed_list = ",".join(f"'{cid}'" for cid in completed_ids)

    # Use pgvector cosine distance to find similar papers
    query = text(f"""
        WITH user_centroid AS (
            SELECT AVG(embedding) as centroid
            FROM papers
            WHERE id IN ({completed_list})
            AND embedding IS NOT NULL
        )
        SELECT p.id, p.arxiv_id, p.title, p.authors, p.abstract,
               p.difficulty_tier, p.venue,
               1 - (p.embedding <=> uc.centroid) as similarity
        FROM papers p, user_centroid uc
        WHERE p.embedding IS NOT NULL
        AND p.id NOT IN ({completed_list})
        ORDER BY p.embedding <=> uc.centroid
        LIMIT 10
    """)

    results = db.execute(query).fetchall()

    return [
        {
            "id": str(row[0]),
            "arxiv_id": row[1],
            "title": row[2],
            "authors": row[3],
            "abstract": row[4][:200] + "..." if row[4] and len(row[4]) > 200 else row[4],
            "difficulty_tier": row[5],
            "venue": row[6],
            "similarity": round(float(row[7]), 4) if row[7] else 0.0,
            "reason": "Similar to papers you've completed",
        }
        for row in results
    ]
