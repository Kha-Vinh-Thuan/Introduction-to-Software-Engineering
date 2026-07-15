import sqlite3
import os
from app.core.config import settings


def verifyDb():
    conn = sqlite3.connect(settings.database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print(f"Database ready — {len(tables)} tables: {', '.join(tables)}")
    return len(tables) > 0


def initDb():
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    if not os.path.exists(settings.database_path):
        print(f"Database not found at {settings.database_path}.")
        print("Run: python data/seed.py to create sample data.")
    else:
        verifyDb()
