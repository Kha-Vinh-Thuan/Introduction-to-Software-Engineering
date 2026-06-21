import axiosInstance from "./axios";

export const tableApi = {
  getTables: () => axiosInstance.get("/api/v1/tables/"),
  getRecords: (tableName, params) => axiosInstance.get(`/api/v1/tables/${tableName}/records`, { params }),
  createRecord: (tableName, data) => axiosInstance.post(`/api/v1/tables/${tableName}/records`, { data }),
  updateRecord: (tableName, recordId, data) => axiosInstance.put(`/api/v1/tables/${tableName}/records/${recordId}`, { data }),
  deleteRecord: (tableName, recordId) => axiosInstance.delete(`/api/v1/tables/${tableName}/records/${recordId}`),
};

export const schemaApi = {
  getSchema: () => axiosInstance.get("/api/v1/schema/"),
  getTableSchema: (tableName) => axiosInstance.get(`/api/v1/schema/${tableName}`),
};

export const chatApi = {
  sendMessage: (message, conversationHistory) =>
    axiosInstance.post("/api/v1/chat/", { message, conversationHistory }),
};

export const reportApi = {
  getWeeklyReport: () => axiosInstance.get("/api/v1/reports/weekly"),
  getReports: () => axiosInstance.get("/api/v1/reports/"),
};

export const importExportApi = {
  importCsv: (tableName, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return axiosInstance.post(`/api/v1/import-export/import/${tableName}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  exportCsv: (tableName) => axiosInstance.get(`/api/v1/import-export/export/${tableName}`, { responseType: "blob" }),
};
