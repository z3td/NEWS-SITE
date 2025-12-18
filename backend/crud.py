from sqlalchemy.orm import Session
from . import models
from . import schemas
from .database import SessionLocal, engine
from datetime import datetime

def get_posts(db: Session):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(
        author=post.author,
        title=post.title,
        content=post.content,
        image_url=post.image_url
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def like_post(db: Session, post_id: int):
    p = db.query(models.Post).filter(models.Post.id == post_id).first()
    if p:
        p.likes += 1
        db.commit()
        db.refresh(p)
    return p

# COMMENTS
def get_comments(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.created_at.asc()).all()

def create_comment(db: Session, post_id: int, comment: schemas.CommentCreate):
    db_comment = models.Comment(
        post_id=post_id,
        author=comment.author,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def like_comment(db: Session, comment_id: int):
    com = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if com:
        com.likes += 1
        db.commit()
        db.refresh(com)
    return com