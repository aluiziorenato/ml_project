import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const CampaignDeactivationDialog = ({ isOpen, campaign, onConfirm, onCancel }) => {
    const [reason, setReason] = useState('');
    const [selectedReason, setSelectedReason] = useState('');
    const [showImpactAnalysis, setShowImpactAnalysis] = useState(false);
    const [alternativeActions, setAlternativeActions] = useState([]);

    const deactivationReasons = [
        { id: 'poor_performance', label: 'Performance Baixa', icon: '📉' },
        { id: 'budget_exceeded', label: 'Orçamento Excedido', icon: '💸' },
        { id: 'high_acos', label: 'ACOS Muito Alto', icon: '📈' },
        { id: 'strategic_change', label: 'Mudança Estratégica', icon: '🎯' },
        { id: 'seasonal_end', label: 'Fim da Sazonalidade', icon: '📅' },
        { id: 'product_issues', label: 'Problemas no Produto', icon: '📦' },
        { id: 'other', label: 'Outro Motivo', icon: '🤔' }
    ];

    const impactAnalysis = campaign ? {
        estimatedRevenueLoss: (campaign.daily_revenue || 0) * 30,
        affectedKeywords: campaign.keywords?.length || 0,
        currentPosition: campaign.avg_position || 0,
        competitorAdvantage: 'Concorrentes podem ganhar posição',
        recoveryTime: '7-14 dias para recuperar posições'
    } : {};

    const generateAlternatives = (reason) => {
        const alternatives = {
            poor_performance: [
                { action: 'Otimizar palavras-chave', icon: '🔍', description: 'Pausar palavras com baixo desempenho' },
                { action: 'Ajustar lances', icon: '💰', description: 'Reduzir lances em 20-30%' },
                { action: 'Melhorar criativos', icon: '🎨', description: 'Testar novos títulos e imagens' }
            ],
            budget_exceeded: [
                { action: 'Reduzir budget diário', icon: '📊', description: 'Diminuir budget em 25%' },
                { action: 'Pausar campanhas secundárias', icon: '⏸️', description: 'Focar nas campanhas principais' },
                { action: 'Implementar dayparting', icon: '🕐', description: 'Rodar apenas nos melhores horários' }
            ],
            high_acos: [
                { action: 'Revisar targeting', icon: '🎯', description: 'Ajustar público-alvo' },
                { action: 'Otimizar landing page', icon: '📄', description: 'Melhorar taxa de conversão' },
                { action: 'Implementar lances negativos', icon: '🚫', description: 'Excluir termos irrelevantes' }
            ],
            default: [
                { action: 'Pausar temporariamente', icon: '⏸️', description: 'Pausar por 7 dias' },
                { action: 'Reduzir investimento', icon: '📉', description: 'Reduzir budget em 50%' },
                { action: 'Análise detalhada', icon: '🔍', description: 'Investigar causas específicas' }
            ]
        };

        return alternatives[reason] || alternatives.default;
    };

    const handleReasonChange = (reasonId) => {
        setSelectedReason(reasonId);
        setAlternativeActions(generateAlternatives(reasonId));
        setShowImpactAnalysis(true);
    };

    const handleConfirmDeactivation = () => {
        onConfirm({
            reason: selectedReason,
            customReason: reason,
            timestamp: new Date().toISOString()
        });
    };

    if (!isOpen || !campaign) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
                onClick={onCancel}
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="bg-red-500 text-white p-6 rounded-t-lg">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-2xl font-bold">⚠️ Confirmar Desativação</h2>
                                <p className="text-red-100 mt-1">
                                    Você está prestes a desativar a campanha: <strong>{campaign.name}</strong>
                                </p>
                            </div>
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={onCancel}
                                className="text-white hover:text-red-200"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </motion.button>
                        </div>
                    </div>

                    <div className="p-6 space-y-6">
                        {/* Campaign Summary */}
                        <div className="bg-gray-50 rounded-lg p-4">
                            <h3 className="font-semibold mb-3">📊 Resumo da Campanha</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-blue-600">
                                        R$ {(campaign.budget || 0).toLocaleString()}
                                    </div>
                                    <div className="text-sm text-gray-600">Budget Diário</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-600">
                                        {(campaign.acos || 0).toFixed(1)}%
                                    </div>
                                    <div className="text-sm text-gray-600">ACOS Atual</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-purple-600">
                                        {campaign.clicks || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Cliques (30d)</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-orange-600">
                                        {campaign.conversions || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Conversões (30d)</div>
                                </div>
                            </div>
                        </div>

                        {/* Reason Selection */}
                        <div>
                            <h3 className="font-semibold mb-3">🤔 Por que desativar esta campanha?</h3>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {deactivationReasons.map((reasonOption) => (
                                    <motion.button
                                        key={reasonOption.id}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => handleReasonChange(reasonOption.id)}
                                        className={`p-4 border-2 rounded-lg text-left transition-all ${
                                            selectedReason === reasonOption.id
                                                ? 'border-red-500 bg-red-50'
                                                : 'border-gray-200 hover:border-red-300'
                                        }`}
                                    >
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xl">{reasonOption.icon}</span>
                                            <span className="font-medium">{reasonOption.label}</span>
                                        </div>
                                    </motion.button>
                                ))}
                            </div>

                            {selectedReason === 'other' && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="mt-4"
                                >
                                    <textarea
                                        value={reason}
                                        onChange={(e) => setReason(e.target.value)}
                                        placeholder="Descreva o motivo..."
                                        className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                                        rows="3"
                                    />
                                </motion.div>
                            )}
                        </div>

                        {/* Impact Analysis */}
                        <AnimatePresence>
                            {showImpactAnalysis && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="bg-yellow-50 border border-yellow-200 rounded-lg p-6"
                                >
                                    <h3 className="font-semibold text-yellow-800 mb-4">
                                        📈 Análise de Impacto da Desativação
                                    </h3>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <h4 className="font-medium text-yellow-700 mb-2">Impactos Estimados:</h4>
                                            <ul className="space-y-2 text-sm text-yellow-700">
                                                <li className="flex items-center space-x-2">
                                                    <span>💰</span>
                                                    <span>Perda de receita: R$ {impactAnalysis.estimatedRevenueLoss?.toLocaleString()}/mês</span>
                                                </li>
                                                <li className="flex items-center space-x-2">
                                                    <span>🔍</span>
                                                    <span>{impactAnalysis.affectedKeywords} palavras-chave afetadas</span>
                                                </li>
                                                <li className="flex items-center space-x-2">
                                                    <span>📊</span>
                                                    <span>Perda de posição atual: #{impactAnalysis.currentPosition}</span>
                                                </li>
                                                <li className="flex items-center space-x-2">
                                                    <span>🏃</span>
                                                    <span>{impactAnalysis.competitorAdvantage}</span>
                                                </li>
                                                <li className="flex items-center space-x-2">
                                                    <span>⏰</span>
                                                    <span>Tempo de recuperação: {impactAnalysis.recoveryTime}</span>
                                                </li>
                                            </ul>
                                        </div>

                                        <div>
                                            <h4 className="font-medium text-yellow-700 mb-2">Possíveis Consequências:</h4>
                                            <ul className="space-y-2 text-sm text-yellow-700">
                                                <li>• Concorrentes podem ocupar nossas posições</li>
                                                <li>• Redução na visibilidade da marca</li>
                                                <li>• Perda de momentum nas vendas</li>
                                                <li>• Dificuldade para reconquistar posições</li>
                                                <li>• Impacto no ranking orgânico</li>
                                            </ul>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Alternative Actions */}
                        <AnimatePresence>
                            {alternativeActions.length > 0 && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className="bg-blue-50 border border-blue-200 rounded-lg p-6"
                                >
                                    <h3 className="font-semibold text-blue-800 mb-4">
                                        💡 Considere Estas Alternativas Antes de Desativar
                                    </h3>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        {alternativeActions.map((alternative, index) => (
                                            <motion.div
                                                key={index}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: index * 0.1 }}
                                                className="bg-white border border-blue-300 rounded-lg p-4"
                                            >
                                                <div className="flex items-center space-x-2 mb-2">
                                                    <span className="text-xl">{alternative.icon}</span>
                                                    <span className="font-medium text-blue-800">{alternative.action}</span>
                                                </div>
                                                <p className="text-sm text-blue-700">{alternative.description}</p>
                                                <motion.button
                                                    whileHover={{ scale: 1.02 }}
                                                    whileTap={{ scale: 0.98 }}
                                                    className="mt-3 w-full bg-blue-500 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-600"
                                                >
                                                    Aplicar Agora
                                                </motion.button>
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Final Confirmation */}
                        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                            <h3 className="font-semibold text-red-800 mb-4">
                                ⚠️ Confirmação Final
                            </h3>
                            <div className="bg-white border border-red-300 rounded-lg p-4 mb-4">
                                <div className="flex items-start space-x-3">
                                    <div className="text-2xl">🚨</div>
                                    <div>
                                        <p className="text-red-700 font-medium">
                                            Esta ação não pode ser desfeita facilmente.
                                        </p>
                                        <p className="text-red-600 text-sm mt-1">
                                            A campanha será desativada imediatamente e pode levar tempo para recuperar as posições atuais.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center mb-4">
                                <input
                                    type="checkbox"
                                    id="confirm-understanding"
                                    className="mr-2"
                                    required
                                />
                                <label htmlFor="confirm-understanding" className="text-sm text-red-700">
                                    Entendo os riscos e impactos da desativação desta campanha
                                </label>
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex space-x-4">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={onCancel}
                                className="flex-1 bg-gray-300 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-400"
                            >
                                ↩️ Cancelar
                            </motion.button>

                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handleConfirmDeactivation}
                                disabled={!selectedReason}
                                className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                                    selectedReason
                                        ? 'bg-red-500 text-white hover:bg-red-600'
                                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                }`}
                            >
                                🛑 Confirmar Desativação
                            </motion.button>
                        </div>

                        {/* Additional Safety Warning */}
                        <div className="text-center">
                            <p className="text-xs text-gray-500">
                                💡 Dica: Considere pausar temporariamente ao invés de desativar permanentemente
                            </p>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

export default CampaignDeactivationDialog;