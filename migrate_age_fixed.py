import os
import sys
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, predict_age, Comment

with app.app_context():
    print("=== FIXED Migration: Adding predicted_age column ===")
    
    # 1. Check if column exists
    # Use raw SQL since column added
    with db.engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(comment)"))
        columns = [row[1] for row in result.fetchall()]
        conn.commit()
    
    if 'predicted_age' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE comment ADD COLUMN predicted_age VARCHAR(50)"))
            conn.commit()
        print("✅ Added predicted_age column")
    else:
        print("ℹ️ Column predicted_age already exists")
    
    # Backfill existing comments (model now has field)
    comments = Comment.query.all()
    updated = 0
    for comment in comments:
        if getattr(comment, 'predicted_age', None) is None:
            age = predict_age(comment.text)
            comment.predicted_age = age
            db.session.commit()
            updated += 1
            print(f"Backfilled comment {comment.id}: {age}")
    
    print(f"✅ Migration complete. Updated {updated} comments.")

