from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.schemas import UserCreate, UserUpdate, RuleUpdate
from app.utils.deps import get_current_user, require_admin
from app.utils.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["管理"])

@router.get("/users")
def get_users(current_user: dict = Depends(require_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nickname, avatar, role, created_at FROM users ORDER BY id")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return users

@router.post("/users")
def create_user(data: UserCreate, current_user: dict = Depends(require_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")

    cursor.execute(
        "INSERT INTO users (username, password_hash, nickname, role) VALUES (?, ?, ?, ?)",
        (data.username, hash_password(data.password), data.nickname, data.role)
    )
    user_id = cursor.lastrowid
    cursor.execute("INSERT INTO points (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return {"id": user_id, "message": "创建成功"}

@router.put("/users/{user_id}")
def update_user(user_id: int, data: UserUpdate, current_user: dict = Depends(require_admin)):
    conn = get_db()
    cursor = conn.cursor()

    updates = []
    params = []
    if data.nickname is not None:
        updates.append("nickname=?")
        params.append(data.nickname)
    if data.role is not None:
        updates.append("role=?")
        params.append(data.role)
    if data.password is not None:
        updates.append("password_hash=?")
        params.append(hash_password(data.password))

    if updates:
        params.append(user_id)
        cursor.execute("UPDATE users SET {} WHERE id=?".format(", ".join(updates)), params)
        conn.commit()

    conn.close()
    return {"message": "更新成功"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(require_admin)):
    if user_id == int(current_user["sub"]):
        raise HTTPException(status_code=400, detail="不能删除自己")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM points WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM checkins WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM books WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.get("/rules")
def get_rules(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rules")
    rules = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rules

@router.put("/rules/{rule_type}")
def update_rule(rule_type: str, data: RuleUpdate, current_user: dict = Depends(require_admin)):
    conn = get_db()
    cursor = conn.cursor()

    updates = []
    params = []
    if data.start_time is not None:
        updates.append("start_time=?")
        params.append(data.start_time)
    if data.end_time is not None:
        updates.append("end_time=?")
        params.append(data.end_time)
    if data.min_steps is not None:
        updates.append("min_steps=?")
        params.append(data.min_steps)
    if data.required_media is not None:
        updates.append("required_media=?")
        params.append(data.required_media)
    if data.points is not None:
        updates.append("points=?")
        params.append(data.points)
    if data.enabled is not None:
        updates.append("enabled=?")
        params.append(data.enabled)

    if updates:
        params.append(rule_type)
        cursor.execute("UPDATE rules SET {} WHERE type=?".format(", ".join(updates)), params)
        conn.commit()

    conn.close()
    return {"message": "更新成功"}