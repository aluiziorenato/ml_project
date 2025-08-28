import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Campaign {
  daily_revenue?: number;
  keywords?: string[];
  avg_position?: number;
  [key: string]: any;
}

interface AlternativeAction {
  action: string;
  icon: string;
  description: string;
}

interface CampaignDeactivationDialogProps {
  isOpen: boolean;
  campaign: Campaign | null;
  onConfirm: (reason: string) => void;
  onCancel: () => void;
}

const deactivationReasons = [
  { id: 'poor_performance', label: 'Performance Baixa', icon: '📉' },
  { id: 'budget_exceeded', label: 'Orçamento Excedido', icon: '💸' },
  { id: 'high_acos', label: 'ACOS Muito Alto', icon: '📈' },
  { id: 'strategic_change', label: 'Mudança Estratégica', icon: '🎯' },
  { id: 'seasonal_end', label: 'Fim da Sazonalidade', icon: '📅' },
  { id: 'product_issues', label: 'Problemas no Produto', icon: '📦' },
  { id: 'other', label: 'Outro Motivo', icon: '🤔' }
];

const CampaignDeactivationDialog: React.FC<CampaignDeactivationDialogProps> = ({ isOpen, campaign, onConfirm, onCancel }) => {
  const [reason, setReason] = useState('');
  const [selectedReason, setSelectedReason] = useState('');
  const [showImpactAnalysis, setShowImpactAnalysis] = useState(false);
  const [alternativeActions, setAlternativeActions] = useState<AlternativeAction[]>([]);

  const impactAnalysis = campaign ? {
    estimatedRevenueLoss: (campaign.daily_revenue || 0) * 30,
    affectedKeywords: campaign.keywords?.length || 0,
    currentPosition: campaign.avg_position || 0,
    competitorAdvantage: 'Concorrentes podem ganhar posição',
    recoveryTime: '7-14 dias para recuperar posições'
  } : {};

  const generateAlternatives = (reason: string): AlternativeAction[] => {
    const alternatives: Record<string, AlternativeAction[]> = {
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

  const handleReasonChange = (reasonId: string) => {
    setSelectedReason(reasonId);
    setAlternativeActions(generateAlternatives(reasonId));
    setShowImpactAnalysis(true);
  };

  // ...existing code...

  return (
    <div>
      {/* Renderize o diálogo de desativação conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default CampaignDeactivationDialog;
