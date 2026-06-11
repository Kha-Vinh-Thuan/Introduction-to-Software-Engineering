import sqlite3
import urllib.request
import os
from app.core.config import settings


NORTHWIND_URL = "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db"


def downloadNorthwind():
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    if not os.path.exists(settings.database_path):
        print(f"Downloading Northwind database to {settings.database_path}...")
        urllib.request.urlretrieve(NORTHWIND_URL, settings.database_path)
        print("Download complete.")
    else:
        print(f"Database already exists at {settings.database_path}, skipping download.")


def verifyDb():
    conn = sqlite3.connect(settings.database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print(f"Database ready — {len(tables)} tables found: {', '.join(tables)}")
    return len(tables) > 0


def initDb():
    downloadNorthwind()
    verifyDb()
