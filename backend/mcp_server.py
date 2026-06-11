import asyncio
from app.mcp.server import runMcpServer

if __name__ == "__main__":
    asyncio.run(runMcpServer())
