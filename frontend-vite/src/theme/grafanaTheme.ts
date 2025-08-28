import { createTheme } from "@mui/material/styles";

const grafanaTheme = (mode: "light" | "dark" = "dark") => {
  const isDark = mode === "dark";

  return createTheme({
    palette: {
      mode,
      primary: { main: "#2563EB" },
      secondary: { main: "#F59E0B" },
      success: { main: "#10B981" },
      error: { main: "#EF4444" },
      warning: { main: "#F59E0B" },
      background: {
        default: isDark ? "#1F2937" : "#F9FAFB",
        paper: isDark ? "#2C3E50" : "#FFFFFF",
      },
      text: {
        primary: isDark ? "#FFFFFF" : "#1F2937",
        secondary: isDark ? "#B0BEC5" : "#5F6368",
      },
      divider: isDark ? "#37474F" : "#CFD8DC",
    },
    components: {
      MuiGrid: {
        defaultProps: { },
      },
      MuiPaper: {
        styleOverrides: { root: { backgroundImage: "none" } },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 500,
            borderRadius: 6,
            padding: "8px 16px",
            boxShadow: "none",
            "&:hover": { opacity: 0.9 },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderLeft: `4px solid ${isDark ? "#2563EB" : "#2563EB"}`,
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          },
        },
      },
      MuiInputBase: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? "#263238" : "#FFFFFF",
            borderRadius: 4,
          },
        },
      },
    },
  });
};

export default grafanaTheme;
