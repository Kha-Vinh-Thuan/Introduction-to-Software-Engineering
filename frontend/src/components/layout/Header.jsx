import { AppBar, Toolbar, Typography, Box } from "@mui/material";
import { useLocation } from "react-router-dom";

const PAGE_TITLES = {
  "/dashboard": "Dashboard",
  "/explorer": "Database Explorer",
  "/schema": "Schema",
  "/import-export": "Import / Export",
  "/reports": "Reports",
  "/chat": "Chat AI Agent",
};

export default function Header() {
  const { pathname } = useLocation();
  const baseRoute = "/" + pathname.split("/")[1];
  const title = PAGE_TITLES[baseRoute] || "DataPilot";

  return (
    <AppBar position="fixed" elevation={1} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" fontWeight={600}>{title}</Typography>
        <Box sx={{ flexGrow: 1 }} />
      </Toolbar>
    </AppBar>
  );
}
