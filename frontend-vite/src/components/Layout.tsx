import React, { useEffect, useRef } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Drawer, List, ListItem, ListItemText, ListItemIcon, Toolbar, AppBar, Typography, Box, Divider, IconButton } from "@mui/material";
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import DashboardIcon from '@mui/icons-material/Dashboard';
import StoreIcon from '@mui/icons-material/Store';
import CampaignIcon from '@mui/icons-material/Campaign';
import GroupIcon from '@mui/icons-material/Group';
import ChatIcon from '@mui/icons-material/Chat';
import TuneIcon from '@mui/icons-material/Tune';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PieChartIcon from '@mui/icons-material/PieChart';
import SearchIcon from '@mui/icons-material/Search';
import InsightsIcon from '@mui/icons-material/Insights';
import CategoryIcon from '@mui/icons-material/Category';
import MonitorIcon from '@mui/icons-material/Monitor';
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';
import PersonIcon from '@mui/icons-material/Person';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import Header from './Header';

const menu = [
  { label: "Dashboard", to: "/", icon: <DashboardIcon /> },
  { label: "Produtos", to: "/produtos", icon: <StoreIcon /> },
  { label: "Campanhas", to: "/campanhas", icon: <CampaignIcon /> },
  { label: "Concorrentes", to: "/concorrentes", icon: <GroupIcon /> },
  { label: "Competidor Inteligente", to: "/competitor-intelligence", icon: <InsightsIcon /> },
  { label: "Chatbot", to: "/chatbot", icon: <ChatIcon /> },
  { label: "Otimização", to: "/otimizacao", icon: <TuneIcon /> },
  { label: "Tendências", to: "/tendencias", icon: <TrendingUpIcon /> },
  { label: "ROI", to: "/roi", icon: <PieChartIcon /> },
  { label: "SEO Visual", to: "/seo-visual", icon: <SearchIcon /> },
  { label: "Intenção Semântica", to: "/intencao-semantica", icon: <InsightsIcon /> },
  { label: "Detector de Tendências", to: "/detector-tendencias", icon: <TrendingUpIcon /> },
  { label: "Categorias", to: "/categorias", icon: <CategoryIcon /> },
  { label: "Monitoramento", to: "/monitoramento", icon: <MonitorIcon /> },
  { label: "Integração ML", to: "/integracao-ml", icon: <IntegrationInstructionsIcon /> },
  { label: "Perfil/Autenticação", to: "/auth", icon: <PersonIcon /> },
  { label: "Calendário", to: "/calendario", icon: <CalendarMonthIcon /> },
];
const clickAudio = typeof window !== 'undefined' ? new window.Audio('/click.mp3') : null;

interface LayoutProps {
  sidebarOpen?: boolean;
  toggleSidebar: () => void;
  mode: string;
  toggleColorMode: () => void;
}

const Layout: React.FC<LayoutProps> = ({ sidebarOpen = false, toggleSidebar, mode, toggleColorMode }) => {
  const timerRef = useRef<any>();
  useEffect(() => {
    if (sidebarOpen) {
      timerRef.current = setTimeout(() => {
        toggleSidebar();
      }, 15000);
    } else {
      clearTimeout(timerRef.current);
    }
    return () => clearTimeout(timerRef.current);
  }, [sidebarOpen, toggleSidebar]);
  const location = useLocation();
  const sidebarStyles = {
    width: sidebarOpen ? 240 : 60,
    transition: "width 0.3s ease",
    bgcolor: "grey.100",
  };
  return (
    <Box>
      {/* Renderize o layout conforme necessário */}
      {/* ...existing code... */}
    </Box>
  );
};

export default Layout;
