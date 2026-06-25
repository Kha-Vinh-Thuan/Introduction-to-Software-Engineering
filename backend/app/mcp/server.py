"""
MCP server (Model Context Protocol) cho DataPilot.

Expose database ra cho AI client (vd: Claude Desktop) qua stdio/JSON-RPC:
  - resources : danh sách bảng + schema từng bảng (chỉ đọc)
  - tools     : listTables, describeTable, executeSql (đọc) +
                createRecord, updateRecord, deleteRecord (ghi)

Toàn bộ logic nằm ở app.agent.tools; file này chỉ lo phần giao thức MCP.
"""

import json

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from app.agent.tools import (
    createRecord,
    deleteRecord,
    describeTable,
    executeSql,
    listTables,
    updateRecord,
)

mcpServer = Server("datapilot-mcp")

TABLES_RESOURCE_URI = "datapilot://tables"
SCHEMA_URI_PREFIX = "datapilot://schema/"


@mcpServer.list_resources()
async def handleListResources() -> list[types.Resource]:
    """Liệt kê resource: 1 resource tổng + 1 resource schema cho mỗi bảng."""
    resources = [
        types.Resource(
            uri=TABLES_RESOURCE_URI,
            name="Database Tables",
            description="List of all tables in the database",
            mimeType="application/json",
        )
    ]
    for tableName in listTables():
        resources.append(
            types.Resource(
                uri=f"{SCHEMA_URI_PREFIX}{tableName}",
                name=f"Schema: {tableName}",
                description=f"Column definitions for table {tableName}",
                mimeType="application/json",
            )
        )
    return resources


@mcpServer.read_resource()
async def handleReadResource(uri: types.AnyUrl) -> str:
    """Đọc nội dung một resource theo uri, trả JSON string."""
    uriStr = str(uri)
    if uriStr == TABLES_RESOURCE_URI:
        return json.dumps(listTables())
    if uriStr.startswith(SCHEMA_URI_PREFIX):
        tableName = uriStr.replace(SCHEMA_URI_PREFIX, "")
        return json.dumps(describeTable(tableName))
    return json.dumps({"error": "Resource not found"})


@mcpServer.list_tools()
async def handleListTools() -> list[types.Tool]:
    """Khai báo các tool mà AI client được phép gọi."""
    return [
        types.Tool(
            name="listTables",
            description="List all tables in the database",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="describeTable",
            description="Get schema of a table",
            inputSchema={
                "type": "object",
                "properties": {"tableName": {"type": "string"}},
                "required": ["tableName"],
            },
        ),
        types.Tool(
            name="executeSql",
            description="Execute a read-only SELECT SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="createRecord",
            description="Insert a record into a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "tableName": {"type": "string"},
                    "data": {"type": "object"},
                },
                "required": ["tableName", "data"],
            },
        ),
        types.Tool(
            name="updateRecord",
            description="Update a record by rowid",
            inputSchema={
                "type": "object",
                "properties": {
                    "tableName": {"type": "string"},
                    "recordId": {"type": "integer"},
                    "data": {"type": "object"},
                },
                "required": ["tableName", "recordId", "data"],
            },
        ),
        types.Tool(
            name="deleteRecord",
            description="Delete a record by rowid",
            inputSchema={
                "type": "object",
                "properties": {
                    "tableName": {"type": "string"},
                    "recordId": {"type": "integer"},
                },
                "required": ["tableName", "recordId"],
            },
        ),
    ]


def _dispatchTool(name: str, arguments: dict) -> dict | list:
    """Định tuyến lời gọi tool tới hàm tương ứng trong app.agent.tools."""
    if name == "listTables":
        return listTables()
    if name == "describeTable":
        return describeTable(arguments.get("tableName", ""))
    if name == "executeSql":
        return executeSql(arguments.get("sql", ""), arguments.get("limit", 100))
    if name == "createRecord":
        return createRecord(arguments.get("tableName", ""), arguments.get("data", {}))
    if name == "updateRecord":
        return updateRecord(
            arguments.get("tableName", ""),
            arguments.get("recordId", 0),
            arguments.get("data", {}),
        )
    if name == "deleteRecord":
        return deleteRecord(arguments.get("tableName", ""), arguments.get("recordId", 0))
    return {"error": f"Unknown tool: {name}"}


@mcpServer.call_tool()
async def handleCallTool(name: str, arguments: dict) -> list[types.TextContent]:
    """Chạy tool theo tên và trả kết quả JSON về cho client."""
    result = _dispatchTool(name, arguments or {})
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]


async def runMcpServer() -> None:
    """Khởi chạy MCP server ở chế độ stdio (dùng với Claude Desktop)."""
    async with stdio_server() as (readStream, writeStream):
        await mcpServer.run(
            readStream,
            writeStream,
            mcpServer.create_initialization_options(),
        )
