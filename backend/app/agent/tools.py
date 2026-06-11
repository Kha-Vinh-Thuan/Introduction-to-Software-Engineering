import sqlglot
from app.core.database import getConnection, getReadOnlyConnection

BLOCKED_STATEMENT_TYPES = {"Insert", "Update", "Delete", "Drop", "Create", "Alter", "Truncate"}


def listTables() -> list[dict]:
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def describeTable(tableName: str) -> list[dict]:
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info([{tableName}])")
    columns = [{"name": row[1], "type": row[2], "notNull": bool(row[3]), "isPrimaryKey": bool(row[5])} for row in cursor.fetchall()]
    conn.close()
    return columns


def executeSql(sql: str, limit: int = 100) -> dict:
    try:
        statements = sqlglot.parse(sql, dialect="sqlite")
        for stmt in statements:
            stmtType = type(stmt).__name__
            if stmtType in BLOCKED_STATEMENT_TYPES:
                return {"error": f"Statement type '{stmtType}' is not allowed. Only SELECT is permitted."}
    except Exception as e:
        return {"error": f"SQL syntax error: {str(e)}"}

    conn = getReadOnlyConnection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchmany(min(limit, 500))
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    conn.close()
    return {"columns": columns, "rows": [list(row) for row in rows], "count": len(rows)}


def createRecord(tableName: str, data: dict) -> dict:
    conn = getConnection()
    cursor = conn.cursor()
    columns = ", ".join([f"[{k}]" for k in data.keys()])
    placeholders = ", ".join(["?" for _ in data])
    cursor.execute(f"INSERT INTO [{tableName}] ({columns}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    lastId = cursor.lastrowid
    conn.close()
    return {"success": True, "id": lastId}


def updateRecord(tableName: str, recordId: int, data: dict) -> dict:
    conn = getConnection()
    cursor = conn.cursor()
    setClause = ", ".join([f"[{k}] = ?" for k in data.keys()])
    cursor.execute(f"UPDATE [{tableName}] SET {setClause} WHERE rowid = ?", list(data.values()) + [recordId])
    conn.commit()
    conn.close()
    return {"success": cursor.rowcount > 0}


def deleteRecord(tableName: str, recordId: int) -> dict:
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM [{tableName}] WHERE rowid = ?", (recordId,))
    conn.commit()
    conn.close()
    return {"success": cursor.rowcount > 0}


def executeToolCall(toolName: str, args: dict):
    toolMap = {
        "listTables": lambda: listTables(),
        "describeTable": lambda: describeTable(args.get("tableName", "")),
        "executeSql": lambda: executeSql(args.get("sql", ""), args.get("limit", 100)),
        "createRecord": lambda: createRecord(args.get("tableName", ""), args.get("data", {})),
        "updateRecord": lambda: updateRecord(args.get("tableName", ""), args.get("recordId", 0), args.get("data", {})),
        "deleteRecord": lambda: deleteRecord(args.get("tableName", ""), args.get("recordId", 0)),
    }
    fn = toolMap.get(toolName)
    if fn:
        return fn()
    return {"error": f"Unknown tool: {toolName}"}


TOOL_DEFINITIONS = [
    {
        "name": "listTables",
        "description": "List all tables in the database. Always call this first if you don't know the database structure.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "describeTable",
        "description": "Get column names, types, and constraints of a specific table. Call before writing SQL.",
        "parameters": {
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Exact table name (case-sensitive)"}
            },
            "required": ["tableName"],
        },
    },
    {
        "name": "executeSql",
        "description": "Execute a SELECT SQL query and return results. Only SELECT is allowed.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "A valid SQLite SELECT statement"},
                "limit": {"type": "integer", "description": "Max rows to return (default 100, max 500)", "default": 100},
            },
            "required": ["sql"],
        },
    },
    {
        "name": "createRecord",
        "description": "Insert a new record into a table.",
        "parameters": {
            "type": "object",
            "properties": {
                "tableName": {"type": "string"},
                "data": {"type": "object", "description": "Key-value pairs of column names and values"},
            },
            "required": ["tableName", "data"],
        },
    },
    {
        "name": "updateRecord",
        "description": "Update an existing record by rowid.",
        "parameters": {
            "type": "object",
            "properties": {
                "tableName": {"type": "string"},
                "recordId": {"type": "integer", "description": "The rowid of the record to update"},
                "data": {"type": "object", "description": "Key-value pairs of columns to update"},
            },
            "required": ["tableName", "recordId", "data"],
        },
    },
    {
        "name": "deleteRecord",
        "description": "Delete a record by rowid.",
        "parameters": {
            "type": "object",
            "properties": {
                "tableName": {"type": "string"},
                "recordId": {"type": "integer", "description": "The rowid of the record to delete"},
            },
            "required": ["tableName", "recordId"],
        },
    },
]
