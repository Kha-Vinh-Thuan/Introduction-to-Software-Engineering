import psycopg
from psycopg.rows import dict_row
from app.core.config import settings


def getConnection() -> psycopg.Connection:
    conn = psycopg.connect(settings.database_path, row_factory= dict_row, autocommit=False)
    return conn


def getReadOnlyConnection() -> psycopg.Connection:
    conn = psycopg.connect(settings.database_path, row_factory= dict_row, autocommit=False)
    conn.read_only = True
    return conn
