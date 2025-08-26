import React from "react"
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Divider,
} from "@mui/material"
import { Link as RouterLink, useLocation } from "react-router-dom"
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
} from "@mui/icons-material"

// Definimos o array de itens já com a cor desejada
const menuItems = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: <DashboardIcon />,
    color: "primary.main",
  },
  {
    label: "Modo Estratégico",
    path: "/estrategico",
    icon: <FlagIcon />,
    color: "error.main",
  },
  {
    label: "Produtos",
    path: "/produtos",
    icon: <InventoryIcon />,
    color: "warning.main",
  },
  {
    label: "Pedidos",
    path: "/pedidos",
    icon: <ListAltIcon />,
    color: "success.main",
  },
  {
    label: "Campanhas",
    path: "/campanhas",
    icon: <CampaignIcon />,
    color: "info.main",
  },
  {
    label: "Anúncios",
    path: "/anuncios",
    icon: <BuildIcon />,
    color: "secondary.main",
  },
  {
    label: "SEO Intelligence",
    path: "/seo",
    icon: <PsychologyIcon />,
    color: "text.primary",
  },
]

export default function Sidebar({ open, toggleCollapse }) {
  const location = useLocation()

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
          <IconButton
            onClick={toggleCollapse}
            size="small"
            aria-label="toggle sidebar"
          >
            {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Divider />

      {/* Lista de navegação */}
      <List sx={{ overflowX: "visible" }}>
        {menuItems.map(({ label, path, icon, color }) => {
          const isActive = location.pathname === path

          return (
            <ListItemButton
              key={path}
              component={RouterLink}
              to={path}
              selected={isActive}
              sx={{
                px: open ? 2 : 1,
                justifyContent: open ? "flex-start" : "center",
                transition: "all 0.2s ease",
                "&:hover .MuiListItemIcon-root": {
                  color,
                  transform: "scale(1.2)",
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: isActive ? color : "text.secondary",
                  transition: "color 0.2s, transform 0.2s",
                  minWidth: 0,
                  mr: open ? 2 : 0,
                }}
              >
                {icon}
              </ListItemIcon>

              {open && <ListItemText primary={label} />}
            </ListItemButton>
          )
        })}
      </List>
    </Box>
  )
}
