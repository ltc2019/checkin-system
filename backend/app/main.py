from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sys, os
sys.path.insert(0, '.')

from app.database import init_db
from app.routers import auth, checkin, books, stats, admin, achievements, export

init_db()

app = FastAPI(title="打卡签到系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(books.router)
app.include_router(stats.router)
app.include_router(admin.router)
app.include_router(achievements.router)
app.include_router(export.router)

@app.get("/")
def root():
    return {"message": "打卡签到系统 API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}