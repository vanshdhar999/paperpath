"""Paper routes — journey view, quiz, quiz submission."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Paper, UserProgress, Prerequisite, Quiz, User
from app.auth import get_current_user
from app.services.claude_service import restructure_paper, generate_quiz

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/{paper_id}/journey")
async def get_paper_journey(paper_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get the LLM-restructured journey view for a paper. Generates and caches on first request."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Check if paper is accessible (not locked)
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id, UserProgress.paper_id == paper_id
    ).first()

    prereqs = db.query(Prerequisite).filter(Prerequisite.paper_id == paper_id).all()
    if prereqs and not progress:
        all_complete = all(
            db.query(UserProgress).filter(
                UserProgress.user_id == user.id,
                UserProgress.paper_id == p.prerequisite_paper_id,
                UserProgress.status == "completed",
            ).first() is not None
            for p in prereqs
        )
        if not all_complete:
            raise HTTPException(status_code=403, detail="Paper is locked. Complete prerequisites first.")

    # Mark as in_progress if not already
    if not progress:
        progress = UserProgress(user_id=user.id, paper_id=paper_id, status="in_progress")
        db.add(progress)
        db.commit()
    elif progress.status == "unlocked":
        progress.status = "in_progress"
        db.commit()

    # Generate journey if not cached
    if not paper.journey_cache:
        journey = restructure_paper(
            title=paper.title,
            abstract=paper.abstract or "",
            full_text=paper.full_text or "",
        )
        paper.journey_cache = journey
        db.commit()

    return {
        "paper": {
            "id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "venue": paper.venue,
            "pdf_url": paper.pdf_url,
        },
        "journey": paper.journey_cache,
        "status": progress.status if progress else "unlocked",
    }


@router.get("/{paper_id}/quiz")
async def get_paper_quiz(paper_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get quiz questions for a paper. Generates and caches on first request."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Generate quiz if not cached
    quiz = db.query(Quiz).filter(Quiz.paper_id == paper_id).first()
    if not quiz:
        if not paper.journey_cache:
            journey = restructure_paper(
                title=paper.title,
                abstract=paper.abstract or "",
                full_text=paper.full_text or "",
            )
            paper.journey_cache = journey
            db.commit()

        questions = generate_quiz(
            title=paper.title,
            abstract=paper.abstract or "",
            journey=paper.journey_cache,
        )
        quiz = Quiz(paper_id=paper_id, questions=questions)
        db.add(quiz)
        paper.quiz_cache = questions
        db.commit()

    return {
        "paper_id": paper_id,
        "title": paper.title,
        "questions": [
            {
                "question": q["question"],
                "options": q["options"],
                # Don't send correct_index to client
            }
            for q in quiz.questions
        ],
    }


@router.post("/{paper_id}/quiz/submit")
async def submit_quiz(
    paper_id: str,
    answers: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Grade a quiz submission. Body: {"answers": [0, 1, 2, ...]}
    Passing = 3/5 correct. Updates user_progress and triggers unlocks.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    quiz = db.query(Quiz).filter(Quiz.paper_id == paper_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found. View the paper journey first.")

    user_answers = answers.get("answers", [])
    if len(user_answers) != len(quiz.questions):
        raise HTTPException(status_code=400, detail=f"Expected {len(quiz.questions)} answers")

    # Grade
    correct = sum(
        1
        for i, q in enumerate(quiz.questions)
        if i < len(user_answers) and user_answers[i] == q["correct_index"]
    )
    total = len(quiz.questions)
    passed = correct >= 3  # 3/5 to pass

    # Update progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user.id, UserProgress.paper_id == paper_id
    ).first()

    if not progress:
        progress = UserProgress(user_id=user.id, paper_id=paper_id)
        db.add(progress)

    progress.quiz_score = correct
    if passed:
        progress.status = "completed"
        progress.completed_at = datetime.utcnow()

    db.commit()

    # Trigger unlocks for papers that depend on this one
    unlocked = []
    if passed:
        dependents = db.query(Prerequisite).filter(
            Prerequisite.prerequisite_paper_id == paper_id
        ).all()
        for dep in dependents:
            # Check if all prerequisites for this dependent are complete
            all_prereqs = db.query(Prerequisite).filter(
                Prerequisite.paper_id == dep.paper_id
            ).all()
            all_complete = all(
                db.query(UserProgress).filter(
                    UserProgress.user_id == user.id,
                    UserProgress.paper_id == p.prerequisite_paper_id,
                    UserProgress.status == "completed",
                ).first() is not None
                for p in all_prereqs
            )
            if all_complete:
                dep_progress = db.query(UserProgress).filter(
                    UserProgress.user_id == user.id,
                    UserProgress.paper_id == dep.paper_id,
                ).first()
                if not dep_progress:
                    dep_progress = UserProgress(
                        user_id=user.id, paper_id=dep.paper_id, status="unlocked"
                    )
                    db.add(dep_progress)
                    unlocked.append(dep.paper_id)
                elif dep_progress.status == "locked":
                    dep_progress.status = "unlocked"
                    unlocked.append(dep.paper_id)
        db.commit()

    return {
        "correct": correct,
        "total": total,
        "passed": passed,
        "score_percent": round(correct / total * 100),
        "unlocked_papers": unlocked,
        "explanations": [
            {
                "question": q["question"],
                "correct_index": q["correct_index"],
                "user_answer": user_answers[i] if i < len(user_answers) else None,
                "is_correct": i < len(user_answers) and user_answers[i] == q["correct_index"],
                "explanation": q["explanation"],
            }
            for i, q in enumerate(quiz.questions)
        ],
    }
