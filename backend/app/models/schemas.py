from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str

class CheckinBase(BaseModel):
    notes: Optional[str] = ""
    audio_url: Optional[str] = ""
    photo_urls: Optional[str] = "[]"
    video_url: Optional[str] = ""

class EarlyCheckin(CheckinBase):
    pass

class ReadingCheckin(CheckinBase):
    book_id: Optional[int] = None
    reading_duration: int = 0
    audio_url: str = ""

class SportCheckin(CheckinBase):
    steps: int = 0
    sport_type: str = ""
    calories: int = 0
    photo_urls: str = "[]"
    video_url: str = ""

class BookCreate(BaseModel):
    title: str
    author: Optional[str] = ""
    total_pages: Optional[int] = 0

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    status: Optional[str] = None

class RuleUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    min_steps: Optional[int] = None
    required_media: Optional[str] = None
    points: Optional[int] = None
    enabled: Optional[int] = None

class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str
    role: Optional[str] = "member"

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
