"""
Agent tools — lớp hàm "tool" mà LLM orchestrator và MCP server cùng gọi.

Mỗi hàm = một tool. Hàm đọc/ghi bản ghi đi qua TableRepository (N-layer),
riêng executeSql chạy trên kết nối read-only và chỉ cho phép SELECT.
"""

import sqlglot

from app.core.database import getReadOnlyConnection
from app.repositories.tableRepository import TableRepository

BLOCKED_STATEMENT_TYPES = {
    "Insert",
    "Update",
    "Delete",
    "Drop",
    "Create",
    "Alter",
    "Truncate",
}
DEFAULT_ROW_LIMIT = 100
MAX_ROW_LIMIT = 200

tableRepository = TableRepository()


def listTables() -> list[str]:
    """Trả về danh sách tên bảng trong database."""
    tables = tableRepository.findAllTables()
    return [table["name"] for table in tables]


def describeTable(tableName: str) -> list[dict] | dict:
    """Trả về định nghĩa cột (schema) của một bảng.

    Mỗi cột gồm: cid, name, type, notnull, dflt_value, pk (từ PRAGMA table_info).
    Tên bảng được kiểm tra dựa trên danh sách bảng thật trước khi truy vấn:
    bảng không tồn tại (hoặc tên không hợp lệ) trả về {"error": ...} thay vì
    list rỗng im lặng — đồng thời chặn tên gây lỗi cú pháp PRAGMA.
    """
    if tableName not in listTables():
        return {"error": f"Bảng không tồn tại: {tableName!r}"}
    return tableRepository.findTableSchema(tableName)


def _isSelectOnly(sql: str) -> bool:
    """True nếu mọi câu lệnh trong sql đều là SELECT (chặn ghi/DDL)."""
    for statement in sqlglot.parse(sql, dialect="sqlite"):
        if statement is None:
            continue
        if type(statement).__name__ in BLOCKED_STATEMENT_TYPES:
            return False
    return True


def executeSql(sql: str, limit: int = DEFAULT_ROW_LIMIT) -> dict:
    """Chạy câu lệnh SELECT trên kết nối read-only, trả về columns + rows."""
    try:
        if not _isSelectOnly(sql):
            return {"error": "Chỉ cho phép câu lệnh SELECT."}
    except Exception as parseError:
        return {"error": f"SQL không hợp lệ: {parseError}"}

    connection = getReadOnlyConnection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchmany(min(limit, MAX_ROW_LIMIT))
        columns = [column[0] for column in cursor.description] if cursor.description else []
        return {"columns": columns, "rows": [list(row) for row in rows], "count": len(rows)}
    except Exception as queryError:
        return {"error": f"Lỗi truy vấn: {queryError}"}
    finally:
        connection.close()


def createRecord(tableName: str, record: dict) -> dict:
    """Chèn một bản ghi mới, trả về id vừa tạo."""
    return tableRepository.insertRecord(tableName, record)


def updateRecord(tableName: str, recordId: int, record: dict) -> dict:
    """Cập nhật bản ghi theo rowid, trả về có hàng nào bị đổi không."""
    updated = tableRepository.updateRecord(tableName, recordId, record)
    return {"updated": updated}


def deleteRecord(tableName: str, recordId: int) -> dict:
    """Xóa bản ghi theo rowid, trả về có hàng nào bị xóa không."""
    deleted = tableRepository.deleteRecord(tableName, recordId)
    return {"deleted": deleted}
