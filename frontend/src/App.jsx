import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";

import useThemeMode from "./hooks/useThemeMode";
import grafanaTheme from "./theme/grafanaTheme";

import Layout from "./components/Layout";

// Páginas
import Dashboard from "./pages/Dashboard";
import Pedidos from "./pages/Pedidos";
import ApiConfig from "./pages/ApiConfig";
import Products from "./pages/Products";          // ✅ Página de produtos
import ProdutoDetalhe from "./pages/ProdutoDetalhe"; // ✅ Página de detalhe

export default function App() {
  const { mode, toggleColorMode } = useThemeMode();
  const theme = grafanaTheme(mode);

  const [sidebarOpen, setSidebarOpen] = useState(true);
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
            <Route index element={<Dashboard />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="pedidos" element={<Pedidos />} />
            <Route path="configuracoes" element={<ApiConfig />} />

            {/* ✅ Novas rotas */}
            <Route path="produtos" element={<Products />} />
            <Route path="produto/:id" element={<ProdutoDetalhe />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
