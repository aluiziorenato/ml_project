import React from "react";
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Divider,
} from "@mui/material";
import { Link as RouterLink, useLocation } from "react-router-dom";
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Dashboard as DashboardIcon,
  Flag as FlagIcon,
  Inventory as InventoryIcon,
  ListAlt as ListAltIcon,
  Campaign as CampaignIcon,
  Build as BuildIcon,
  Psychology as PsychologyIcon,
} from "@mui/icons-material";

const menuItems = [
  { label: "Dashboard", icon: <DashboardIcon />, path: "/dashboard" },
  { label: "Modo Estratégico", icon: <FlagIcon />, path: "/estrategico" },
  { label: "Produtos", icon: <InventoryIcon />, path: "/produtos" },
  { label: "Pedidos", icon: <ListAltIcon />, path: "/pedidos" },
  { label: "Campanhas", icon: <CampaignIcon />, path: "/campanhas" },
  { label: "Anúncios", icon: <BuildIcon />, path: "/anuncios" },
  { label: "SEO Intelligence", icon: <PsychologyIcon />, path: "/seo" },
];

export default function Sidebar({ open, toggleCollapse }) {
  const location = useLocation();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        bgcolor: "background.paper",
        color: "text.primary",
        overflowX: "hidden",
        transition: "width 0.3s ease",
      }}
    >
      {/* Botão de recolher/expandir */}
      <Box display="flex" justifyContent={open ? "flex-end" : "center"} p={1}>
        <Tooltip title={open ? "Recolher menu" : "Expandir menu"}>
          <IconButton onClick={toggleCollapse} size="small" aria-label="toggle sidebar">
            {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Divider />

      {/* Lista de navegação */}
      <List>
        {menuItems.map(({ label, icon, path }) => {
          const isActive = location.pathname === path;

          return (
            <ListItemButton
              key={label}
              component={RouterLink}
              to={path}
              selected={isActive}
              sx={{
                "&:hover .MuiListItemIcon-root": {
                  color: "primary.main",
                  transform: "scale(1.2)",
                },
                transition: "all 0.2s ease",
                px: open ? 2 : 1,
                justifyContent: open ? "flex-start" : "center",
              }}
            >
              <ListItemIcon
                sx={{
                  color: isActive ? "primary.main" : "text.secondary",
                  transition: "0.2s",
                  minWidth: 0,
                  mr: open ? 2 : 0,
                }}
              >
                {icon}
              </ListItemIcon>
              {open && <ListItemText primary={label} />}
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );
}
