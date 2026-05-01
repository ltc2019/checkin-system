from fastapi import APIRouter, Depends, Query
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

    # 根据周期计算日期范围
    if period == "daily":
        date_filter = "date(checkin_time) = date('now')"
    elif period == "weekly":
        date_filter = "date(checkin_time) >= date('now', '-7 days')"
    elif period == "monthly":
        date_filter = "date(checkin_time) >= date('now', '-30 days')"
    elif period == "yearly":
        date_filter = "date(checkin_time) >= date('now', '-365 days')"
    else:
        date_filter = "date(checkin_time) >= date('now', '-7 days')"

    # 获取所有用户
    cursor.execute("SELECT id, username, nickname FROM users")
    users = cursor.fetchall()

    # 计算每个用户的打卡次数
    ranks = []
    for u in users:
        cursor.execute(
            f"SELECT type, COUNT(*) as count FROM checkins WHERE user_id=? AND {date_filter} GROUP BY type",
            (u["id"],)
        )
        counts = {r["type"]: r["count"] for r in cursor.fetchall()}
        early = counts.get("early", 0)
        reading = counts.get("reading", 0)
        sport = counts.get("sport", 0)
        total = early + reading + sport
        ranks.append({
            "id": u["id"],
            "username": u["username"],
            "nickname": u["nickname"] or u["username"],
            "early": early,
            "reading": reading,
            "sport": sport,
            "total": total
        })

    # 按总数排序
    ranks.sort(key=lambda x: x["total"], reverse=True)

    # 分项排行
    early_rank = sorted(ranks, key=lambda x: x["early"], reverse=True)[:10]
    reading_rank = sorted(ranks, key=lambda x: x["reading"], reverse=True)[:10]
    sport_rank = sorted(ranks, key=lambda x: x["sport"], reverse=True)[:10]

    conn.close()
    return {"total": ranks[:50], "early": early_rank, "reading": reading_rank, "sport": sport_rank}

@router.get("/calendar")
def get_calendar(
    year: int = Query(None),
    month: int = Query(None),
    current_user: dict = Depends(get_current_user)
):
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date(checkin_time) as day, type FROM checkins "
        "WHERE user_id=? AND date(checkin_time) >= ? AND date(checkin_time) <= ?",
        (current_user["sub"], start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    )

    calendar = {}
    for r in cursor.fetchall():
        day = r["day"]
        if day not in calendar:
            calendar[day] = {"early": False, "reading": False, "sport": False}
        calendar[day][r["type"]] = True

    conn.close()
    return {"year": year, "month": month, "calendar": calendar}

@router.get("/streak")
def get_streak(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    # 当前连续早起天数
    cursor.execute(
        "SELECT DISTINCT date(checkin_time) as day FROM checkins "
        "WHERE user_id=? AND type='early' "
        "ORDER BY day DESC",
        (current_user["sub"],)
    )
    early_days = [r["day"] for r in cursor.fetchall()]

    early_streak = 0
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    if early_days:
        check_date = today if early_days[0] == today else yesterday
        for i, day in enumerate(early_days):
            expected = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if day == expected:
                early_streak += 1
            else:
                break

    # 当前连续总打卡天数
    cursor.execute(
        "SELECT DISTINCT date(checkin_time) as day FROM checkins "
        "WHERE user_id=? "
        "ORDER BY day DESC",
        (current_user["sub"],)
    )
    all_days = [r["day"] for r in cursor.fetchall()]

    total_streak = 0
    if all_days:
        for i, day in enumerate(all_days):
            expected = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if day == expected:
                total_streak += 1
            else:
                break

    # 最长连续天数
    max_streak = 0
    if all_days:
        temp_streak = 1
        for i in range(1, len(all_days)):
            prev = datetime.strptime(all_days[i-1], "%Y-%m-%d")
            curr = datetime.strptime(all_days[i], "%Y-%m-%d")
            if (prev - curr).days == 1:
                temp_streak += 1
            else:
                max_streak = max(max_streak, temp_streak)
                temp_streak = 1
        max_streak = max(max_streak, temp_streak)

    conn.close()
    return {
        "early_streak": early_streak,
        "total_streak": total_streak,
        "max_streak": max_streak
    }

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()

    # 基本信息
    cursor.execute("SELECT id, username, nickname, avatar, role, created_at FROM users WHERE id=?", (current_user["sub"],))
    user = dict(cursor.fetchone())

    # 总打卡次数
    cursor.execute("SELECT COUNT(*) FROM checkins WHERE user_id=?", (current_user["sub"],))
    total_checkins = cursor.fetchone()[0]

    # 各类型打卡次数
    cursor.execute(
        "SELECT type, COUNT(*) as count FROM checkins WHERE user_id=? GROUP BY type",
        (current_user["sub"],)
    )
    by_type = {r["type"]: r["count"] for r in cursor.fetchall()}

    # 总积分
    cursor.execute("SELECT total FROM points WHERE user_id=?", (current_user["sub"],))
    points_row = cursor.fetchone()
    total_points = points_row["total"] if points_row else 0

    # 本周打卡
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT COUNT(*) FROM checkins WHERE user_id=? AND date(checkin_time) >= ?",
        (current_user["sub"], week_start)
    )
    weekly_checkins = cursor.fetchone()[0]

    # 本月打卡
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT COUNT(*) FROM checkins WHERE user_id=? AND date(checkin_time) >= ?",
        (current_user["sub"], month_start)
    )
    monthly_checkins = cursor.fetchone()[0]

    # 连续天数
    cursor.execute(
        "SELECT DISTINCT date(checkin_time) as day FROM checkins WHERE user_id=? ORDER BY day DESC LIMIT 365",
        (current_user["sub"],)
    )
    all_days = [r["day"] for r in cursor.fetchall()]

    current_streak = 0
    max_streak = 0
    if all_days:
        for i, day in enumerate(all_days):
            expected = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if day == expected:
                current_streak += 1
            else:
                break

        temp_streak = 1
        for i in range(1, len(all_days)):
            prev = datetime.strptime(all_days[i-1], "%Y-%m-%d")
            curr = datetime.strptime(all_days[i], "%Y-%m-%d")
            if (prev - curr).days == 1:
                temp_streak += 1
            else:
                max_streak = max(max_streak, temp_streak)
                temp_streak = 1
        max_streak = max(max_streak, temp_streak)

    conn.close()
    return {
        "user": user,
        "total_checkins": total_checkins,
        "by_type": {"early": by_type.get("early", 0), "reading": by_type.get("reading", 0), "sport": by_type.get("sport", 0)},
        "total_points": total_points,
        "weekly_checkins": weekly_checkins,
        "monthly_checkins": monthly_checkins,
        "current_streak": current_streak,
        "max_streak": max_streak
    }