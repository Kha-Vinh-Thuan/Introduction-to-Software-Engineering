import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import Header from "../components/layout/Header";

const SIDEBAR_WIDTH = 240;

export default function MainLayout() {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar width={SIDEBAR_WIDTH} />
      <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column", ml: `${SIDEBAR_WIDTH}px` }}>
        <Header />
        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: "64px" }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
