from fastapi import APIRouter, Depends
from app.database import get_db
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/achievements", tags=["成就"])

ACHIEVEMENTS = {
    "early_7": {"name": "早起鸟·初级", "desc": "连续早起7天", "icon": "🌅", "level": 1},
    "early_14": {"name": "早起鸟·中级", "desc": "连续早起14天", "icon": "🌅", "level": 2},
    "early_30": {"name": "早起鸟·高级", "desc": "连续早起30天", "icon": "🌅", "level": 3},
    "early_100": {"name": "早起鸟·大师", "desc": "连续早起100天", "icon": "🌅", "level": 4},
    "reading_10": {"name": "书虫·初级", "desc": "累计读书打卡10次", "icon": "📚", "level": 1},
    "reading_50": {"name": "书虫·中级", "desc": "累计读书打卡50次", "icon": "📚", "level": 2},
    "reading_100": {"name": "书虫·高级", "desc": "累计读书打卡100次", "icon": "📚", "level": 3},
    "reading_365": {"name": "书虫·大师", "desc": "累计读书打卡365次", "icon": "📚", "level": 4},
    "sport_10": {"name": "运动达人·初级", "desc": "累计运动打卡10次", "icon": "🏃", "level": 1},
    "sport_50": {"name": "运动达人·中级", "desc": "累计运动打卡50次", "icon": "🏃", "level": 2},
    "sport_100": {"name": "运动达人·高级", "desc": "累计运动打卡100次", "icon": "🏃", "level": 3},
    "sport_365": {"name": "运动达人·大师", "desc": "累计运动打卡365次", "icon": "🏃", "level": 4},
    "all_1": {"name": "全能选手·初级", "desc": "单日三项全打卡1次", "icon": "✨", "level": 1},
    "all_10": {"name": "全能选手·中级", "desc": "单日三项全打卡10次", "icon": "✨", "level": 2},
    "all_50": {"name": "全能选手·高级", "desc": "单日三项全打卡50次", "icon": "✨", "level": 3},
    "total_100": {"name": "坚持者·初级", "desc": "总打卡100次", "icon": "🏆", "level": 1},
    "total_365": {"name": "坚持者·中级", "desc": "总打卡365次", "icon": "🏆", "level": 2},
    "total_1000": {"name": "坚持者·大师", "desc": "总打卡1000次", "icon": "🏆", "level": 3},
}

@router.get("")
def get_user_achievements(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT type, level, achieved_at FROM achievements WHERE user_id=?",
        (current_user["sub"],)
    )
    achieved = [dict(r) for r in cursor.fetchall()]

    result = []
    for a in achieved:
        info = ACHIEVEMENTS.get(a["type"], {})
        result.append({
            "type": a["type"],
            "name": info.get("name", a["type"]),
            "desc": info.get("desc", ""),
            "icon": info.get("icon", "🏅"),
            "level": a["level"],
            "achieved_at": a["achieved_at"]
        })

    conn.close()
    return result

@router.get("/all")
def get_all_achievements(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT type FROM achievements WHERE user_id=?", (current_user["sub"],))
    achieved_types = [r["type"] for r in cursor.fetchall()]
    conn.close()

    result = []
    for type_key, info in ACHIEVEMENTS.items():
        result.append({
            "type": type_key,
            "name": info["name"],
            "desc": info["desc"],
            "icon": info["icon"],
            "level": info["level"],
            "achieved": type_key in achieved_types
        })

    return result

def check_and_award_achievements(user_id: int, conn):
    from datetime import datetime, timedelta
    cursor = conn.cursor()

    awards = []

    # 早起连续天数
    cursor.execute(
        "SELECT DISTINCT date(checkin_time) as day FROM checkins "
        "WHERE user_id=? AND type='early' ORDER BY day DESC LIMIT 100",
        (user_id,)
    )
    early_days = [r["day"] for r in cursor.fetchall()]

    early_streak = 0
    for i, day in enumerate(early_days):
        expected = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if day == expected:
            early_streak += 1
        else:
            break

    # 检查早起成就
    for threshold, type_key in [(7, "early_7"), (14, "early_14"), (30, "early_30"), (100, "early_100")]:
        if early_streak >= threshold:
            cursor.execute("SELECT 1 FROM achievements WHERE user_id=? AND type=?", (user_id, type_key))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO achievements (user_id, type) VALUES (?, ?)", (user_id, type_key))
                awards.append(type_key)

    # 累计打卡次数
    cursor.execute("SELECT type, COUNT(*) as count FROM checkins WHERE user_id=? GROUP BY type", (user_id,))
    counts = {r["type"]: r["count"] for r in cursor.fetchall()}

    reading_count = counts.get("reading", 0)
    sport_count = counts.get("sport", 0)

    for threshold, type_key in [(10, "reading_10"), (50, "reading_50"), (100, "reading_100"), (365, "reading_365")]:
        if reading_count >= threshold:
            cursor.execute("SELECT 1 FROM achievements WHERE user_id=? AND type=?", (user_id, type_key))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO achievements (user_id, type) VALUES (?, ?)", (user_id, type_key))
                awards.append(type_key)

    for threshold, type_key in [(10, "sport_10"), (50, "sport_50"), (100, "sport_100"), (365, "sport_365")]:
        if sport_count >= threshold:
            cursor.execute("SELECT 1 FROM achievements WHERE user_id=? AND type=?", (user_id, type_key))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO achievements (user_id, type) VALUES (?, ?)", (user_id, type_key))
                awards.append(type_key)

    # 单日三项全打卡
    cursor.execute(
        "SELECT date(checkin_time) as day, COUNT(DISTINCT type) as types FROM checkins "
        "WHERE user_id=? GROUP BY day HAVING types=3",
        (user_id,)
    )
    all_days_count = len(cursor.fetchall())

    for threshold, type_key in [(1, "all_1"), (10, "all_10"), (50, "all_50")]:
        if all_days_count >= threshold:
            cursor.execute("SELECT 1 FROM achievements WHERE user_id=? AND type=?", (user_id, type_key))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO achievements (user_id, type) VALUES (?, ?)", (user_id, type_key))
                awards.append(type_key)

    # 总打卡次数
    total_count = sum(counts.values())

    for threshold, type_key in [(100, "total_100"), (365, "total_365"), (1000, "total_1000")]:
        if total_count >= threshold:
            cursor.execute("SELECT 1 FROM achievements WHERE user_id=? AND type=?", (user_id, type_key))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO achievements (user_id, type) VALUES (?, ?)", (user_id, type_key))
                awards.append(type_key)

    return awards