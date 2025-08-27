import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";

import useThemeMode from "./hooks/useThemeMode";
import grafanaTheme from "./theme/grafanaTheme";

import Layout from "./components/Layout";
import DashboardLayout from "./pages/Dashboard/DashboardLayout";

// Páginas
import Dashboard from "./pages/Dashboard";
import Pedidos from "./pages/Pedidos";
import ApiConfig from "./pages/ApiConfig";
import Produtos from "./pages/Produtos";          // ✅ Página de produtos
import ProdutoDetalhe from "./pages/ProdutoDetalhe"; // ✅ Página de detalhe
import Campanhas from "./pages/Campanhas";
import Concorrentes from "./pages/Concorrentes";
import Chatbot from "./pages/Chatbot";
import Otimizacao from "./pages/Otimizacao";
import Tendencias from "./pages/Tendencias";
import ROI from "./pages/ROI";
import IntencaoSemantica from "./pages/IntencaoSemantica";
import DetectorTendencias from "./pages/DetectorTendencias";
import SEOVisual from "./pages/SEOVisual";
import ChatbotUpload from "./pages/ChatbotUpload";
import DashboardImagem from "./pages/Dashboard/DashboardImagem";

export default function App() {
  const { mode, toggleColorMode } = useThemeMode();
  const theme = grafanaTheme(mode);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              <Layout
                toggleColorMode={toggleColorMode}
                mode={mode}
                sidebarOpen={sidebarOpen}
                toggleSidebar={toggleSidebar}
              />
            }
          >
            <Route index element={<DashboardLayout />} />
            <Route path="dashboard" element={<DashboardLayout />} />
            <Route path="pedidos" element={<Pedidos />} />
            <Route path="configuracoes" element={<ApiConfig />} />

            {/* ✅ Novas rotas */}
            <Route path="produtos" element={<Produtos />} />
            <Route path="produto/:id" element={<ProdutoDetalhe />} />
            <Route path="campanhas" element={<Campanhas />} />
            <Route path="concorrentes" element={<Concorrentes />} />
            <Route path="chatbot" element={<Chatbot />} />
            <Route path="chatbot-upload" element={<ChatbotUpload />} />
            <Route path="otimizacao" element={<Otimizacao />} />
            <Route path="tendencias" element={<Tendencias />} />
            <Route path="roi" element={<ROI />} />
            <Route path="intencao-semantica" element={<IntencaoSemantica />} />
            <Route path="detector-tendencias" element={<DetectorTendencias />} />
            <Route path="seo-visual" element={<SEOVisual />} />
            <Route path="dashboard-ideia" element={<DashboardImagem />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
