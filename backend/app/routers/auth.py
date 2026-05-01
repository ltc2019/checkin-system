from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.schemas import LoginRequest, RegisterRequest
from app.utils.auth import hash_password, verify_password, create_token
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, role FROM users WHERE username=?", (data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {
        "token": create_token(user["id"], data.username, user["role"]),
        "user": {"id": user["id"], "username": data.username, "role": user["role"]}
    }

@router.post("/register")
def register(data: RegisterRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")

    cursor.execute(
        "INSERT INTO users (username, password_hash, nickname) VALUES (?, ?, ?)",
        (data.username, hash_password(data.password), data.nickname)
    )
    user_id = cursor.lastrowid
    cursor.execute("INSERT INTO points (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    return {"token": create_token(user_id, data.username, "member"), "user": {"id": user_id, "username": data.username, "role": "member"}}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nickname, avatar, role FROM users WHERE id=?", (current_user["sub"],))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(user)