from fastapi import APIRouter, Depends
from fastapi.responses import Response
from app.database import get_db
from app.utils.deps import get_current_user
import json

router = APIRouter(prefix="/api/export", tags=["导出"])

@router.get("/csv")
def export_csv(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, type, checkin_time, notes, steps, reading_duration, sport_type, calories, book_id "
        "FROM checkins WHERE user_id=? ORDER BY checkin_time DESC",
        (current_user["sub"],)
    )
    records = cursor.fetchall()
    conn.close()

    lines = ["id,type,checkin_time,notes,steps,reading_duration,sport_type,calories,book_id"]
    for r in records:
        notes = r["notes"].replace(",", "，").replace("\n", " ") if r["notes"] else ""
        lines.append(f"{r['id']},{r['type']},{r['checkin_time']},\"{notes}\",{r['steps'] or 0},{r['reading_duration'] or 0},{r['sport_type'] or ''},{r['calories'] or 0},{r['book_id'] or ''}")

    csv_content = "\n".join(lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=checkin_records.csv"}
    )

@router.get("/json")
def export_json(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM checkins WHERE user_id=? ORDER BY checkin_time DESC",
        (current_user["sub"],)
    )
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return Response(
        content=json.dumps(records, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=checkin_records.json"}
    )