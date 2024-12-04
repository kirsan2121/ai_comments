from database import SessionLocal, init_db
import crud

def main():
    # Initialize database
    init_db()
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create a comment
        comment = crud.create_comment(db, "This is a test comment!")
        print(f"Created comment: {comment.id}")
        
        # Get all comments
        comments = crud.get_comments(db)
        print(f"All comments: {comments}")
        
        # Update the comment
        updated_comment = crud.update_comment(db, comment.id, "This is an updated comment!")
        print(f"Updated comment: {updated_comment.content}")
        
        # Delete the comment
        deleted = crud.delete_comment(db, comment.id)
        print(f"Comment deleted: {deleted}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
