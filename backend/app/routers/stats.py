from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.database import get_db
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/stats", tags=["统计"])

@router.get("/weekly")
def get_weekly(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT type, COUNT(*) as count FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? "
        "GROUP BY type",
        (current_user["sub"], week_start)
    )
    by_type = {r["type"]: r["count"] for r in cursor.fetchall()}

    cursor.execute(
        "SELECT date(checkin_time) as day, type, COUNT(*) as count FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? "
        "GROUP BY day, type ORDER BY day",
        (current_user["sub"], week_start)
    )
    daily = {}
    for r in cursor.fetchall():
        if r["day"] not in daily:
            daily[r["day"]] = {"early": 0, "reading": 0, "sport": 0}
        daily[r["day"]][r["type"]] = r["count"]

    conn.close()
    return {"by_type": by_type, "daily": daily, "total": sum(by_type.values())}

@router.get("/monthly")
def get_monthly(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT type, COUNT(*) as count FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? "
        "GROUP BY type",
        (current_user["sub"], month_start)
    )
    by_type = {r["type"]: r["count"] for r in cursor.fetchall()}

    cursor.execute(
        "SELECT strftime('%Y-%m-%d', checkin_time) as day, type, COUNT(*) as count FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? "
        "GROUP BY day, type ORDER BY day",
        (current_user["sub"], month_start)
    )
    daily = {}
    for r in cursor.fetchall():
        if r["day"] not in daily:
            daily[r["day"]] = {"early": 0, "reading": 0, "sport": 0}
        daily[r["day"]][r["type"]] = r["count"]

    conn.close()
    return {"by_type": by_type, "daily": daily, "total": sum(by_type.values())}

@router.get("/yearly")
def get_yearly(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    year_start = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT type, COUNT(*) as count FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? "
        "GROUP BY type",
        (current_user["sub"], year_start)
    )
    by_type = {r["type"]: r["count"] for r in cursor.fetchall()}

    cursor.execute(
        "SELECT strftime('%Y-%m', checkin_time) as month, type, COUNT(*) as count FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? "
        "GROUP BY month, type ORDER BY month",
        (current_user["sub"], year_start)
    )
    monthly = {}
    for r in cursor.fetchall():
        if r["month"] not in monthly:
            monthly[r["month"]] = {"early": 0, "reading": 0, "sport": 0}
        monthly[r["month"]][r["type"]] = r["count"]

    conn.close()
    return {"by_type": by_type, "monthly": monthly, "total": sum(by_type.values())}

@router.get("/rank")
def get_rank(current_user: dict = Depends(get_current_user), period: str = "weekly"):
    conn = get_db()
    cursor = conn.cursor()

    column = {"weekly": "weekly", "monthly": "monthly", "yearly": "yearly"}.get(period, "weekly")

    cursor.execute(
        "SELECT u.id, u.username, u.nickname, COALESCE(p.total, 0) as total, "
        "COALESCE(p.{}, 0) as period_score ".format(column) +
        "FROM users u LEFT JOIN points p ON u.id = p.user_id "
        "ORDER BY p.{} DESC LIMIT 50".format(column)
    )
    ranks = [dict(r) for r in cursor.fetchall()]

    offset = "-7 days" if period == "weekly" else "-30 days" if period == "monthly" else "-365 days"

    cursor.execute(
        "SELECT u.id, u.nickname, "
        "(SELECT COUNT(*) FROM checkins c WHERE c.user_id=u.id AND c.type='early' AND date(c.checkin_time) >= date('now', '{}')) as count ".format(offset) +
        "FROM users u ORDER BY count DESC LIMIT 10"
    )
    early_rank = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        "SELECT u.id, u.nickname, "
        "(SELECT COUNT(*) FROM checkins c WHERE c.user_id=u.id AND c.type='reading' AND date(c.checkin_time) >= date('now', '{}')) as count ".format(offset) +
        "FROM users u ORDER BY count DESC LIMIT 10"
    )
    reading_rank = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        "SELECT u.id, u.nickname, "
        "(SELECT COUNT(*) FROM checkins c WHERE c.user_id=u.id AND c.type='sport' AND date(c.checkin_time) >= date('now', '{}')) as count ".format(offset) +
        "FROM users u ORDER BY count DESC LIMIT 10"
    )
    sport_rank = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {"total": ranks, "early": early_rank, "reading": reading_rank, "sport": sport_rank}