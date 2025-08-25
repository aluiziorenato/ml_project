import { createTheme } from "@mui/material/styles";

const grafanaTheme = (mode = "dark") => {
  const isDark = mode === "dark";

  return createTheme({
    palette: {
      mode,
      primary: {
        main: "#00bcd4", // Azul vibrante estilo Grafana
      },
      secondary: {
        main: "#ff9800", // Laranja para destaque
      },
      background: {
        default: isDark ? "#1f2a36" : "#f4f6f8",
        paper: isDark ? "#2c3e50" : "#ffffff",
      },
      text: {
        primary: isDark ? "#ffffff" : "#1a1a1a",
        secondary: isDark ? "#b0bec5" : "#5f6368",
      },
      divider: isDark ? "#37474f" : "#cfd8dc",
    },

    typography: {
      fontFamily: "'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif",
      fontSize: 14,
      h1: { fontSize: "2rem", fontWeight: 600 },
      h2: { fontSize: "1.75rem", fontWeight: 500 },
      h3: { fontSize: "1.5rem", fontWeight: 500 },
      h4: { fontSize: "1.25rem", fontWeight: 500 },
      h5: { fontSize: "1rem", fontWeight: 500 },
      h6: { fontSize: "0.875rem", fontWeight: 500 },
    },

    shape: {
      borderRadius: 8,
    },

    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 500,
          },
        },
      },
      MuiInputBase: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? "#263238" : "#ffffff",
            borderRadius: 4,
          },
        },
      },
    },
  });
};

export default grafanaTheme;
