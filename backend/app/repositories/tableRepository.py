from app.core.database import getConnection


class TableRepository:
    def findAllTables(self) -> list[dict]:
        conn = getConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM pg_tables WHERE schemaname='public' ORDER BY name")

        tables = []
        for row in cursor.fetchall():
            tableName = row["name"]
            cursor.execute(f"SELECT COUNT(*) as count FROM [{tableName}]")
            rowCount = cursor.fetchone()["count"]
            tables.append({"name": tableName, "rowCount": rowCount})
        conn.close()
        return tables

    def findTableSchema(self, tableName: str) -> list[dict]:
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info([{tableName}])")
        columns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return columns

    def findRecords(self, tableName: str, page: int, pageSize: int, search: str) -> dict:
        conn = getConnection()
        cursor = conn.cursor()
        offset = (page - 1) * pageSize

        cursor.execute(f"SELECT COUNT(*) as total FROM [{tableName}]")
        total = cursor.fetchone()["total"]

        cursor.execute(f"SELECT * FROM [{tableName}] LIMIT ? OFFSET ?",(pageSize, offset))

        records = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if search:
            search = search.strip().lower()
            records = [
                record
                for record in records
                if any(search in str(value).lower() for value in record.values())
            ]

        return {"data": records, "total": total, "page": page, "pageSize": pageSize}
    
    def getSortedRecords(self, tableName: str, sortColumn: str, sortOrder: str = "ASC", page: int = 1, pageSize: int = 50) -> dict:
        conn = getConnection()
        cursor = conn.cursor()
        offset = (page - 1) * pageSize

        cursor.execute(f"SELECT COUNT(*) as total FROM [{tableName}]")
        total = cursor.fetchone()["total"]

        cursor.execute(f"SELECT * FROM [{tableName}] ORDER BY [{sortColumn}] {sortOrder} LIMIT ? OFFSET ?",(pageSize, offset))

        records = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return {"data": records, "total": total, "page": page, "pageSize": pageSize}

    def getRecordById(self, tableName: str, recordId: int) -> dict:
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM [{tableName}] WHERE rowid = ?", (recordId,))
        record = cursor.fetchone()
        conn.close()
        return dict(record) if record else None
    
    def insertRecord(self, tableName: str, data: dict) -> dict:
        conn = getConnection()
        cursor = conn.cursor()
        columns = ", ".join([f"[{k}]" for k in data.keys()])
        placeholders = ", ".join(["?" for _ in data])
        cursor.execute(
            f"INSERT INTO [{tableName}] ({columns}) VALUES ({placeholders})",
            list(data.values())
        )
        conn.commit()
        lastId = cursor.lastrowid
        conn.close()
        return {"id": lastId}

    def updateRecord(self, tableName: str, recordId: int, data: dict) -> bool:
        conn = getConnection()
        cursor = conn.cursor()
        setClause = ", ".join([f"[{k}] = ?" for k in data.keys()])
        cursor.execute(
            f"UPDATE [{tableName}] SET {setClause} WHERE rowid = ?",
            list(data.values()) + [recordId]
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def deleteRecord(self, tableName: str, recordId: int) -> bool:
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM [{tableName}] WHERE rowid = ?", (recordId,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
