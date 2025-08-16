#!/usr/bin/env python3
"""
Demonstration script for Strategic Mode Service functionality
This script showcases the key features of the strategic mode implementation
"""

import json
from datetime import date, datetime

def demo_strategic_modes():
    """Demonstrate the 4 strategic modes"""
    print("🎯 STRATEGIC MODES DEMONSTRATION")
    print("=" * 50)
    
    strategies = [
        {
            "id": 1,
            "name": "💰 Maximizar Lucro",
            "description": "Foco na maximização da margem de lucro por venda",
            "acos_range": "10-15%",
            "budget_multiplier": "0.7x (conservador)",
            "bid_adjustment": "-20% (redução)",
            "margin_threshold": "40%",
            "ideal_for": "Períodos de baixa competição, produtos com alta margem",
            "automation_rules": {
                "bid_adjustment": "Reduzir lances quando ACOS > 15%",
                "campaign_pause": "Pausar campanhas quando ACOS > 20%",
                "budget_reallocation": "Realocação para produtos com ROI > 1.5x"
            }
        },
        {
            "id": 2,
            "name": "📈 Escalar Vendas",
            "description": "Maximizar volume de vendas mantendo rentabilidade",
            "acos_range": "15-25%",
            "budget_multiplier": "0.85x (moderado)",
            "bid_adjustment": "+15% (aumento)",
            "margin_threshold": "30%",
            "ideal_for": "Crescimento de vendas, lançamento de produtos",
            "automation_rules": {
                "bid_adjustment": "Aumentar lances quando conversão > 5%",
                "keyword_expansion": "Expandir keywords com score > 8",
                "budget_increase": "Aumentar orçamento com crescimento > 20%"
            }
        },
        {
            "id": 3,
            "name": "🛡️ Proteger Margem",
            "description": "Manter margem mesmo com aumento de competição",
            "acos_range": "8-12%",
            "budget_multiplier": "0.6x (muito conservador)",
            "bid_adjustment": "-30% (redução significativa)",
            "margin_threshold": "45%",
            "ideal_for": "Datas especiais, alta competição, produtos exclusivos",
            "automation_rules": {
                "competitor_monitoring": "Ajustar lances com mudança de preço > 10%",
                "campaign_pause": "Pausar campanhas quando ACOS > 15%",
                "margin_protection": "Reduzir lances com queda de margem > 25%"
            }
        },
        {
            "id": 4,
            "name": "⚡ Campanhas Agressivas",
            "description": "Conquistar market share através de investimento agressivo",
            "acos_range": "25-40%",
            "budget_multiplier": "1.2x (agressivo)",
            "bid_adjustment": "+50% (aumento significativo)",
            "margin_threshold": "20%",
            "ideal_for": "Conquista de mercado, novos produtos, entrada em nichos",
            "automation_rules": {
                "max_bids": "Lances máximos para posição top 3",
                "keyword_activation": "Ativar todas keywords sugeridas pela IA",
                "continuous_campaigns": "Campanhas 24/7 durante datas especiais"
            }
        }
    ]
    
    for strategy in strategies:
        print(f"\n{strategy['name']}")
        print(f"📝 {strategy['description']}")
        print(f"🎯 ACOS Target: {strategy['acos_range']}")
        print(f"💰 Orçamento: {strategy['budget_multiplier']}")
        print(f"📊 Lances: {strategy['bid_adjustment']}")
        print(f"🛡️ Margem Mínima: {strategy['margin_threshold']}")
        print(f"✨ Ideal para: {strategy['ideal_for']}")
        print("🤖 Automações:")
        for rule, description in strategy['automation_rules'].items():
            print(f"   • {description}")

def demo_special_dates():
    """Demonstrate special dates configuration"""
    print("\n\n📅 SPECIAL DATES DEMONSTRATION")
    print("=" * 50)
    
    special_dates = [
        {
            "name": "🛍️ Black Friday",
            "date": "29/11/2024",
            "duration": "1 dia",
            "budget_multiplier": "3.0x",
            "acos_adjustment": "+10%",
            "priority_categories": ["eletrônicos", "moda", "casa"],
            "peak_hours": ["08:00-12:00", "18:00-23:00"],
            "impact": "Maior data de vendas do ano - máximo investimento"
        },
        {
            "name": "💻 Cyber Monday",
            "date": "02/12/2024",
            "duration": "1 dia",
            "budget_multiplier": "2.5x",
            "acos_adjustment": "+8%",
            "priority_categories": ["eletrônicos", "informática", "games"],
            "peak_hours": ["09:00-11:00", "14:00-16:00", "20:00-22:00"],
            "impact": "Foco em produtos digitais e tecnologia"
        },
        {
            "name": "🎄 Natal",
            "date": "15-24/12/2024",
            "duration": "10 dias",
            "budget_multiplier": "2.0x",
            "acos_adjustment": "+5%",
            "priority_categories": ["presentes", "decoração", "brinquedos"],
            "peak_hours": ["19:00-22:00"],
            "impact": "Período prolongado de alta demanda por presentes"
        },
        {
            "name": "🌸 Dia das Mães",
            "date": "10-12/05/2024",
            "duration": "3 dias",
            "budget_multiplier": "2.2x",
            "acos_adjustment": "+7%",
            "priority_categories": ["presentes", "beleza", "casa", "flores"],
            "peak_hours": ["09:00-11:00", "15:00-17:00"],
            "impact": "Alta demanda por produtos relacionados a mães"
        }
    ]
    
    for event in special_dates:
        print(f"\n{event['name']}")
        print(f"📅 Data: {event['date']} ({event['duration']})")
        print(f"💰 Multiplicador de Orçamento: {event['budget_multiplier']}")
        print(f"🎯 Ajuste de ACOS: {event['acos_adjustment']}")
        print(f"🏷️ Categorias Prioritárias: {', '.join(event['priority_categories'])}")
        print(f"⏰ Horários de Pico: {', '.join(event['peak_hours'])}")
        print(f"📈 Impacto: {event['impact']}")

def demo_automation_workflow():
    """Demonstrate automation workflow"""
    print("\n\n🤖 AUTOMATION WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    workflow_steps = [
        {
            "step": 1,
            "title": "Detecção de Evento",
            "description": "Sistema monitora ACOS, margem, ou atividade de concorrentes",
            "triggers": ["ACOS > threshold", "Margem < limite", "Concorrente ajusta preço"],
            "frequency": "A cada 5 minutos"
        },
        {
            "step": 2,
            "title": "Análise de Estratégia",
            "description": "Verifica qual estratégia está ativa e suas regras",
            "actions": ["Consulta estratégia ativa", "Verifica regras de automação", "Calcula impacto"],
            "frequency": "Imediato"
        },
        {
            "step": 3,
            "title": "Decisão Automática",
            "description": "Aplica regras da estratégia para decidir ação",
            "decisions": ["Ajustar lances", "Pausar campanha", "Realocação de orçamento", "Enviar alerta"],
            "frequency": "< 1 segundo"
        },
        {
            "step": 4,
            "title": "Execução da Ação",
            "description": "Envia comandos para serviços integrados",
            "services": ["ACOS Service (8016)", "Campaign Automation (8014)", "Discount Scheduler (8015)"],
            "frequency": "Imediato"
        },
        {
            "step": 5,
            "title": "Monitoramento e Log",
            "description": "Registra ação executada e monitora resultado",
            "outputs": ["Log da ação", "Métricas de performance", "Alertas se necessário"],
            "frequency": "Contínuo"
        }
    ]
    
    for step in workflow_steps:
        print(f"\n{step['step']}. {step['title']}")
        print(f"📝 {step['description']}")
        if 'triggers' in step:
            print(f"🔥 Triggers: {', '.join(step['triggers'])}")
        if 'actions' in step:
            print(f"⚙️ Ações: {', '.join(step['actions'])}")
        if 'decisions' in step:
            print(f"🧠 Decisões: {', '.join(step['decisions'])}")
        if 'services' in step:
            print(f"🔗 Serviços: {', '.join(step['services'])}")
        print(f"⏱️ Frequência: {step['frequency']}")

def demo_dashboard_kpis():
    """Demonstrate dashboard KPIs"""
    print("\n\n📊 DASHBOARD KPIs DEMONSTRATION")
    print("=" * 50)
    
    sample_kpis = {
        "strategy_info": {
            "active_strategy": "Escalar Vendas",
            "applied_since": "15/01/2024 10:30",
            "status": "Ativa"
        },
        "financial_metrics": {
            "total_spend": "R$ 15.420,50",
            "total_sales": "R$ 89.334,20",
            "profit": "R$ 73.913,70",
            "roi": "4.8x"
        },
        "campaign_metrics": {
            "average_acos": "17.2%",
            "active_campaigns": 23,
            "paused_campaigns": 4,
            "total_clicks": "1.247",
            "conversions": 89
        },
        "alerts_summary": {
            "critical_alerts": 0,
            "warning_alerts": 2,
            "info_alerts": 5,
            "total_unresolved": 7
        },
        "recent_actions": [
            "Redução de lance em 15% - Campanha XYZ",
            "Pausa automática - Campanha ABC (ACOS > 30%)",
            "Aumento de orçamento - Campanha DEF (+20%)",
            "Alerta enviado - Margem baixa produto GHI"
        ]
    }
    
    print("📈 ESTRATÉGIA ATIVA")
    strategy = sample_kpis["strategy_info"]
    print(f"   • Estratégia: {strategy['active_strategy']}")
    print(f"   • Aplicada em: {strategy['applied_since']}")
    print(f"   • Status: {strategy['status']}")
    
    print("\n💰 MÉTRICAS FINANCEIRAS")
    financial = sample_kpis["financial_metrics"]
    for metric, value in financial.items():
        print(f"   • {metric.replace('_', ' ').title()}: {value}")
    
    print("\n📊 MÉTRICAS DE CAMPANHAS")
    campaigns = sample_kpis["campaign_metrics"]
    for metric, value in campaigns.items():
        print(f"   • {metric.replace('_', ' ').title()}: {value}")
    
    print("\n🚨 RESUMO DE ALERTAS")
    alerts = sample_kpis["alerts_summary"]
    for alert_type, count in alerts.items():
        print(f"   • {alert_type.replace('_', ' ').title()}: {count}")
    
    print("\n⚡ AÇÕES RECENTES")
    for action in sample_kpis["recent_actions"]:
        print(f"   • {action}")

def demo_integration_architecture():
    """Demonstrate integration architecture"""
    print("\n\n🏗️ INTEGRATION ARCHITECTURE DEMONSTRATION")
    print("=" * 60)
    
    architecture = {
        "strategic_mode_service": {
            "port": 8017,
            "description": "Orquestrador central de estratégias",
            "responsibilities": [
                "Gerenciar configurações de estratégias",
                "Coordenar aplicação entre serviços",
                "Calcular limites dinâmicos",
                "Processar alertas multicanal",
                "Gerar relatórios comparativos"
            ]
        },
        "integrated_services": [
            {
                "name": "ACOS Service",
                "port": 8016,
                "integration": "Aplica thresholds de ACOS baseados na estratégia",
                "data_flow": "Recebe configurações → Monitora ACOS → Executa ações"
            },
            {
                "name": "Campaign Automation",
                "port": 8014,
                "integration": "Ajusta lances e orçamentos conforme estratégia",
                "data_flow": "Recebe parâmetros → Otimiza campanhas → Reporta resultados"
            },
            {
                "name": "Discount Scheduler",
                "port": 8015,
                "integration": "Programa descontos respeitando limites de margem",
                "data_flow": "Recebe limites → Agenda campanhas → Monitora performance"
            }
        ],
        "ai_modules": [
            "AI Predictive (8005) - Predições e análises",
            "ROI Prediction (8013) - Análise de ROI correlacionado",
            "Dynamic Optimization (8005) - Otimização em tempo real"
        ]
    }
    
    print("🎯 STRATEGIC MODE SERVICE (Coordenador Central)")
    service = architecture["strategic_mode_service"]
    print(f"   📡 Porta: {service['port']}")
    print(f"   📝 {service['description']}")
    print("   🔧 Responsabilidades:")
    for resp in service["responsibilities"]:
        print(f"      • {resp}")
    
    print("\n🔗 SERVIÇOS INTEGRADOS")
    for service in architecture["integrated_services"]:
        print(f"\n   {service['name']} (Porta {service['port']})")
        print(f"   🔄 Integração: {service['integration']}")
        print(f"   📊 Fluxo: {service['data_flow']}")
    
    print("\n🧠 MÓDULOS DE IA")
    for module in architecture["ai_modules"]:
        print(f"   • {module}")

def main():
    """Main demonstration function"""
    print("🚀 STRATEGIC MODE SERVICE - COMPLETE DEMONSTRATION")
    print("=" * 80)
    print("Este é um sistema completo de modo estratégico para campanhas publicitárias")
    print("que integra com IA existente e permite configuração global de estratégias.")
    print("=" * 80)
    
    demo_strategic_modes()
    demo_special_dates() 
    demo_automation_workflow()
    demo_dashboard_kpis()
    demo_integration_architecture()
    
    print("\n\n✨ SUMMARY - FUNCIONALIDADES IMPLEMENTADAS")
    print("=" * 60)
    print("✅ 4 Modos estratégicos pré-configurados")
    print("✅ 7+ Datas especiais com configuração automática")
    print("✅ Sistema de automação inteligente com 5 etapas")
    print("✅ Dashboard completo com KPIs em tempo real")
    print("✅ Integração com 3 serviços existentes")
    print("✅ Backend FastAPI com 25+ endpoints")
    print("✅ Frontend React com 3 componentes principais")
    print("✅ Banco de dados com 6 tabelas especializadas")
    print("✅ Testes automatizados e validação")
    print("✅ Docker e docker-compose configurados")
    print("✅ Documentação técnica completa")
    
    print("\n🎯 PRÓXIMOS PASSOS SUGERIDOS:")
    print("1. Executar: docker-compose up strategic_mode_service")
    print("2. Acessar: http://localhost:3000 (Frontend)")
    print("3. Navegar: Modo Estratégico → Configuração")
    print("4. Testar: Aplicação de estratégias")
    print("5. Monitorar: Dashboard de performance")
    
    print("\n🏆 IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    main()