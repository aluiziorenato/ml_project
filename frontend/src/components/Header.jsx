import React from "react";
import { Box, Typography, IconButton, useTheme } from "@mui/material";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import SettingsIcon from "@mui/icons-material/Settings";
import { useNavigate } from "react-router-dom";

export default function Header({ mode, toggleColorMode }) {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <Box
      component="header"
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      px={3}
      py={2}
      bgcolor={theme.palette.background.paper}
      borderBottom={`1px solid ${theme.palette.divider}`}
    >
      <Typography variant="h6" fontWeight={500}>
        Dashboard
      </Typography>

      <Box>
        <IconButton onClick={toggleColorMode} color="inherit">
          {mode === "dark" ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>

        <IconButton onClick={() => navigate("/configuracoes")} color="inherit">
          <SettingsIcon />
        </IconButton>
      </Box>
    </Box>
  );
}
