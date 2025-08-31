import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CampaignList from './components/CampaignList';
import StrategyPanel from './components/StrategyPanel';
import HistoryModal from './components/HistoryModal';
import WeeklyScheduler from './components/WeeklyScheduler';

import Dashboard from './pages/Dashboard.tsx';
import Chatbot from './pages/Chatbot';
import DetectorTendencias from './pages/DetectorTendencias';
import Pedidos from './pages/Pedidos';
import ProdutoDetalhe from './pages/ProdutoDetalhe';
import ProdutoDashboard from './pages/ProdutoDashboard';
import Concorrentes from './pages/Concorrentes';
import ACOSManagement from './pages/ACOSManagement';
import AnunciosPage from './pages/AnunciosPage';
import ApiConfig from './pages/ApiConfig';
import ApiTester from './pages/ApiTester';
import Campaigns from './pages/Campaigns';
import Campanhas from './pages/Campanhas';
import ChatbotUpload from './pages/ChatbotUpload';
import CompetitorIntelligence from './pages/CompetitorIntelligence';
import ComprehensiveDashboard from './pages/ComprehensiveDashboard';
import GridMuiTest from './pages/GridMuiTest';
import IntencaoSemantica from './pages/IntencaoSemantica';
import IntencoesBuscaPage from './pages/IntencoesBuscaPage';
import MarketPulse from './pages/MarketPulse';
import MetricasPage from './pages/MetricasPage';
import NovoAnuncioML from './pages/NovoAnuncioML';
import NovoAnuncioML_backup from './pages/NovoAnuncioML_backup';
import OAuthManager from './pages/OAuthManager';
import Orders from './pages/Orders';
import Otimizacao from './pages/Otimizacao';
import OtimizacaoTest from './pages/OtimizacaoTest';
import Products from './pages/Products';
import Produtos from './pages/Produtos';
import ROI from './pages/ROI';
import SEOIntelligenceDashboard from './pages/SEOIntelligenceDashboard';
import SEOVisual from './pages/SEOVisual';
import StrategicMode from './pages/StrategicMode';
import Tendencias from './pages/Tendencias';
import DynamicOptimization from './pages/DynamicOptimization';

// Constantes globais
const MODES = [
  'competitivo', 'defensivo', 'otimizacao', 'retreinamento', 'monitoramento', 'coopeticao', 'observacao'
];
const WEEK_DAYS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
const HOURS = Array.from({ length: 24 }, (_, i) => `${i}:00`);
const MOCK_LAST_UPDATE = '30/08/2025 10:00';

// Mock inicial para campanhas e histórico
const MOCK_CAMPAIGNS = [
  { id: 1, name: 'Campanha A', activeMode: 'competitivo' },
  { id: 2, name: 'Campanha B', activeMode: 'defensivo' }
];
const MOCK_HISTORY = [
  'Modo competitivo ativado na Campanha A',
  'Orçamento ajustado na Campanha B'
];
const MOCK_SCHEDULE = (() => {
  const arr = Array(7).fill().map(() => Array(24).fill(false));
  arr[0][9] = true;
  arr[2][15] = true;
  return arr;
})();

function App() {
  // Estados e funções da tela de otimização dinâmica
  // ...existing code...

  // Renderização principal: Dashboard sempre visível, conteúdo muda via Outlet
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />}>
          <Route index element={<Dashboard />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chatbot" element={<Chatbot />} />
          <Route path="detector-tendencias" element={<DetectorTendencias />} />
          <Route path="pedidos" element={<Pedidos />} />
          <Route path="produto-detalhe" element={<ProdutoDetalhe />} />
          <Route path="produto-dashboard" element={<ProdutoDashboard />} />
          <Route path="concorrentes" element={<Concorrentes />} />
          <Route path="acos-management" element={<ACOSManagement />} />
          <Route path="anuncios" element={<AnunciosPage />} />
          <Route path="api-config" element={<ApiConfig />} />
          <Route path="api-tester" element={<ApiTester />} />
          <Route path="campaigns" element={<Campaigns />} />
          <Route path="otimizacao-campanhas" element={<Otimizacao />} />
          <Route path="campanhas" element={<Campanhas />} />
          <Route path="chatbot-upload" element={<ChatbotUpload />} />
          <Route path="competitor-intelligence" element={<CompetitorIntelligence />} />
          <Route path="comprehensive-dashboard" element={<ComprehensiveDashboard />} />
          <Route path="grid-mui-test" element={<GridMuiTest />} />
          <Route path="intencao-semantica" element={<IntencaoSemantica />} />
          <Route path="intencoes-busca" element={<IntencoesBuscaPage />} />
          <Route path="market-pulse" element={<MarketPulse />} />
          <Route path="metricas" element={<MetricasPage />} />
          <Route path="novo-anuncio" element={<NovoAnuncioML />} />
          <Route path="novo-anuncio-ml" element={<NovoAnuncioML />} />
          <Route path="novo-anuncio-ml-backup" element={<NovoAnuncioML_backup />} />
          <Route path="oauth-manager" element={<OAuthManager />} />
          <Route path="orders" element={<Orders />} />
          <Route path="otimizacao" element={<Otimizacao />} />
          <Route path="otimizacao-test" element={<OtimizacaoTest />} />
          <Route path="products" element={<Products />} />
          <Route path="produtos" element={<Produtos />} />
          <Route path="roi" element={<ROI />} />
          <Route path="seo-intelligence-dashboard" element={<SEOIntelligenceDashboard />} />
          <Route path="seo-visual" element={<SEOVisual />} />
          <Route path="strategic-mode" element={<StrategicMode />} />
          <Route path="tendencias" element={<Tendencias />} />
          <Route path="dynamic-optimization" element={<DynamicOptimization />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
