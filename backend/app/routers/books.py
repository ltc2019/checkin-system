from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.schemas import BookCreate, BookUpdate
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/books", tags=["书籍"])

@router.get("")
def get_books(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM books WHERE user_id=? ORDER BY updated_at DESC",
        (current_user["sub"],)
    )
    books = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return books

@router.post("")
def create_book(data: BookCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (user_id, title, author, total_pages) VALUES (?, ?, ?, ?)",
        (current_user["sub"], data.title, data.author, data.total_pages)
    )
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": book_id, "message": "添加成功"}

@router.put("/{book_id}")
def update_book(book_id: int, data: BookUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM books WHERE id=? AND user_id=?", (book_id, current_user["sub"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="书籍不存在")

    updates = []
    params = []
    if data.title is not None:
        updates.append("title=?")
        params.append(data.title)
    if data.author is not None:
        updates.append("author=?")
        params.append(data.author)
    if data.total_pages is not None:
        updates.append("total_pages=?")
        params.append(data.total_pages)
    if data.current_page is not None:
        updates.append("current_page=?")
        params.append(data.current_page)
    if data.status is not None:
        updates.append("status=?")
        params.append(data.status)

    if updates:
        updates.append("updated_at=datetime('now','localtime')")
        params.extend([book_id, current_user["sub"]])
        cursor.execute("UPDATE books SET {} WHERE id=? AND user_id=?".format(", ".join(updates)), params)
        conn.commit()

    conn.close()
    return {"message": "更新成功"}

@router.delete("/{book_id}")
def delete_book(book_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, current_user["sub"]))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}