from sqlalchemy.orm import Session
from database import Comment
from typing import List, Optional

def create_comment(db: Session, content: str) -> Comment:
    """
    Create a new comment
    """
    db_comment = Comment(content=content)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    """
    Get a single comment by ID
    """
    return db.query(Comment).filter(Comment.id == comment_id).first()

def get_comments(db: Session, skip: int = 0, limit: int = 100) -> List[Comment]:
    """
    Get a list of comments with pagination
    """
    return db.query(Comment).offset(skip).limit(limit).all()

def update_comment(db: Session, comment_id: int, content: str) -> Optional[Comment]:
    """
    Update a comment
    """
    db_comment = get_comment(db, comment_id)
    if db_comment:
        db_comment.content = content
        db.commit()
        db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int) -> bool:
    """
    Delete a comment
    """
    db_comment = get_comment(db, comment_id)
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False
