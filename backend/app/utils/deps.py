from fastapi import Depends, HTTPException, Header
from app.database import get_db
from app.utils.auth import decode_token

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")
    payload = decode_token(authorization[7:])
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期")
    return payload

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user