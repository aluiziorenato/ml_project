import React from "react";
import { AppBar, Toolbar, Typography, IconButton, useTheme } from "@mui/material";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import SettingsIcon from "@mui/icons-material/Settings";
import { useNavigate } from "react-router-dom";

export default function Header({ mode, toggleColorMode }) {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <AppBar position="static" color="default" component="header" sx={{ mb: 2 }}>
      <Toolbar>
        <Typography variant="h6" color="inherit" noWrap sx={{ flexGrow: 1 }}>
          ML Automation Dashboard
        </Typography>

        <IconButton onClick={toggleColorMode} color="inherit">
          {mode === "dark" ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>

        <IconButton onClick={() => navigate("/configuracoes")} color="inherit">
          <SettingsIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}
