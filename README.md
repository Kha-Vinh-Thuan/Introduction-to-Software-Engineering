# DataPilot

> **Hỏi dữ liệu nhân sự bằng tiếng Việt tự nhiên.** DataPilot dịch câu hỏi của bạn
> thành SQL, tự chạy truy vấn trên SQLite (chỉ đọc), rồi trả lời bằng lời văn kèm
> số liệu — thông qua một **tool-use loop** thật sự, không phải chat wrapper.

Đồ án môn **Nhập môn Công nghệ Phần mềm**. Một AI agent phân tích dữ liệu HR của
công ty công nghệ Việt Nam (~95 nhân sự, 8 bảng): lương, chấm công, nghỉ phép, phòng ban.

| | |
|---|---|
| **Backend** | Python · FastAPI · httpx · sqlglot · MCP SDK |
| **LLM** | OpenRouter — `meta-llama/llama-3.3-70b-instruct:free` (mặc định) |
| **Frontend** | React 18 · Vite · MUI 5 · React Query · Zustand |
| **Database** | SQLite (read-only cho AI) |
| **Giao thức AI** | REST API + MCP server (Model Context Protocol) |

---

## Mục lục

- [DataPilot là gì](#datapilot-là-gì)
- [Kiến trúc](#kiến-trúc)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Cơ sở dữ liệu](#cơ-sở-dữ-liệu)
- [Yêu cầu môi trường](#yêu-cầu-môi-trường)
- [Cài đặt & chạy](#cài-đặt--chạy)
- [API](#api)
- [MCP Server](#mcp-server)
- [Bảo mật SQL (3 lớp)](#bảo-mật-sql-3-lớp)
- [Trạng thái dự án](#trạng-thái-dự-án)
- [Tài liệu](#tài-liệu)
- [Quy ước phát triển](#quy-ước-phát-triển)

---

## DataPilot là gì

Người dùng đặt câu hỏi tự nhiên (vd: *"Top 10 nhân viên lương cao nhất tháng này?"*).
LLM **tự quyết định** cần truy vấn gì, gọi tool `executeSql`, **nhận kết quả thật**,
rồi suy luận tiếp cho tới khi đủ thông tin để trả lời. LLM là bộ não điều phối —
Python chỉ thực thi tool và canh an toàn.

Hai cách dùng cùng một lõi dữ liệu:

1. **Web app** — REST API `POST /api/v1/chat/` với orchestrator tự chạy tool-use loop.
2. **MCP server** — expose database cho AI client ngoài (vd Claude Desktop) qua stdio/JSON-RPC.

---

## Kiến trúc

```
                ┌─────────────────────────────────────────────┐
                │            Browser (React + MUI)             │
                │            http://localhost:5173             │
                └───────────────────────┬─────────────────────┘
                                        │ HTTP (axios)
                                        ▼
        ┌───────────────────────────────────────────────────────────┐
        │                  FastAPI  ·  app.main:app                  │
        │                  http://localhost:8000                     │
        │   GET  /health                                             │
        │   POST /api/v1/chat/   ─► ChatService ─► AgentOrchestrator │
        │                                                           │ │
        │   ┌─────────────── AgentOrchestrator (tool-use loop) ───┐ │ │
        │   │ 1. Gửi message + tool defs tới OpenRouter           │ │ │
        │   │ 2. LLM trả về tool_call executeSql(sql)             │ │ │
        │   │ 3. Safety layer kiểm tra → chạy SELECT read-only    │ │ │
        │   │ 4. Gửi kết quả về LLM → lặp (tối đa 3 vòng)          │ │ │
        │   │ 5. LLM tổng hợp câu trả lời tiếng Việt              │ │ │
        │   └────────────────────────────┬────────────────────────┘ │ │
        └────────────────────────────────┼───────────────────────────┘
                                         │
            OpenRouter API ◄─────────────┘             ┌──────────────────┐
            (Llama 3.3 70B)                            │  data/           │
                                         ┌────────────►│  datapilot.db    │
                                         │   SELECT    │  (SQLite)        │
        ┌────────────────────────────────┴──────────┐  └──────────────────┘
        │      MCP Server  ·  mcp_server.py (stdio)  │         ▲
        │  resources: datapilot://tables, schema/*   │─────────┘
        │  tools: listTables, describeTable,         │   read / write
        │         executeSql, create/update/delete   │
        └────────────────────────────────────────────┘
                         ▲
                         │ JSON-RPC
                Claude Desktop / AI client khác
```

Backend theo **N-Layer**: `endpoint → service → repository/agent → database`.

---

## Cấu trúc thư mục

```
Introduction-to-Software-Engineering/
├── README.md                  ← bạn đang ở đây
├── backend/                   FastAPI + AI orchestrator + MCP server
│   ├── app/
│   │   ├── main.py            ASGI app (entry point thật: app.main:app)
│   │   ├── api/controller/    router + endpoints (hiện có: chat)
│   │   ├── services/          business logic (chat, table, report)
│   │   ├── repositories/      data access (SQL)
│   │   ├── agent/             orchestrator (OpenRouter) + tools (executeSql…)
│   │   ├── mcp/server.py      MCP server (protocol layer)
│   │   ├── core/              config, database, initDb
│   │   ├── models/ schemas/   domain model + Pydantic schema
│   │   └── utils/             responseHelper
│   ├── data/seed.py           sinh dữ liệu HR mẫu → data/datapilot.db
│   ├── mcp_server.py          chạy MCP server ở chế độ stdio
│   ├── requirements.txt
│   └── run.bat                setup + chạy backend (Windows)
├── frontend/                  React + Vite + MUI
│   ├── src/
│   │   ├── pages/             dashboard · explorer · schema · reports · chat · import-export
│   │   ├── components/layout/ Header, Sidebar
│   │   ├── layouts/ routes/ stores/ theme/ utils/
│   │   └── main.jsx App.jsx
│   ├── package.json
│   └── run.bat                setup + chạy frontend (Windows)
└── documents/                 kế hoạch dự án + template báo cáo môn học
```

---

## Cơ sở dữ liệu

SQLite mô phỏng hệ thống HR công ty công nghệ Việt Nam (~95 nhân sự, dữ liệu Jan 2024 – Jun 2025).
Tạo bằng `python data/seed.py` (chỉ dùng thư viện chuẩn, dữ liệu cố định nhờ `random.seed(42)`).

| Bảng | Nội dung |
|---|---|
| `Departments` | Cây phòng ban 2 cấp (23 phòng) |
| `Employees` | Thông tin cơ bản nhân viên (họ tên, giới tính, ngày sinh, địa chỉ) |
| `EmployeeProfiles` | Hồ sơ HR đầy đủ (CCCD, hợp đồng, chức vụ, cấp bậc, ngân hàng…) |
| `BaseSalary` | Lịch sử lương cứng + phụ cấp cố định |
| `SalaryHistory` | Lương thực nhận hàng tháng (tính từ BaseSalary + Attendance) |
| `Attendance` | Chấm công T2–T6, 9h–18h, có đi trễ / tăng ca |
| `LeaveRequests` | Đơn nghỉ phép theo Luật Lao Động VN |
| `ChatHistory` | Lịch sử hội thoại với AI |

---

## Yêu cầu môi trường

- **Python** 3.11+
- **Node.js** 18+ (kèm npm)
- **OpenRouter API key** — lấy miễn phí tại <https://openrouter.ai/keys>
- Hệ điều hành: hướng dẫn dưới đây dùng **Windows (PowerShell)**; trên macOS/Linux thay `run.bat` bằng các lệnh tương đương hoặc dùng `make`.

---

## Cài đặt & chạy

Cần **2 terminal**: một cho backend, một cho frontend.

### 1) Backend

```powershell
cd backend

# Tạo venv + cài dependencies
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# Sinh database mẫu (tạo data/datapilot.db)
venv\Scripts\python data\seed.py

# Tạo file .env và điền API key
copy .env.example .env
# Mở .env và thêm dòng:  OPENROUTER_API_KEY=sk-or-...

# Chạy backend
venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend chạy tại <http://localhost:8000> — tài liệu API tự sinh ở <http://localhost:8000/docs>.

> **Quan trọng:** lõi chat dùng **OpenRouter**, nên `.env` **bắt buộc** có
> `OPENROUTER_API_KEY`. File `.env.example` hiện chỉ liệt kê biến `GEMINI_*` cũ
> (bị bỏ qua) — hãy tự thêm `OPENROUTER_API_KEY`. Xem [Trạng thái dự án](#trạng-thái-dự-án).

### 2) Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend chạy tại <http://localhost:5173>, gọi backend qua `VITE_API_BASE_URL` (mặc định `http://localhost:8000`).

### Biến môi trường

**Backend (`backend/.env`)**

| Biến | Mô tả | Mặc định |
|---|---|---|
| `OPENROUTER_API_KEY` | Khóa OpenRouter (**bắt buộc** cho chat) | — |
| `OPENROUTER_MODEL` | Model dùng cho tool-use | `meta-llama/llama-3.3-70b-instruct:free` |
| `DATABASE_PATH` | Đường dẫn file SQLite | `./data/datapilot.db` |
| `CORS_ORIGINS` | Origin được phép | `["http://localhost:5173","http://localhost:3000"]` |
| `DEBUG` | Bật debug | `False` |

**Frontend (`frontend/.env`)**

| Biến | Mô tả | Mặc định |
|---|---|---|
| `VITE_API_BASE_URL` | URL backend | `http://localhost:8000` |
| `VITE_APP_NAME` | Tên app | `DataPilot` |

---

## API

Hiện đã nối dây (wired):

| Method | Path | Mô tả |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/chat/` | Gửi câu hỏi cho AI agent (chạy tool-use loop) |

**Ví dụ:**

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Phòng ban nào đông nhân viên nhất?", "conversationHistory": []}'
```

**Response:**

```json
{
  "reply": "Phòng Lập Trình Backend đông nhất với 12 nhân viên...",
  "toolCalls": [
    { "tool": "executeSql", "args": { "sql": "SELECT ..." }, "result": { "count": 5 } }
  ],
  "sqlExecuted": null
}
```

---

## MCP Server

Expose database cho AI client qua Model Context Protocol (stdio).

```powershell
cd backend
venv\Scripts\python mcp_server.py
```

Đăng ký trong `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "datapilot": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:/đường/dẫn/tới/backend"
    }
  }
}
```

- **Resources:** `datapilot://tables`, `datapilot://schema/{table}`
- **Tools:** `listTables`, `describeTable`, `executeSql` (read-only), `createRecord`, `updateRecord`, `deleteRecord`

---

## Bảo mật SQL (3 lớp)

LLM chỉ được **đọc** dữ liệu. Mọi câu lệnh ghi/DDL bị chặn:

1. **Kết nối read-only** — SQLite mở ở `mode=ro`; mọi thao tác ghi bị OS/SQLite từ chối.
2. **Parser sqlglot** — phân tích AST, chặn các statement `Insert/Update/Delete/Drop/Create/Alter/Truncate`.
3. **System prompt** — chỉ thị LLM chỉ sinh `SELECT` và từ chối yêu cầu xóa/sửa.

Thêm vào đó: giới hạn số dòng trả về (mặc định 100, tối đa 200) để tránh tràn kết quả.

---

## Trạng thái dự án

DataPilot đang phát triển — phần **chat + MCP đã chạy được**, một số phần còn là khung
hoặc tài liệu chưa khớp code. Để minh bạch:

**Đã hoạt động**
- Tool-use loop qua OpenRouter (`POST /api/v1/chat/`)
- `executeSql` với 3 lớp bảo mật read-only
- MCP server (resources + tools)
- Seed dữ liệu HR đầy đủ (`data/seed.py`)
- Frontend: routing + layout + trang Chat

**Khung / chưa nối dây**
- Các trang frontend Dashboard, Explorer, Schema, Reports, Import/Export đã có UI nhưng backend chưa expose endpoint tương ứng (router hiện chỉ gồm `chat`).
- `services/tableService.py`, `services/reportService.py`, `repositories/` đã viết nhưng chưa có endpoint gọi tới.

**Sai lệch tài liệu cần lưu ý (sẽ dọn dần)**
- `backend/.env.example` liệt kê `GEMINI_API_KEY` (cũ) thay vì `OPENROUTER_API_KEY` đang dùng → tự thêm khi tạo `.env`.
- `backend/main.py` (ở gốc backend) và target `make run` trỏ tới module `app.api.v1.router` không còn tồn tại → **dùng `app.main:app`** (như `run.bat`), đừng dùng `make run`.
- README con của backend liệt kê nhiều endpoint (tables/schema/reports/import-export) chưa được nối dây.
- `backend/README.md` đề cập Gemini; thực tế lõi chat dùng OpenRouter (config vẫn giữ sẵn cấu hình Anthropic/Claude để dự phòng).

---

## Tài liệu

Thư mục [`documents/`](documents/) chứa tài liệu môn học:

- `DataPilot-ProjectPlan.txt` — kế hoạch dự án chi tiết (kiến trúc, phân công, lịch 8 tuần, demo script)
- `Template0..3` — template Proposal / Requirement / Design / Testing
- `AI Usage Guidelines.pdf`, `SE10_00.pdf` — hướng dẫn môn học

> Lưu ý: bản kế hoạch gốc dùng dataset **Northwind** và **Claude API**; bản triển khai
> hiện tại đã đổi sang **dữ liệu HR Việt Nam** và **OpenRouter**.

---

## Quy ước phát triển

Format commit: `<type>(<scope>): <mô tả>` — vd `feat(chat): add tool-use loop`.
Chi tiết quy tắc đặt tên, cấu trúc code và commit xem trong README con:

- [`backend/README.md`](backend/README.md) — quy ước backend, kiến trúc N-Layer
- [`frontend/README.md`](frontend/README.md) — quy ước frontend, React Query / Zustand

---

*Đồ án Nhập môn Công nghệ Phần mềm — dùng cho mục đích học tập.*
