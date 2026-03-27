import sqlite3

conn = sqlite3.connect('instance/new_posts.db')
cursor = conn.cursor()

# Check current columns
cursor.execute("PRAGMA table_info(post)")
columns = [row[1] for row in cursor.fetchall()]
print("Current columns:", columns)

# Add missing columns
if 'media_path' not in columns:
    cursor.execute("ALTER TABLE post ADD COLUMN media_path VARCHAR(255)")
    print("Added media_path column")

if 'media_type' not in columns:
    cursor.execute("ALTER TABLE post ADD COLUMN media_type VARCHAR(50)")
    print("Added media_type column")

conn.commit()
conn.close()
print("Database updated successfully")
