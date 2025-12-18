from pydantic import BaseModel
from typing import Optional

class PostCreate(BaseModel):
    author: str
    title: str
    content: str
    image_url: Optional[str] = None

class CommentCreate(BaseModel):
    author: str
    content: str
