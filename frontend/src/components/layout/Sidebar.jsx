import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Typography, Box, Divider } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import DashboardIcon from "@mui/icons-material/Dashboard";
import StorageIcon from "@mui/icons-material/Storage";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import ImportExportIcon from "@mui/icons-material/ImportExport";
import AssessmentIcon from "@mui/icons-material/Assessment";
import ChatIcon from "@mui/icons-material/Chat";

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: <DashboardIcon /> },
  { label: "DB Explorer", path: "/explorer", icon: <StorageIcon /> },
  { label: "Schema", path: "/schema", icon: <AccountTreeIcon /> },
  { label: "Import / Export", path: "/import-export", icon: <ImportExportIcon /> },
  { label: "Reports", path: "/reports", icon: <AssessmentIcon /> },
  { label: "Chat AI", path: "/chat", icon: <ChatIcon /> },
];

export default function Sidebar({ width }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <Drawer variant="permanent" sx={{ width, flexShrink: 0, "& .MuiDrawer-paper": { width, boxSizing: "border-box" } }}>
      <Box sx={{ p: 2, display: "flex", alignItems: "center", gap: 1 }}>
        <StorageIcon color="primary" />
        <Typography variant="h6" fontWeight={700}>DataPilot</Typography>
      </Box>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={pathname.startsWith(item.path)}
            onClick={() => navigate(item.path)}
            sx={{ borderRadius: 1, mx: 1, mb: 0.5 }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}
