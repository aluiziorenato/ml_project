import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const MarkupSafetyValidator = ({ onValidation, currentMarkup, productCost, productPrice }) => {
    const [validationResult, setValidationResult] = useState(null);
    const [safetyMargin, setSafetyMargin] = useState(10); // Default 10% safety margin
    const [loading, setLoading] = useState(false);
    const [showWarning, setShowWarning] = useState(false);

    useEffect(() => {
        if (currentMarkup && productCost && productPrice) {
            validateMarkup();
        }
    }, [currentMarkup, productCost, productPrice, safetyMargin]);

    const validateMarkup = async () => {
        setLoading(true);
        
        try {
            // Calculate profit margin
            const profitMargin = ((productPrice - productCost) / productPrice) * 100;
            const markupPercentage = parseFloat(currentMarkup);
            
            // Calculate remaining margin after ads
            const remainingMargin = profitMargin - markupPercentage;
            
            // Determine safety status
            let status = 'safe';
            let severity = 'low';
            let message = '';
            let recommendations = [];

            if (remainingMargin < safetyMargin) {
                status = 'danger';
                severity = 'critical';
                message = `Margem restante (${remainingMargin.toFixed(1)}%) abaixo do limite de segurança (${safetyMargin}%)`;
                recommendations.push('Reduzir gasto com anúncios');
                recommendations.push('Aumentar preço do produto');
                recommendations.push('Negociar melhor custo com fornecedor');
                setShowWarning(true);
            } else if (remainingMargin < safetyMargin * 1.5) {
                status = 'warning';
                severity = 'medium';
                message = `Margem restante (${remainingMargin.toFixed(1)}%) próxima do limite de segurança`;
                recommendations.push('Monitorar gastos com anúncios');
                recommendations.push('Considerar ajustar estratégia');
                setShowWarning(true);
            } else {
                status = 'safe';
                severity = 'low';
                message = `Margem segura: ${remainingMargin.toFixed(1)}% restante após anúncios`;
                recommendations.push('Margem adequada para operação');
                recommendations.push('Possível aumentar investimento em ads');
                setShowWarning(false);
            }

            const result = {
                status,
                severity,
                message,
                profitMargin: profitMargin.toFixed(1),
                markupPercentage: markupPercentage.toFixed(1),
                remainingMargin: remainingMargin.toFixed(1),
                safetyMargin: safetyMargin.toFixed(1),
                recommendations,
                maxSafeMarkup: Math.max(0, profitMargin - safetyMargin).toFixed(1)
            };

            setValidationResult(result);
            
            if (onValidation) {
                onValidation(result);
            }

            // Send to alerts service if dangerous
            if (status === 'danger') {
                const token = localStorage.getItem('access_token');
                if (token) {
                    await axios.post('http://localhost:8019/check-metrics', 
                        [{
                            user_id: 'current_user',
                            metric: 'markup_margin',
                            value: remainingMargin,
                            product_id: 'current_product'
                        }],
                        { headers: { Authorization: `Bearer ${token}` } }
                    );
                }
            }

        } catch (error) {
            console.error('Erro ao validar markup:', error);
            setValidationResult({
                status: 'error',
                severity: 'high',
                message: 'Erro ao validar margem de segurança',
                recommendations: ['Verificar dados do produto']
            });
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'safe': return 'text-green-600 bg-green-100 border-green-300';
            case 'warning': return 'text-yellow-600 bg-yellow-100 border-yellow-300';
            case 'danger': return 'text-red-600 bg-red-100 border-red-300';
            case 'error': return 'text-gray-600 bg-gray-100 border-gray-300';
            default: return 'text-gray-600 bg-gray-100 border-gray-300';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'safe': return '✅';
            case 'warning': return '⚠️';
            case 'danger': return '🚨';
            case 'error': return '❌';
            default: return '❓';
        }
    };

    return (
        <div className="space-y-4">
            {/* Safety Margin Configuration */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-lg p-6"
            >
                <h3 className="text-lg font-semibold mb-4">🛡️ Configuração de Margem de Segurança</h3>
                <div className="flex items-center space-x-4">
                    <label className="text-sm font-medium">Margem mínima de segurança:</label>
                    <input
                        type="number"
                        value={safetyMargin}
                        onChange={(e) => setSafetyMargin(parseFloat(e.target.value) || 0)}
                        className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center"
                        min="0"
                        max="50"
                        step="0.5"
                    />
                    <span className="text-sm text-gray-600">%</span>
                    <div className="text-xs text-gray-500">
                        Margem mínima que deve sobrar após gastos com anúncios
                    </div>
                </div>
            </motion.div>

            {/* Validation Result */}
            <AnimatePresence>
                {validationResult && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className={`rounded-lg p-6 border-2 ${getStatusColor(validationResult.status)}`}
                    >
                        <div className="flex items-start space-x-4">
                            <div className="text-3xl">
                                {getStatusIcon(validationResult.status)}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="text-lg font-semibold">
                                        Validação de Margem de Segurança
                                    </h4>
                                    {loading && (
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current"></div>
                                    )}
                                </div>
                                
                                <p className="text-sm font-medium mb-4">
                                    {validationResult.message}
                                </p>

                                {/* Metrics Display */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                                    <div className="text-center">
                                        <div className="text-2xl font-bold">
                                            {validationResult.profitMargin}%
                                        </div>
                                        <div className="text-xs opacity-75">Margem Total</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold">
                                            {validationResult.markupPercentage}%
                                        </div>
                                        <div className="text-xs opacity-75">Markup Atual</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold">
                                            {validationResult.remainingMargin}%
                                        </div>
                                        <div className="text-xs opacity-75">Margem Restante</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold">
                                            {validationResult.maxSafeMarkup}%
                                        </div>
                                        <div className="text-xs opacity-75">Markup Máximo Seguro</div>
                                    </div>
                                </div>

                                {/* Visual Progress Bar */}
                                <div className="mb-4">
                                    <div className="flex justify-between text-xs mb-1">
                                        <span>Uso da Margem</span>
                                        <span>{((parseFloat(validationResult.markupPercentage) / parseFloat(validationResult.profitMargin)) * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-3">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ 
                                                width: `${Math.min(100, (parseFloat(validationResult.markupPercentage) / parseFloat(validationResult.profitMargin)) * 100)}%` 
                                            }}
                                            transition={{ duration: 1, ease: "easeOut" }}
                                            className={`h-3 rounded-full ${
                                                validationResult.status === 'safe' ? 'bg-green-500' :
                                                validationResult.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                                            }`}
                                        />
                                    </div>
                                    <div className="flex justify-between text-xs mt-1 text-gray-500">
                                        <span>0%</span>
                                        <span className="text-red-500">Limite: {safetyMargin}%</span>
                                        <span>100%</span>
                                    </div>
                                </div>

                                {/* Recommendations */}
                                {validationResult.recommendations && validationResult.recommendations.length > 0 && (
                                    <div>
                                        <h5 className="font-semibold mb-2">Recomendações:</h5>
                                        <ul className="space-y-1">
                                            {validationResult.recommendations.map((recommendation, index) => (
                                                <motion.li
                                                    key={index}
                                                    initial={{ opacity: 0, x: -10 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: index * 0.1 }}
                                                    className="flex items-center space-x-2 text-sm"
                                                >
                                                    <span className="text-lg">•</span>
                                                    <span>{recommendation}</span>
                                                </motion.li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Warning Modal */}
            <AnimatePresence>
                {showWarning && validationResult?.status === 'danger' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                        onClick={() => setShowWarning(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="text-center">
                                <div className="text-6xl mb-4">🚨</div>
                                <h3 className="text-xl font-bold text-red-600 mb-2">
                                    Alerta de Margem de Segurança!
                                </h3>
                                <p className="text-gray-700 mb-6">
                                    A margem restante está abaixo do limite de segurança. 
                                    Continuar pode resultar em prejuízo.
                                </p>
                                
                                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                                    <div className="text-sm text-red-700">
                                        <strong>Margem Restante:</strong> {validationResult.remainingMargin}%<br/>
                                        <strong>Limite de Segurança:</strong> {validationResult.safetyMargin}%<br/>
                                        <strong>Deficit:</strong> {(parseFloat(validationResult.safetyMargin) - parseFloat(validationResult.remainingMargin)).toFixed(1)}%
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <motion.button
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => setShowWarning(false)}
                                        className="w-full bg-red-500 text-white py-3 rounded-lg font-medium hover:bg-red-600"
                                    >
                                        🛑 Entendi, vou ajustar
                                    </motion.button>
                                    
                                    <motion.button
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => setShowWarning(false)}
                                        className="w-full bg-gray-300 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-400"
                                    >
                                        Continuar mesmo assim
                                    </motion.button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Quick Actions */}
            {validationResult && validationResult.status !== 'safe' && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-blue-50 rounded-lg p-6 border border-blue-200"
                >
                    <h4 className="font-semibold text-blue-900 mb-3">⚡ Ações Rápidas</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="bg-white border border-blue-300 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-50"
                        >
                            📉 Reduzir Markup para {validationResult.maxSafeMarkup}%
                        </motion.button>
                        
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="bg-white border border-blue-300 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-50"
                        >
                            💰 Sugerir Novo Preço
                        </motion.button>
                        
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="bg-white border border-blue-300 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-50"
                        >
                            🔔 Criar Alerta Automático
                        </motion.button>
                    </div>
                </motion.div>
            )}
        </div>
    );
};

export default MarkupSafetyValidator;