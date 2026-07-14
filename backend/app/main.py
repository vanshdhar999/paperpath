from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth_routes import router as auth_router
from app.api.tracks_routes import router as tracks_router
from app.api.papers_routes import router as papers_router
from app.api.profile_routes import router as profile_router
from app.api.suggestions_routes import router as suggestions_router
from app.services.scheduler_service import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Paperpath API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tracks_router)
app.include_router(papers_router)
app.include_router(profile_router)
app.include_router(suggestions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
