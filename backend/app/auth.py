"""Supabase JWT verification and current-user dependency."""
import httpx
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.db.models import User


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Extract and verify Supabase JWT, return the User row."""
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

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Call /auth/sync-user first.")

    return user
