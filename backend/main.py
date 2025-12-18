from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import FastAPI
from . import crud
from backend import models
from . import schemas
from backend.database import SessionLocal, engine
from datetime import datetime
from backend import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="News API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper: format datetime to "dd.mm.YYYY HH:MM"
def fmt(dt):
    if not dt:
        return None
    return dt.strftime("%d.%m.%Y %H:%M")

@app.get("/posts")
def list_posts(db: Session = Depends(get_db)):
    posts = crud.get_posts(db)
    out = []
    for p in posts:
        out.append({
            "id": p.id,
            "author": p.author,
            "title": p.title,
            "content": p.content,
            "image_url": p.image_url,
            "created_at": fmt(p.created_at),
            "likes": p.likes
        })
    return out

@app.get("/posts/{post_id}")
def read_post(post_id: int, db: Session = Depends(get_db)):
    p = crud.get_post(db, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": p.id,
        "author": p.author,
        "title": p.title,
        "content": p.content,
        "image_url": p.image_url,
        "created_at": fmt(p.created_at),
        "likes": p.likes
    }

@app.post("/posts")
def create_new_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    p = crud.create_post(db, post)
    return {
        "id": p.id,
        "author": p.author,
        "title": p.title,
        "content": p.content,
        "image_url": p.image_url,
        "created_at": fmt(p.created_at),
        "likes": p.likes
    }

@app.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    p = crud.like_post(db, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": p.id, "likes": p.likes}

# COMMENTS
@app.get("/posts/{post_id}/comments")
def list_comments(post_id: int, db: Session = Depends(get_db)):
    if not crud.get_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    coms = crud.get_comments(db, post_id)
    out = []
    for c in coms:
        out.append({
            "id": c.id,
            "post_id": c.post_id,
            "author": c.author,
            "content": c.content,
            "created_at": fmt(c.created_at),
            "likes": c.likes
        })
    return out

@app.post("/posts/{post_id}/comments")
def add_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    if not crud.get_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    c = crud.create_comment(db, post_id, comment)
    return {
        "id": c.id,
        "post_id": c.post_id,
        "author": c.author,
        "content": c.content,
        "created_at": fmt(c.created_at),
        "likes": c.likes
    }

@app.post("/comments/{comment_id}/like")
def like_comment(comment_id: int, db: Session = Depends(get_db)):
    c = crud.like_comment(db, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"id": c.id, "likes": c.likes}
