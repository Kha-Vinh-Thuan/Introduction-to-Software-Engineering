import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import DashboardPage from "../pages/dashboard/DashboardPage";
import ExplorerPage from "../pages/explorer/ExplorerPage";
import SchemaPage from "../pages/schema/SchemaPage";
import ImportExportPage from "../pages/importExport/ImportExportPage";
import ReportsPage from "../pages/reports/ReportsPage";
import ChatPage from "../pages/chat/ChatPage";
import NotFoundPage from "../pages/error/NotFoundPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="explorer" element={<ExplorerPage />} />
        <Route path="explorer/:tableName" element={<ExplorerPage />} />
        <Route path="schema" element={<SchemaPage />} />
        <Route path="import-export" element={<ImportExportPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
