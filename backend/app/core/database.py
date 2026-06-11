import sqlite3
from app.core.config import settings


def getConnection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def getReadOnlyConnection() -> sqlite3.Connection:
    uri = f"file:{settings.database_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn
