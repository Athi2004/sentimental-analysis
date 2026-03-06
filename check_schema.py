import sqlite3

conn = sqlite3.connect('instance/new_posts.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(post)")
columns = cursor.fetchall()

print("Columns in post table:")
for col in columns:
    print(col)

conn.close()
