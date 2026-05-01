import sqlite3
import os

db_path = 'mdb.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email, role FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]}")
    conn.close()
else:
    print("DB not found")
