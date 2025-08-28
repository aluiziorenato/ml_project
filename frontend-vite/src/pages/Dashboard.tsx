import React, { useState } from "react";
import { Box, AppBar, Toolbar, IconButton, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Tabs, Tab, Typography } from "@mui/material";
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import SettingsIcon from '@mui/icons-material/Settings';
import DashboardCards from '../components/Dashboard/DashboardCards';
import DashboardTable from '../components/Dashboard/DashboardTable';
import DashboardChart from '../components/Dashboard/DashboardChart';

const drawerWidth = 220;
import ScienceIcon from '@mui/icons-material/Science';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TuneIcon from '@mui/icons-material/Tune';
import StoreIcon from '@mui/icons-material/Store';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import ListAltIcon from '@mui/icons-material/ListAlt';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import InfoIcon from '@mui/icons-material/Info';

const menuItems = [
  { label: 'Dashboard', icon: <DashboardIcon />, page: 'dashboard' },
  { label: 'Relatórios', icon: <BarChartIcon />, page: 'relatorios' },
  { label: 'Configurações', icon: <SettingsIcon />, page: 'configuracoes' },
  { divider: true },
  { label: 'Inteligência Artificial', section: true },
  { label: 'Intenção Semântica', icon: <ScienceIcon />, page: 'intencao-semantica' },
  { label: 'Chatbot', icon: <SmartToyIcon />, page: 'chatbot' },
  { label: 'Detector de Tendências', icon: <TrendingUpIcon />, page: 'detector-tendencias' },
  { label: 'Otimização de ACOS', icon: <TuneIcon />, page: 'acos-management' },
  { label: 'Otimização de Campanhas', icon: <TuneIcon />, page: 'otimizacao-campanhas' },
  { divider: true },
  { label: 'Mercado Livre', section: true },
  { label: 'Produtos', icon: <StoreIcon />, page: 'produtos' },
  { label: 'Anúncios', icon: <ListAltIcon />, page: 'anuncios' },
  { label: 'Pedidos', icon: <ShoppingCartIcon />, page: 'pedidos' },
  { label: 'Concorrentes', icon: <GroupWorkIcon />, page: 'concorrentes' },
  { label: 'Dashboard de Produto', icon: <InfoIcon />, page: 'produto-dashboard' },
  { label: 'Detalhe do Produto', icon: <InfoIcon />, page: 'produto-detalhe' },
];

const Dashboard: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [tab, setTab] = useState(0);
  const [menuPage, setMenuPage] = useState('dashboard');

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f5f6fa' }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', background: '#222a36', color: '#fff' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item, idx) => {
              if (item.divider) return <Box key={idx} sx={{ my: 1, borderBottom: '1px solid #444' }} />;
              if (item.section) return (
                <Typography key={idx} variant="caption" sx={{ color: '#90caf9', pl: 2, pt: 1, pb: 0.5 }}>{item.label}</Typography>
              );
              return (
                <ListItemButton
                  key={item.page}
                  selected={menuPage === item.page}
                  onClick={() => setMenuPage(item.page ?? '')}
                  sx={{ borderRadius: 2, mb: 1 }}
                >
                  <ListItemIcon sx={{ color: '#fff' }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              );
            })}
          </List>
        </Box>
      </Drawer>
      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 4 }}>
        {/* Header */}
        <AppBar position="static" elevation={0} sx={{ background: '#fff', color: '#222a36', mb: 4 }}>
          <Toolbar>
            <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }} onClick={() => setDrawerOpen(!drawerOpen)}>
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Dashboard Community
            </Typography>
          </Toolbar>
        </AppBar>
        {/* Tabs para navegação interna */}
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
          <Tab label="Resumo" />
          <Tab label="Vendedores" />
          <Tab label="Gráficos" />
        </Tabs>
        {/* Cards Detalhados */}
        {tab === 0 && <DashboardCards />}
        {/* Tabela de Dados com filtros e exportação */}
        {tab === 1 && <DashboardTable />}
        {/* Gráfico dinâmico */}
        {tab === 2 && <DashboardChart />}
      </Box>
    </Box>
  );
};

export default Dashboard;
