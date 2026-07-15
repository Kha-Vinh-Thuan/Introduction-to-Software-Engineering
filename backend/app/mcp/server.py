from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from app.agent.tools import listTables, describeTable, executeSql, createRecord, updateRecord, deleteRecord

mcpServer = Server("datapilot-mcp")


@mcpServer.list_resources()
async def handleListResources() -> list[types.Resource]:
    tables = listTables()
    resources = [
        types.Resource(
            uri=f"datapilot://tables",
            name="Database Tables",
            description="List of all tables in the database",
            mimeType="application/json",
        )
    ]
    for table in tables:
        resources.append(
            types.Resource(
                uri=f"datapilot://schema/{table}",
                name=f"Schema: {table}",
                description=f"Column definitions for table {table}",
                mimeType="application/json",
            )
        )
    return resources


@mcpServer.read_resource()
async def handleReadResource(uri: types.AnyUrl) -> str:
    import json
    uriStr = str(uri)
    if uriStr == "datapilot://tables":
        return json.dumps(listTables())
    if uriStr.startswith("datapilot://schema/"):
        tableName = uriStr.replace("datapilot://schema/", "")
        return json.dumps(describeTable(tableName))
    return json.dumps({"error": "Resource not found"})


@mcpServer.list_tools()
async def handleListTools() -> list[types.Tool]:
    return [
        types.Tool(name="listTables", description="List all tables in the database", inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="describeTable", description="Get schema of a table", inputSchema={"type": "object", "properties": {"tableName": {"type": "string"}}, "required": ["tableName"]}),
        types.Tool(name="executeSql", description="Execute a SELECT SQL query", inputSchema={"type": "object", "properties": {"sql": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["sql"]}),
        types.Tool(name="createRecord", description="Insert a record into a table", inputSchema={"type": "object", "properties": {"tableName": {"type": "string"}, "data": {"type": "object"}}, "required": ["tableName", "data"]}),
        types.Tool(name="updateRecord", description="Update a record by rowid", inputSchema={"type": "object", "properties": {"tableName": {"type": "string"}, "recordId": {"type": "integer"}, "data": {"type": "object"}}, "required": ["tableName", "recordId", "data"]}),
        types.Tool(name="deleteRecord", description="Delete a record by rowid", inputSchema={"type": "object", "properties": {"tableName": {"type": "string"}, "recordId": {"type": "integer"}}, "required": ["tableName", "recordId"]}),
    ]


@mcpServer.call_tool()
async def handleCallTool(name: str, arguments: dict):
    import json
    toolMap = {
        "listTables": lambda: listTables(),
        "describeTable": lambda: describeTable(arguments.get("tableName", "")),
        "executeSql": lambda: executeSql(arguments.get("sql", ""), arguments.get("limit", 100)),
        "createRecord": lambda: createRecord(arguments.get("tableName", ""), arguments.get("data", {})),
        "updateRecord": lambda: updateRecord(arguments.get("tableName", ""), arguments.get("recordId", 0), arguments.get("data", {})),
        "deleteRecord": lambda: deleteRecord(arguments.get("tableName", ""), arguments.get("recordId", 0)),
    }
    fn = toolMap.get(name)
    result = fn() if fn else {"error": f"Unknown tool: {name}"}
    return [types.TextContent(type="text", text=json.dumps(result))]


async def runMcpServer():
    async with stdio_server() as (readStream, writeStream):
        await mcpServer.run(readStream, writeStream, mcpServer.create_initialization_options())
