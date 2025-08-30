import NovoAnuncioML from './pages/NovoAnuncioML';
import MarketPulse from './pages/MarketPulse';
import MetricasPage from './pages/MetricasPage';
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/Dashboard';
import AnunciosPage from './pages/AnunciosPage';
import ProductsPage from './pages/Produtos';
import IntencaoSemantica from './pages/IntencaoSemantica';
import IntencoesBuscaPage from './pages/IntencoesBuscaPage';
import Chatbot from './pages/Chatbot';
import DetectorTendencias from './pages/DetectorTendencias';
import ACOSManagement from './pages/ACOSManagement';
import Campanhas from './pages/Campanhas';
import Pedidos from './pages/Pedidos';
import Concorrentes from './pages/Concorrentes';
import ProdutoDetalhe from './pages/ProdutoDetalhe';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/anuncios" element={<AnunciosPage />} />
        <Route path="/produtos" element={<ProductsPage />} />
        <Route path="/intencao-semantica" element={<IntencaoSemantica />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/detector-tendencias" element={<DetectorTendencias />} />
        <Route path="/acos-management" element={<ACOSManagement />} />
        <Route path="/otimizacao-campanhas" element={<Campanhas />} />
        <Route path="/pedidos" element={<Pedidos />} />
        <Route path="/concorrentes" element={<Concorrentes />} />
        <Route path="/produto-detalhe" element={<ProdutoDetalhe />} />
        <Route path="/novo-anuncio" element={<NovoAnuncioML />} />
        <Route path="/metricas" element={<MetricasPage />} />
        <Route path="/intencoes-busca" element={<IntencoesBuscaPage />} />
        <Route path="/market-pulse" element={<MarketPulse />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
