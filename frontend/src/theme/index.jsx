import { useMemo } from "react";
import { CssBaseline } from "@mui/material";
import { createTheme, ThemeProvider as MuiThemeProvider } from "@mui/material/styles";
import palette from "./palette";
import typography from "./typography";

export default function ThemeProvider({ children }) {
  const theme = useMemo(
    () =>
      createTheme({
        palette,
        typography,
        shape: { borderRadius: 8 },
        components: {
          MuiButton: { styleOverrides: { root: { textTransform: "none", fontWeight: 600 } } },
          MuiListItemButton: { styleOverrides: { root: { "&.Mui-selected": { fontWeight: 600 } } } },
        },
      }),
    []
  );

  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  );
}
