import React from "react";
import { Box, Divider } from "@mui/material";
import Sidebar from "./Sidebar";
import Header from "./Header";
import { Outlet } from "react-router-dom";

export default function Layout({ sidebarOpen, toggleSidebar, mode, toggleColorMode }) {
  const sidebarStyles = {
    width: sidebarOpen ? 240 : 60,
    transition: "width 0.3s ease",
    bgcolor: "grey.100",
    borderRight: "1px solid",
    display: "flex",
    flexDirection: "column",
  };

  return (
    <Box display="flex" minHeight="100vh">
      <Box sx={sidebarStyles}>
        <Sidebar open={sidebarOpen} toggleCollapse={toggleSidebar} />
      </Box>

      <Box flex={1} display="flex" flexDirection="column">
        <Header mode={mode} toggleColorMode={toggleColorMode} />
        <Divider />
        <Box component="main" flex={1} overflow="auto" p={3}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
