from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/new_posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    # Check if columns exist
    result = db.engine.execute(text("PRAGMA table_info(post)"))
    columns = [row[1] for row in result.fetchall()]
    print("Current columns in post table:", columns)

    if 'media_path' not in columns:
        print("Adding media_path column...")
        db.engine.execute(text("ALTER TABLE post ADD COLUMN media_path VARCHAR(255)"))
    if 'media_type' not in columns:
        print("Adding media_type column...")
        db.engine.execute(text("ALTER TABLE post ADD COLUMN media_type VARCHAR(50)"))

    print("Columns added successfully.")
