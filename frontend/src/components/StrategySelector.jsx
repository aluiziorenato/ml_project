import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircleIcon, ExclamationTriangleIcon, CogIcon } from '@heroicons/react/24/solid';

const StrategySelector = ({ onStrategySelect, selectedStrategy, isLoading = false }) => {
  const [strategies, setStrategies] = useState([]);
  const [impactPreview, setImpactPreview] = useState(null);

  const defaultStrategies = [
    {
      id: 1,
      name: "Maximizar Lucro",
      description: "Foco na maximização da margem de lucro por venda",
      icon: "💰",
      color: "green",
      acos_min: 10,
      acos_max: 15,
      budget_multiplier: 0.7,
      bid_adjustment: -20,
      margin_threshold: 40,
      advantages: [
        "ACOS conservador (10-15%)",
        "Proteção da margem",
        "Redução automática de lances",
        "Foco em produtos rentáveis"
      ],
      ideal_for: "Períodos de baixa competição, produtos com alta margem"
    },
    {
      id: 2,
      name: "Escalar Vendas",
      description: "Maximizar volume de vendas mantendo rentabilidade",
      icon: "📈",
      color: "blue",
      acos_min: 15,
      acos_max: 25,
      budget_multiplier: 0.85,
      bid_adjustment: 15,
      margin_threshold: 30,
      advantages: [
        "ACOS moderado (15-25%)",
        "Expansão de keywords",
        "Aumento de orçamento automático",
        "Foco em volume"
      ],
      ideal_for: "Crescimento de vendas, lançamento de produtos"
    },
    {
      id: 3,
      name: "Proteger Margem",
      description: "Manter margem mesmo com aumento de competição",
      icon: "🛡️",
      color: "purple",
      acos_min: 8,
      acos_max: 12,
      budget_multiplier: 0.6,
      bid_adjustment: -30,
      margin_threshold: 45,
      advantages: [
        "ACOS muito conservador (8-12%)",
        "Monitoramento de concorrentes",
        "Pausa preventiva de campanhas",
        "Proteção máxima da margem"
      ],
      ideal_for: "Datas especiais, alta competição, produtos exclusivos"
    },
    {
      id: 4,
      name: "Campanhas Agressivas",
      description: "Conquistar market share através de investimento agressivo",
      icon: "⚡",
      color: "red",
      acos_min: 25,
      acos_max: 40,
      budget_multiplier: 1.2,
      bid_adjustment: 50,
      margin_threshold: 20,
      advantages: [
        "ACOS agressivo (25-40%)",
        "Lances máximos",
        "Ativação de todas keywords",
        "Campanhas 24/7"
      ],
      ideal_for: "Conquista de mercado, novos produtos, entrada em nichos"
    }
  ];

  useEffect(() => {
    setStrategies(defaultStrategies);
  }, []);

  const handleStrategyClick = (strategy) => {
    setImpactPreview(calculateImpact(strategy));
    onStrategySelect(strategy);
  };

  const calculateImpact = (strategy) => {
    return {
      acos_change: `${strategy.acos_min}% - ${strategy.acos_max}%`,
      budget_change: `${((strategy.budget_multiplier - 1) * 100).toFixed(1)}%`,
      bid_change: `${strategy.bid_adjustment > 0 ? '+' : ''}${strategy.bid_adjustment}%`,
      margin_protection: `Pausar campanhas se margem < ${strategy.margin_threshold}%`
    };
  };

  const getColorClasses = (color, isSelected = false) => {
    const colors = {
      green: isSelected 
        ? 'border-green-500 bg-green-50 ring-green-500' 
        : 'border-green-200 hover:border-green-300 hover:bg-green-50',
      blue: isSelected 
        ? 'border-blue-500 bg-blue-50 ring-blue-500' 
        : 'border-blue-200 hover:border-blue-300 hover:bg-blue-50',
      purple: isSelected 
        ? 'border-purple-500 bg-purple-50 ring-purple-500' 
        : 'border-purple-200 hover:border-purple-300 hover:bg-purple-50',
      red: isSelected 
        ? 'border-red-500 bg-red-50 ring-red-500' 
        : 'border-red-200 hover:border-red-300 hover:bg-red-50'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Escolha sua Estratégia Global
        </h2>
        <p className="text-gray-600">
          Selecione a estratégia que melhor se adapta aos seus objetivos de negócio
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {strategies.map((strategy) => {
          const isSelected = selectedStrategy?.id === strategy.id;
          
          return (
            <motion.div
              key={strategy.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`relative p-6 rounded-lg border-2 cursor-pointer transition-all duration-200 ${getColorClasses(strategy.color, isSelected)} ${isSelected ? 'ring-2' : ''}`}
              onClick={() => handleStrategyClick(strategy)}
            >
              {isSelected && (
                <div className="absolute -top-2 -right-2">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 bg-white rounded-full" />
                </div>
              )}

              <div className="flex items-start space-x-4">
                <div className="text-3xl">{strategy.icon}</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {strategy.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {strategy.description}
                  </p>

                  <div className="space-y-2">
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Principais Benefícios:
                    </div>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {strategy.advantages.slice(0, 2).map((advantage, index) => (
                        <li key={index} className="flex items-center">
                          <CheckCircleIcon className="h-3 w-3 text-green-500 mr-2 flex-shrink-0" />
                          {advantage}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-3 p-3 bg-gray-50 rounded-md">
                    <div className="text-xs font-medium text-gray-500 mb-1">Ideal para:</div>
                    <div className="text-xs text-gray-600">{strategy.ideal_for}</div>
                  </div>
                </div>
              </div>

              {isLoading && isSelected && (
                <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CogIcon className="h-5 w-5 text-blue-500 animate-spin" />
                    <span className="text-sm font-medium text-gray-600">Aplicando...</span>
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {impactPreview && selectedStrategy && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-blue-500 mr-2" />
            Impacto Estimado da Estratégia
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm font-medium text-gray-500">ACOS Target</div>
              <div className="text-lg font-bold text-blue-600">{impactPreview.acos_change}</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-500">Orçamento</div>
              <div className="text-lg font-bold text-blue-600">{impactPreview.budget_change}</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-500">Lances</div>
              <div className="text-lg font-bold text-blue-600">{impactPreview.bid_change}</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-500">Proteção</div>
              <div className="text-xs font-medium text-blue-600">{impactPreview.margin_protection}</div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default StrategySelector;