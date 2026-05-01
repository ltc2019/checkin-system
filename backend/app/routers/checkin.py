from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from datetime import datetime, timedelta
import os, json, uuid
from app.database import get_db
from app.models.schemas import EarlyCheckin, ReadingCheckin, SportCheckin
from app.utils.deps import get_current_user
from app.routers.achievements import check_and_award_achievements

router = APIRouter(prefix="/api/checkin", tags=["打卡"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

@router.post("/early")
def early_checkin(data: EarlyCheckin, current_user: dict = Depends(get_current_user)):
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT start_time, end_time, points FROM rules WHERE type='early' AND enabled=1")
    rule = cursor.fetchone()

    if rule and not (rule["start_time"] <= current_time <= rule["end_time"]):
        conn.close()
        raise HTTPException(status_code=400, detail=f"打卡时间必须在 {rule['start_time']}-{rule['end_time']} 之间")

    today = now.strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT id FROM checkins WHERE user_id=? AND type='early' AND date(checkin_time)=?",
        (current_user["sub"], today)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="今日已打过早起卡")

    cursor.execute(
        "INSERT INTO checkins (user_id, type, notes) VALUES (?, 'early', ?)",
        (current_user["sub"], data.notes)
    )

    points = rule["points"] if rule else 1
    cursor.execute(
        "INSERT INTO points (user_id, total, weekly, monthly, yearly) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET total=total+?, weekly=weekly+?, monthly=monthly+?, yearly=yearly+?",
        (current_user["sub"], points, points, points, points, points, points, points, points)
    )

    cursor.execute(
        "SELECT COUNT(*) FROM checkins WHERE user_id=? AND type='early' AND checkin_time >= date('now', '-7 days')",
        (current_user["sub"],)
    )
    streak = cursor.fetchone()[0]

    awards = check_and_award_achievements(current_user["sub"], conn)

    conn.commit()
    conn.close()
    return {"message": "早起打卡成功", "points": points, "streak": streak + 1, "awards": awards}

@router.post("/reading")
def reading_checkin(data: ReadingCheckin, current_user: dict = Depends(get_current_user)):
    if not data.audio_url:
        raise HTTPException(status_code=400, detail="读书打卡需要上传录音")

    conn = get_db()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT id FROM checkins WHERE user_id=? AND type='reading' AND date(checkin_time)=?",
        (current_user["sub"], today)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="今日已打过读书卡")

    cursor.execute(
        "INSERT INTO checkins (user_id, type, notes, audio_url, book_id, reading_duration) "
        "VALUES (?, 'reading', ?, ?, ?, ?)",
        (current_user["sub"], data.notes, data.audio_url, data.book_id, data.reading_duration)
    )

    cursor.execute("SELECT points FROM rules WHERE type='reading' AND enabled=1")
    rule = cursor.fetchone()
    points = rule["points"] if rule else 1

    cursor.execute(
        "INSERT INTO points (user_id, total, weekly, monthly, yearly) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET total=total+?, weekly=weekly+?, monthly=monthly+?, yearly=yearly+?",
        (current_user["sub"], points, points, points, points, points, points, points, points)
    )

    if data.book_id:
        cursor.execute(
            "UPDATE books SET updated_at=datetime('now','localtime') WHERE id=? AND user_id=?",
            (data.book_id, current_user["sub"])
        )

    awards = check_and_award_achievements(current_user["sub"], conn)

    conn.commit()
    conn.close()
    return {"message": "读书打卡成功", "points": points, "awards": awards}

@router.post("/sport")
def sport_checkin(data: SportCheckin, current_user: dict = Depends(get_current_user)):
    if not data.photo_urls or data.photo_urls == "[]":
        raise HTTPException(status_code=400, detail="运动打卡需要上传照片或视频")

    conn = get_db()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT id FROM checkins WHERE user_id=? AND type='sport' AND date(checkin_time)=?",
        (current_user["sub"], today)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="今日已打过运动卡")

    cursor.execute(
        "INSERT INTO checkins (user_id, type, notes, photo_urls, video_url, steps, sport_type, calories) "
        "VALUES (?, 'sport', ?, ?, ?, ?, ?, ?)",
        (current_user["sub"], data.notes, data.photo_urls, data.video_url, data.steps, data.sport_type, data.calories)
    )

    cursor.execute("SELECT points, min_steps FROM rules WHERE type='sport' AND enabled=1")
    rule = cursor.fetchone()
    points = rule["points"] if rule else 1

    if rule and rule["min_steps"] > 0 and data.steps < rule["min_steps"]:
        conn.close()
        raise HTTPException(status_code=400, detail=f"步数需达到 {rule['min_steps']} 步")

    cursor.execute(
        "INSERT INTO points (user_id, total, weekly, monthly, yearly) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET total=total+?, weekly=weekly+?, monthly=monthly+?, yearly=yearly+?",
        (current_user["sub"], points, points, points, points, points, points, points, points)
    )

    awards = check_and_award_achievements(current_user["sub"], conn)

    conn.commit()
    conn.close()
    return {"message": "运动打卡成功", "points": points, "awards": awards}

@router.get("/today")
def get_today(current_user: dict = Depends(get_current_user)):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT type, checkin_time, notes FROM checkins WHERE user_id=? AND date(checkin_time)=?",
        (current_user["sub"], today)
    )
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {
        "early": next((r for r in records if r["type"] == "early"), None),
        "reading": [r for r in records if r["type"] == "reading"],
        "sport": [r for r in records if r["type"] == "sport"],
    }

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), folder: str = Form("photos")):
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = "{}.{}".format(uuid.uuid4().hex, ext)
    save_dir = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {"url": "/uploads/{}/{}".format(folder, filename)}

@router.get("/history")
def get_history(
    type: str = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()

    conditions = ["user_id=?"]
    params = [current_user["sub"]]

    if type:
        conditions.append("type=?")
        params.append(type)

    where = " AND ".join(conditions)
    params.extend([limit, offset])

    cursor.execute(
        f"SELECT * FROM checkins WHERE {where} ORDER BY checkin_time DESC LIMIT ? OFFSET ?",
        params
    )
    records = [dict(r) for r in cursor.fetchall()]

    cursor.execute(f"SELECT COUNT(*) FROM checkins WHERE {where}", params[:len(params)-2])
    total = cursor.fetchone()[0]

    conn.close()
    return {"records": records, "total": total, "limit": limit, "offset": offset}

@router.get("/record/{record_id}")
def get_record(record_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checkins WHERE id=? AND user_id=?", (record_id, current_user["sub"]))
    record = cursor.fetchone()
    conn.close()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return dict(record)

@router.delete("/record/{record_id}")
def delete_record(record_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checkins WHERE id=? AND user_id=?", (record_id, current_user["sub"]))
    record = cursor.fetchone()
    if not record:
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")

    record_time = datetime.strptime(record["checkin_time"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() - record_time > timedelta(hours=24):
        conn.close()
        raise HTTPException(status_code=400, detail="超过24小时，无法删除")

    cursor.execute("DELETE FROM checkins WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}