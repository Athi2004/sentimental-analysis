import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, predict_age, Comment

with app.app_context():
    print("=== Migrating Comment table: Adding predicted_age column ===")
    
    # 1. Add column (safe, won't overwrite)
    try:
        db.engine.execute("ALTER TABLE comment ADD COLUMN predicted_age VARCHAR(50)")
        print("✅ Added predicted_age column")
    except Exception as e:
        print(f"Column exists or error: {e}")
    
    # 2. Backfill existing comments
    comments = Comment.query.all()
    updated = 0
    for comment in comments:
        if comment.predicted_age is None:
            age = predict_age(comment.text)
            comment.predicted_age = age
            db.session.commit()
            updated += 1
            print(f"Backfilled comment {comment.id}: {age}")
    
    print(f"✅ Migration complete. Updated {updated} comments.")

