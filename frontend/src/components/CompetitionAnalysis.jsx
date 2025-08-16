import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const api = axios.create({ 
    baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
});

const CompetitionAnalysis = ({ userId }) => {
    const [competitionData, setCompetitionData] = useState([]);
    const [adCountData, setAdCountData] = useState([]);
    const [competitionResults, setCompetitionResults] = useState([]);
    const [marketShare, setMarketShare] = useState([]);
    const [selectedPeriod, setSelectedPeriod] = useState('7d');
    const [loading, setLoading] = useState(true);

    const COLORS = ['#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#F97316'];

    useEffect(() => {
        loadCompetitionData();
    }, [selectedPeriod]);

    const loadCompetitionData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            // Simulate API calls to competition intelligence service
            const competitionResponse = await axios.get(
                `http://localhost:8006/competition/analysis?period=${selectedPeriod}&user_id=${userId}`, 
                { headers }
            );

            // Mock data for demonstration
            const mockCompetitionData = [
                { date: '2024-01-01', ourPosition: 3, competitors: 15, avgPrice: 45.90, ourPrice: 43.50 },
                { date: '2024-01-02', ourPosition: 2, competitors: 18, avgPrice: 46.20, ourPrice: 44.00 },
                { date: '2024-01-03', ourPosition: 4, competitors: 12, avgPrice: 45.80, ourPrice: 42.90 },
                { date: '2024-01-04', ourPosition: 1, competitors: 20, avgPrice: 47.10, ourPrice: 45.20 },
                { date: '2024-01-05', ourPosition: 2, competitors: 16, avgPrice: 46.50, ourPrice: 44.80 },
                { date: '2024-01-06', ourPosition: 3, competitors: 14, avgPrice: 45.70, ourPrice: 43.90 },
                { date: '2024-01-07', ourPosition: 1, competitors: 22, avgPrice: 48.20, ourPrice: 46.10 },
            ];

            const mockAdCountData = [
                { keyword: 'smartphone', ourAds: 15, competitorAds: 45, totalCompeting: 8 },
                { keyword: 'notebook', ourAds: 12, competitorAds: 38, totalCompeting: 6 },
                { keyword: 'headphone', ourAds: 8, competitorAds: 25, totalCompeting: 5 },
                { keyword: 'tablet', ourAds: 10, competitorAds: 30, totalCompeting: 7 },
                { keyword: 'smartwatch', ourAds: 6, competitorAds: 18, totalCompeting: 4 },
            ];

            const mockCompetitionResults = [
                { competitor: 'Concorrente A', wins: 25, losses: 15, winRate: 62.5 },
                { competitor: 'Concorrente B', wins: 18, losses: 22, winRate: 45.0 },
                { competitor: 'Concorrente C', wins: 30, losses: 10, winRate: 75.0 },
                { competitor: 'Concorrente D', wins: 12, losses: 28, winRate: 30.0 },
                { competitor: 'Concorrente E', wins: 22, losses: 18, winRate: 55.0 },
            ];

            const mockMarketShare = [
                { name: 'Nossa Empresa', value: 28, color: '#8B5CF6' },
                { name: 'Concorrente A', value: 22, color: '#10B981' },
                { name: 'Concorrente B', value: 18, color: '#F59E0B' },
                { name: 'Concorrente C', value: 15, color: '#EF4444' },
                { name: 'Outros', value: 17, color: '#6B7280' },
            ];

            setCompetitionData(mockCompetitionData);
            setAdCountData(mockAdCountData);
            setCompetitionResults(mockCompetitionResults);
            setMarketShare(mockMarketShare);

        } catch (error) {
            console.error('Erro ao carregar dados de concorrência:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Period Selector */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-lg p-6"
            >
                <div className="flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-900">📊 Análise de Concorrência</h2>
                    <div className="flex space-x-2">
                        {['7d', '30d', '90d'].map((period) => (
                            <motion.button
                                key={period}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => setSelectedPeriod(period)}
                                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                                    selectedPeriod === period
                                        ? 'bg-indigo-500 text-white'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                {period === '7d' ? '7 dias' : period === '30d' ? '30 dias' : '90 dias'}
                            </motion.button>
                        ))}
                    </div>
                </div>
            </motion.div>

            {/* KPI Summary */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-4 gap-6"
            >
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                    <div className="text-3xl font-bold">
                        #{competitionData.length > 0 ? competitionData[competitionData.length - 1].ourPosition : '-'}
                    </div>
                    <div className="text-sm opacity-90">Posição Atual</div>
                </div>
                
                <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                    <div className="text-3xl font-bold">
                        {competitionResults.reduce((acc, curr) => acc + curr.wins, 0)}
                    </div>
                    <div className="text-sm opacity-90">Vitórias Totais</div>
                </div>
                
                <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-lg p-6 text-white">
                    <div className="text-3xl font-bold">
                        {adCountData.reduce((acc, curr) => acc + curr.ourAds, 0)}
                    </div>
                    <div className="text-sm opacity-90">Anúncios Ativos</div>
                </div>
                
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                    <div className="text-3xl font-bold">{marketShare[0]?.value || 0}%</div>
                    <div className="text-sm opacity-90">Market Share</div>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Position Tracking */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <h3 className="text-lg font-semibold mb-4">📈 Evolução da Posição</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={competitionData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis reversed domain={[1, 'dataMax']} />
                            <Tooltip 
                                formatter={(value, name) => [
                                    name === 'ourPosition' ? `#${value}` : value,
                                    name === 'ourPosition' ? 'Nossa Posição' : 'Concorrentes'
                                ]}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="ourPosition" 
                                stroke="#8B5CF6" 
                                strokeWidth={3}
                                dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="competitors" 
                                stroke="#10B981" 
                                strokeWidth={2}
                                dot={{ fill: '#10B981', strokeWidth: 2, r: 3 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Market Share */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <h3 className="text-lg font-semibold mb-4">🎯 Participação de Mercado</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={marketShare}
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                                label={({ name, value }) => `${name}: ${value}%`}
                            >
                                {marketShare.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </motion.div>
            </div>

            {/* Ad Competition Analysis */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-lg p-6"
            >
                <h3 className="text-lg font-semibold mb-4">🎯 Quantidade de Anúncios Concorrendo</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={adCountData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="keyword" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="ourAds" fill="#8B5CF6" name="Nossos Anúncios" />
                        <Bar dataKey="competitorAds" fill="#10B981" name="Anúncios Concorrentes" />
                    </BarChart>
                </ResponsiveContainer>
            </motion.div>

            {/* Competition Results Table */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-lg p-6"
            >
                <h3 className="text-lg font-semibold mb-4">🏆 Resultados da Concorrência</h3>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-200">
                                <th className="text-left py-3 px-4 font-medium text-gray-900">Concorrente</th>
                                <th className="text-center py-3 px-4 font-medium text-gray-900">Vitórias</th>
                                <th className="text-center py-3 px-4 font-medium text-gray-900">Derrotas</th>
                                <th className="text-center py-3 px-4 font-medium text-gray-900">Taxa de Vitória</th>
                                <th className="text-center py-3 px-4 font-medium text-gray-900">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {competitionResults.map((result, index) => (
                                <motion.tr
                                    key={index}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="border-b border-gray-100 hover:bg-gray-50"
                                >
                                    <td className="py-3 px-4 font-medium">{result.competitor}</td>
                                    <td className="py-3 px-4 text-center text-green-600 font-medium">
                                        {result.wins}
                                    </td>
                                    <td className="py-3 px-4 text-center text-red-600 font-medium">
                                        {result.losses}
                                    </td>
                                    <td className="py-3 px-4 text-center">
                                        <div className="flex items-center justify-center space-x-2">
                                            <div className="w-20 bg-gray-200 rounded-full h-2">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${result.winRate}%` }}
                                                    transition={{ duration: 1, delay: index * 0.1 }}
                                                    className={`h-2 rounded-full ${
                                                        result.winRate >= 70 ? 'bg-green-500' :
                                                        result.winRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                                                    }`}
                                                />
                                            </div>
                                            <span className="text-sm font-medium">{result.winRate}%</span>
                                        </div>
                                    </td>
                                    <td className="py-3 px-4 text-center">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            result.winRate >= 70 ? 'bg-green-100 text-green-800' :
                                            result.winRate >= 50 ? 'bg-yellow-100 text-yellow-800' : 
                                            'bg-red-100 text-red-800'
                                        }`}>
                                            {result.winRate >= 70 ? '🎯 Dominando' :
                                             result.winRate >= 50 ? '⚡ Competitivo' : '📉 Perdendo'}
                                        </span>
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </motion.div>

            {/* Price Analysis */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-lg p-6"
            >
                <h3 className="text-lg font-semibold mb-4">💰 Análise de Preços vs Concorrência</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={competitionData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip 
                            formatter={(value, name) => [
                                `R$ ${value}`,
                                name === 'ourPrice' ? 'Nosso Preço' : 'Preço Médio Concorrentes'
                            ]}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="ourPrice" 
                            stroke="#8B5CF6" 
                            strokeWidth={3}
                            dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="avgPrice" 
                            stroke="#EF4444" 
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={{ fill: '#EF4444', strokeWidth: 2, r: 3 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </motion.div>

            {/* Action Recommendations */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200"
            >
                <h3 className="text-lg font-semibold mb-4 text-blue-900">🤖 Recomendações de IA</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="text-lg">🎯</div>
                            <div className="font-medium text-blue-900">Oportunidade de Posicionamento</div>
                        </div>
                        <div className="text-sm text-blue-700">
                            Reduzir preço em 3-5% pode melhorar posição para #1 em palavras-chave estratégicas.
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="text-lg">💡</div>
                            <div className="font-medium text-blue-900">Expansão Recomendada</div>
                        </div>
                        <div className="text-sm text-blue-700">
                            Aumentar investimento em "smartwatch" - apenas 4 concorrentes ativos.
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="text-lg">⚠️</div>
                            <div className="font-medium text-blue-900">Alerta de Concorrência</div>
                        </div>
                        <div className="text-sm text-blue-700">
                            Concorrente C está ganhando market share rapidamente - monitorar estratégia.
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="text-lg">📊</div>
                            <div className="font-medium text-blue-900">Otimização de Budget</div>
                        </div>
                        <div className="text-sm text-blue-700">
                            Realocar 20% do budget de "tablet" para "smartphone" para melhor ROI.
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default CompetitionAnalysis;