# DataPilot — Frontend

React + MUI frontend cho hệ thống quản lý database qua LLM.

## Quick Start

```bash
make install   # cài node_modules
make run       # chạy frontend tại http://localhost:5173
make build     # build production
```

---

## Architecture

```
src/
├── components/     Reusable UI components, chia theo feature
│   ├── layout/     Header, Sidebar
│   ├── common/     Button, Dialog, Table dùng chung
│   ├── dashboard/  Components riêng cho Dashboard page
│   ├── explorer/   Components riêng cho DB Explorer
│   ├── schema/     Components riêng cho Schema page
│   ├── reports/    Components riêng cho Reports page
│   └── chat/       Components riêng cho Chat page
├── pages/          Page components (1 page = 1 folder)
├── hooks/          Custom hooks, chia theo feature
├── layouts/        Layout wrappers (MainLayout)
├── routes/         Route definitions
├── stores/         Zustand global state
├── theme/          MUI theme config
├── utils/          axios instance, api helpers
└── constants/      App-wide constants
```

---

## Quy tắc code — BẮT BUỘC tuân thủ

### Đặt tên

| Loại | Quy tắc | Ví dụ |
|---|---|---|
| Component | PascalCase | `RecordTable`, `ChatMessageBubble` |
| Custom hook | camelCase, bắt đầu bằng `use` + động từ + tác dụng | `useGetTables`, `useSendMessage`, `useExportCsv` |
| Function | camelCase, động từ + tác dụng | `formatDate`, `parseErrorMessage`, `buildQueryParams` |
| Variable / state | camelCase, rõ nghĩa | `tableList`, `isLoading`, `selectedTableName` |
| File component | PascalCase | `RecordTable.jsx`, `ChatInputBox.jsx` |
| File hook | camelCase | `useGetTables.js`, `useSendMessage.js` |
| Constant | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE`, `DEFAULT_DEBOUNCE_MS` |

**Không được đặt tên kiểu:** `data`, `res`, `temp`, `x`, `item`, `val`

### Component

- Mỗi file component chỉ export **một component**
- Props phải khai báo rõ ràng, có default value nếu optional
- Không viết logic phức tạp trực tiếp trong JSX — tách ra hook hoặc function

### Custom Hooks

- Mỗi hook chỉ làm **một việc** (fetch data, mutation, hoặc local state)
- Dùng React Query cho tất cả server state — không dùng `useEffect` + `useState` để fetch
- Hook trả về object có tên rõ ràng, không trả về array

```jsx
// Đúng
const { tableList, isLoadingTableList, refetchTableList } = useGetTables();

// Sai
const [data, loading, refetch] = useGetTables();
```

### API calls

- Tất cả API calls đặt trong `src/utils/api.js`
- Không gọi `axios` trực tiếp trong component hoặc hook
- Dùng React Query `useQuery` / `useMutation` — không dùng `useEffect` để fetch

### State management

- Server state: React Query
- Global UI state: Zustand (`src/stores/`)
- Local UI state: `useState` trong component

---

## Commit Convention

Format: `<type>(<scope>): <mô tả ngắn>`

| Type | Khi nào dùng |
|---|---|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa bug |
| `refactor` | Refactor code, không thay đổi behavior |
| `style` | Thay đổi CSS/styling thuần túy |
| `test` | Thêm/sửa test |
| `docs` | Cập nhật tài liệu |
| `chore` | Config, dependency |

Ví dụ:
```
feat(explorer): add paginated record table with search
fix(chat): prevent duplicate messages on fast submit
refactor(hooks): move table fetch logic into useGetTables hook
style(sidebar): highlight active nav item
```

**Không được nhắc tới AI, tool hỗ trợ, hay tên người trong commit message.**

---

## Pages

| Route | Component | Mô tả |
|---|---|---|
| `/dashboard` | `DashboardPage` | Thống kê tổng quan, charts |
| `/explorer` | `ExplorerPage` | Sidebar bảng + browse/CRUD records |
| `/explorer/:tableName` | `ExplorerPage` | Xem records của bảng cụ thể |
| `/schema` | `SchemaPage` | Cấu trúc bảng, quan hệ |
| `/import-export` | `ImportExportPage` | Upload CSV, export data |
| `/reports` | `ReportsPage` | Báo cáo định kỳ, weekly report |
| `/chat` | `ChatPage` | Text2SQL, hỏi đáp tự nhiên |

---

## Environment Variables

| Biến | Mô tả | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend URL | `http://localhost:8000` |
| `VITE_APP_NAME` | Tên app | `DataPilot` |
