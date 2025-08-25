// src/theme/grafanaTheme.js

import { createTheme } from "@mui/material/styles";

const grafanaTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      ...(mode === "dark"
        ? {
            background: {
              default: "#121212",
              paper: "#1E1E1E",
            },
            text: {
              primary: "#ffffff",
              secondary: "#aaaaaa",
            },
            divider: "#333",
          }
        : {}),
    },
    components: {
      MuiGrid2: {
        defaultProps: {
          disableEqualOverflow: true,
        },
      },
    },
  });

export default grafanaTheme;
