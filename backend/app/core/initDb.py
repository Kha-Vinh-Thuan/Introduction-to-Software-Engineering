from app.core.database import getConnection

def verifyDb(conn) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")

    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print(f"Database ready — {len(tables)} tables: {', '.join(tables)}")
    return len(tables) > 0


def initDb():
    try:
        conn = getConnection()
        if not verifyDb(conn):
            conn.close()
            raise Exception("Database initialization failed: No tables found")
        conn.close()
    except Exception as e:
        print(e)
        raise
