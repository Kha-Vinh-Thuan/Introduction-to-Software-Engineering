import httpx
import json
from app.core.config import settings

SYSTEM_PROMPT = """Bạn là DataPilot, trợ lý phân tích dữ liệu HR. Chỉ trả lời dựa trên dữ liệu từ DB.

SCHEMA (SQLite):
Employees(EmployeeID,HoTen,GioiTinh[Nam/Nữ],NgaySinh,DiaChi,ThanhPho,SoDienThoai,NgayVaoLam)
EmployeeProfiles(ProfileID,EmployeeID,DepartmentID,CCCD,TinhTrangHonNhan[SINGLE/MARRIED/DIVORCED],LoaiHopDong[FULL_TIME/CONTRACT/PROBATION],TrangThaiLamViec[ACTIVE/RESIGNED/PENDING_TERMINATION],NgayVao,NgayNghi,ChucVu,CapBac,QuanLyTrucTiepID,EmailCongTy,SoDienThoaiCongTy,NguoiLienHeKhanCap,SoTaiKhoanNganHang,TenNganHang,MaSoThue,SoNgayPhepNam,SoNgayPhepBenh)
Departments(DepartmentID,DepartmentName,ParentDepartmentID,CostCenter,HeadCount)
Attendance(AttendanceID,EmployeeID,NgayLamViec,GioVao,GioRa,HinhThucLam[OFFICE/REMOTE/BUSINESS_TRIP],TrangThai[PRESENT/ABSENT/ON_LEAVE/HOLIDAY/WEEKEND],DiTre[0/1],SoPhutDiTre,SoPhutTangCa)
BaseSalary(BaseSalaryID,EmployeeID,NgayHieuLuc,LuongCoBan,PhuCapDiLai,PhuCapAnTrua,PhuCapSucKhoe)
SalaryHistory(SalaryID,EmployeeID,BaseSalaryID,NamKy,ThangKy,SoNgayLamViec,LuongCoBan,PhuCapDiLai,PhuCapAnTrua,PhuCapSucKhoe,ThuongHieuQua,PhuCapTangCa,KhauTruDiTre,KhauTruThue,KhauTruBHXH,LuongThucNhan,NgayThanhToan)
LeaveRequests(LeaveID,EmployeeID,LoaiNghi[ANNUAL/SICK/PERSONAL/MATERNITY/PATERNITY/UNPAID],NgayBatDau,NgayKetThuc,SoNgay,LyDo,TrangThai[PENDING/APPROVED/REJECTED/CANCELLED],DuyetBoi,NgayDuyet,TaoLuc)

QUAN HỆ: Employees.EmployeeID=EmployeeProfiles.EmployeeID=Attendance.EmployeeID=BaseSalary.EmployeeID=SalaryHistory.EmployeeID=LeaveRequests.EmployeeID; EmployeeProfiles.DepartmentID=Departments.DepartmentID; SalaryHistory.BaseSalaryID=BaseSalary.BaseSalaryID

QUY TẮC: Gọi executeSql trực tiếp (đã biết schema). Chỉ SELECT. Trả lời tiếng Việt, ngắn gọn, có số liệu."""

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "executeSql",
            "description": "Thực thi SELECT SQL trên SQLite HR database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "Câu lệnh SELECT hợp lệ"},
                    "limit": {"type": "integer", "description": "Số hàng tối đa, mặc định 100"},
                },
                "required": ["sql"],
            },
        },
    }
]

MAX_HISTORY = 6


def _executeSql(sql: str, limit: int = 100) -> dict:
    import sqlglot
    from app.core.database import getReadOnlyConnection

    BLOCKED = {"Insert", "Update", "Delete", "Drop", "Create", "Alter", "Truncate"}
    try:
        for stmt in sqlglot.parse(sql, dialect="sqlite"):
            if type(stmt).__name__ in BLOCKED:
                return {"error": f"Chỉ SELECT được phép."}
    except Exception as e:
        return {"error": f"SQL không hợp lệ: {e}"}

    conn = getReadOnlyConnection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchmany(min(limit, 200))
    columns = [d[0] for d in cursor.description] if cursor.description else []
    conn.close()
    return {"columns": columns, "rows": [list(r) for r in rows], "count": len(rows)}


class AgentOrchestrator:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "DataPilot",
        }

    async def run(self, userMessage: str, conversationHistory: list[dict]) -> dict:
        # Giới hạn history để tiết kiệm token
        recentHistory = conversationHistory[-(MAX_HISTORY):]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in recentHistory:
            role = msg.get("role", "user")
            content = msg.get("content", "") or (
                msg.get("parts", [{}])[0].get("text", "") if msg.get("parts") else ""
            )
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": userMessage})

        toolCallsLog = []
        message = {}

        async with httpx.AsyncClient(timeout=60) as client:
            for _ in range(3):
                payload = {
                    "model": settings.openrouter_model,
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice": "auto",
                }
                resp = await client.post(OPENROUTER_URL, headers=self.headers, json=payload)
                if resp.status_code >= 400:
                    raise Exception(f"OpenRouter error {resp.status_code}: {resp.text}")

                data = resp.json()
                choice = data["choices"][0]
                message = choice["message"]
                messages.append(message)

                tool_calls = message.get("tool_calls") or []
                if not tool_calls or choice.get("finish_reason") == "stop":
                    break

                for tc in tool_calls:
                    fn_args = json.loads(tc["function"]["arguments"])
                    result = _executeSql(**fn_args)
                    toolCallsLog.append({"tool": "executeSql", "args": fn_args, "result": result})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, ensure_ascii=False),
                    })

        return {"reply": message.get("content") or "", "toolCalls": toolCallsLog}
