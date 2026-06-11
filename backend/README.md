# DataPilot — Backend

FastAPI backend với AI agent orchestration, MCP server, và SQLite.

## Quick Start

```bash
make install   # tạo venv + cài packages
make run       # chạy backend tại http://localhost:8000
make mcp       # chạy MCP server (stdio mode, dùng với Claude Desktop)
```

Sau khi chạy `make install`, mở `.env` và điền `GEMINI_API_KEY`.

---

## Architecture

```
N-Layer Architecture:
  Endpoint (Controller) → Service → Repository → Database

app/
├── api/v1/endpoints/   Controller layer — nhận request, trả response
├── services/           Business logic layer
├── repositories/       Data access layer — SQL queries
├── models/             Domain models (dataclass)
├── schemas/            Pydantic request/response schemas
├── agent/              LLM orchestrator + tool definitions
├── mcp/                MCP server (Model Context Protocol)
├── core/               Config, database connection
└── utils/              Helper functions
```

---

## Quy tắc code — BẮT BUỘC tuân thủ

### Đặt tên

| Loại | Quy tắc | Ví dụ |
|---|---|---|
| Function / Method | camelCase, động từ + tác dụng | `getTables`, `createRecord`, `validateSql` |
| Variable | camelCase, rõ nghĩa | `tableName`, `recordId`, `rowCount` |
| Class | PascalCase | `TableService`, `AgentOrchestrator` |
| File | camelCase + suffix rõ loại | `tableService.py`, `chatEndpoint.py` |
| Constant | UPPER_SNAKE_CASE | `MAX_TOOL_CALLS`, `BLOCKED_STATEMENT_TYPES` |

**Không được đặt tên kiểu:** `data`, `result`, `temp`, `x`, `val`, `obj`

### Cấu trúc function

- Mỗi function chỉ làm **một việc**
- Không viết function dài hơn 40 dòng
- Tham số không quá 5 — nếu hơn thì tạo dataclass/schema

### Import

- Absolute import — không dùng relative import (`from ..utils` → không được)
- Group theo thứ tự: stdlib → third-party → local

### Error handling

- Không `except Exception` trống không
- Raise exception có message rõ ràng
- Endpoint trả về `errorResponse()` từ `utils/responseHelper.py`

---

## Commit Convention

Format: `<type>(<scope>): <mô tả ngắn>`

| Type | Khi nào dùng |
|---|---|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa bug |
| `refactor` | Refactor code, không thay đổi behavior |
| `test` | Thêm/sửa test |
| `docs` | Cập nhật tài liệu |
| `chore` | Config, dependency, build |

Ví dụ:
```
feat(chat): add tool-use loop with max iteration guard
fix(repository): handle missing table gracefully in findRecords
refactor(agent): extract tool dispatch into separate module
```

**Không được nhắc tới AI, tool hỗ trợ, hay tên người trong commit message.**

---

## API Endpoints

| Method | Path | Mô tả |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/tables/` | Danh sách bảng |
| GET | `/api/v1/tables/{name}/records` | Records của bảng |
| POST | `/api/v1/tables/{name}/records` | Thêm record |
| PUT | `/api/v1/tables/{name}/records/{id}` | Sửa record |
| DELETE | `/api/v1/tables/{name}/records/{id}` | Xóa record |
| GET | `/api/v1/schema/` | Full schema |
| GET | `/api/v1/schema/{name}` | Schema của bảng |
| POST | `/api/v1/chat/` | Gửi message cho AI agent |
| GET | `/api/v1/reports/weekly` | Báo cáo tuần |
| POST | `/api/v1/import-export/import/{name}` | Import CSV |
| GET | `/api/v1/import-export/export/{name}` | Export CSV |

Docs đầy đủ: http://localhost:8000/docs

---

## MCP Server (Claude Desktop / Claude Code)

Thêm vào `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "datapilot": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/backend"
    }
  }
}
```

---

## Environment Variables

| Biến | Mô tả | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (bắt buộc) | — |
| `GEMINI_MODEL` | Model name | `gemini-2.0-flash` |
| `DATABASE_PATH` | Đường dẫn SQLite file | `./data/datapilot.db` |
| `DEBUG` | Bật debug mode | `True` |
| `CORS_ORIGINS` | Allowed origins | `["http://localhost:5173"]` |
