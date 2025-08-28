import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

interface MarkupSafetyValidatorProps {
  onValidation: (result: any) => void;
  currentMarkup: number;
  productCost: number;
  productPrice: number;
}

const MarkupSafetyValidator: React.FC<MarkupSafetyValidatorProps> = ({ onValidation, currentMarkup, productCost, productPrice }) => {
  const [validationResult, setValidationResult] = useState<any>(null);
  const [safetyMargin, setSafetyMargin] = useState(10);
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
      const profitMargin = ((productPrice - productCost) / productPrice) * 100;
      const markupPercentage = parseFloat(String(currentMarkup));
      const remainingMargin = profitMargin - markupPercentage;
      let status = 'safe';
      let severity = 'low';
      let message = '';
      let recommendations: string[] = [];
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
        recommendations,
        remainingMargin,
      };
      setValidationResult(result);
      onValidation(result);
    } catch (error) {
      // Trate o erro conforme necessário
    } finally {
      setLoading(false);
    }
  };

  // ...existing code...

  return (
    <div>
      {/* Renderize o validador de markup conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default MarkupSafetyValidator;
