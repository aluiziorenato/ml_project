import React from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import ACOSManagement from "./pages/ACOSManagement";
import AnunciosPage from "./pages/AnunciosPage";
import Campanhas from "./pages/Campanhas";
import Chatbot from "./pages/Chatbot";
import Concorrentes from "./pages/Concorrentes";
import DashboardPage from "./pages/Dashboard";
import DetectorTendencias from "./pages/DetectorTendencias";
import DynamicOptimization from "./pages/DynamicOptimization";
import IntencaoSemantica from "./pages/IntencaoSemantica";
import IntencoesBuscaPage from "./pages/IntencoesBuscaPage";
import MarketPulse from "./pages/MarketPulse";
import MetricasPage from "./pages/MetricasPage";
import NovoAnuncioML from "./pages/NovoAnuncioML";
import NovoAnuncio from "./pages/Products/NovoAnuncio";
import Otimizacao from "./pages/Otimizacao";
import Pedidos from "./pages/Pedidos";
import ProdutoDetalhe from "./pages/ProdutoDetalhe";
import ProductsPage from "./pages/Produtos";

function App() {
	return (
		<BrowserRouter>
			<nav className="bg-gray-100 p-4 flex gap-4 shadow">
				<Link to="/" className="font-bold text-blue-700 hover:underline">
					Dashboard
				</Link>
				<Link
					to="/dynamic-optimization"
					className="font-bold text-pink-700 hover:underline"
				>
					Otimização Dinâmica
				</Link>
				{/* Adicione outros links conforme necessário */}
			</nav>
			<Routes>
				<Route path="/" element={<DashboardPage />} />
				<Route path="/dashboard" element={<DashboardPage />} />
				<Route path="/anuncios" element={<AnunciosPage />} />
				<Route path="/produtos" element={<ProductsPage />} />
				<Route path="/intencao-semantica" element={<IntencaoSemantica />} />
				<Route path="/chatbot" element={<Chatbot />} />
				<Route path="/detector-tendencias" element={<DetectorTendencias />} />
				<Route path="/acos-management" element={<ACOSManagement />} />
				<Route path="/otimizacao-campanhas" element={<Otimizacao />} />
				<Route path="/pedidos" element={<Pedidos />} />
				<Route path="/concorrentes" element={<Concorrentes />} />
				<Route path="/produto-detalhe" element={<ProdutoDetalhe />} />
				<Route path="/novo-anuncio" element={<NovoAnuncio />} />
				<Route path="/metricas" element={<MetricasPage />} />
				<Route path="/intencoes-busca" element={<IntencoesBuscaPage />} />
				<Route path="/market-pulse" element={<MarketPulse />} />
				<Route path="/dynamic-optimization" element={<DynamicOptimization />} />
			</Routes>
		</BrowserRouter>
	);
}

export default App;
