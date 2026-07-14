"""Auth routes — sync Supabase user to our DB."""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync-user")
async def sync_user(request: Request, db: Session = Depends(get_db)):
    """Create or update a user row from the Supabase JWT."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split(" ", 1)[1]

    # Verify token with Supabase
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_service_role_key},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    supabase_user = resp.json()
    user_id = supabase_user["id"]
    email = supabase_user.get("email", "")
    name = supabase_user.get("user_metadata", {}).get("name", "")
    username = email.split("@")[0] if email else user_id[:8]

    existing = db.query(User).filter(User.id == user_id).first()
    if existing:
        return {"status": "exists", "user_id": user_id}

    user = User(
        id=user_id,
        email=email,
        name=name,
        username=username,
        domain_interests=["ML/AI"],
    )
    db.add(user)
    db.commit()

    return {"status": "created", "user_id": user_id}
