import { Box, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <Box sx={{ textAlign: "center", mt: 8 }}>
      <Typography variant="h3" fontWeight={700}>404</Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>Page not found</Typography>
      <Button variant="contained" onClick={() => navigate("/dashboard")}>Go to Dashboard</Button>
    </Box>
  );
}
