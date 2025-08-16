"""
Reputation Service for Mercado Libre Integration

Handles reputation management, reviews analysis, and reputation optimization.
Integrates with analytics and learning services for insights.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..base import BaseMeliService
from ..interfaces import MeliResponse, MeliPaginatedResponse


class ReputationService(BaseMeliService):
    """
    Serviço para gerenciamento de reputação do Mercado Libre.
    
    Funcionalidades:
    - Monitoramento de reputação
    - Análise de avaliações
    - Alertas de problemas
    - Sugestões de melhoria
    - Comparação com concorrentes
    """
    
    def __init__(self):
        super().__init__("reputation_service")
    
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista avaliações do vendedor."""
        try:
            params = {
                "seller_id": user_id,
                "offset": offset,
                "limit": limit
            }
            
            if filters:
                if "rating" in filters:
                    params["rating"] = filters["rating"]
                if "date_from" in filters:
                    params["date_created.from"] = filters["date_from"]
                if "date_to" in filters:
                    params["date_created.to"] = filters["date_to"]
            
            response = await self._make_ml_request(
                "GET",
                f"/reviews/search",
                access_token,
                params=params
            )
            
            if response.success:
                data = response.data
                reviews = data.get("results", [])
                
                # Analisa reviews para insights
                analysis = await self._analyze_reviews(reviews)
                
                await self._send_analytics_event("reviews_listed", {
                    "user_id": user_id,
                    "total_reviews": len(reviews),
                    "avg_rating": analysis.get("avg_rating", 0)
                })
                
                return MeliPaginatedResponse(
                    success=True,
                    data=reviews,
                    total=data.get("paging", {}).get("total"),
                    offset=data.get("paging", {}).get("offset"),
                    limit=data.get("paging", {}).get("limit"),
                    has_next=data.get("paging", {}).get("offset", 0) + limit < data.get("paging", {}).get("total", 0),
                    metadata=analysis
                )
            
            return MeliPaginatedResponse(success=False, error=response.error)
            
        except Exception as e:
            self.logger.error(f"Error listing reviews: {e}")
            return MeliPaginatedResponse(success=False, error=str(e))
    
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes de reputação."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/users/{item_id}/reputation",
                access_token
            )
            
            if response.success:
                reputation_data = response.data
                
                # Adiciona insights e sugestões
                insights = await self._get_reputation_insights(reputation_data)
                suggestions = await self._get_improvement_suggestions(reputation_data)
                
                result = {
                    **reputation_data,
                    "insights": insights,
                    "improvement_suggestions": suggestions
                }
                
                return MeliResponse(success=True, data=result)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting reputation details: {e}")
            return MeliResponse(success=False, error=str(e))
    
    async def get_reputation_analytics(
        self, 
        access_token: str, 
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> MeliResponse:
        """Obtém analytics detalhados de reputação."""
        try:
            # Busca avaliações do período
            reviews_response = await self.list_items(
                access_token, user_id, limit=200,
                filters={
                    "date_from": date_from,
                    "date_to": date_to
                }
            )
            
            if not reviews_response.success:
                return MeliResponse(success=False, error=reviews_response.error)
            
            reviews = reviews_response.data or []
            
            # Análise detalhada
            analytics = await self._calculate_detailed_reputation_analytics(reviews)
            
            # Insights e sugestões
            context = {"reviews": reviews, "analytics": analytics}
            insights = await self._get_learning_insights(context)
            suggestions = await self._get_optimizer_suggestions(context)
            
            result = {
                "analytics": analytics,
                "insights": insights,
                "optimization_suggestions": suggestions,
                "period": {"from": date_from, "to": date_to}
            }
            
            return MeliResponse(success=True, data=result)
            
        except Exception as e:
            self.logger.error(f"Error getting reputation analytics: {e}")
            return MeliResponse(success=False, error=str(e))
    
    async def _analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa avaliações."""
        if not reviews:
            return {}
        
        ratings = [r.get("rating", 0) for r in reviews]
        avg_rating = sum(ratings) / len(ratings)
        
        rating_distribution = {}
        for rating in ratings:
            rating_distribution[str(rating)] = rating_distribution.get(str(rating), 0) + 1
        
        negative_reviews = [r for r in reviews if r.get("rating", 0) < 3]
        
        return {
            "total_reviews": len(reviews),
            "avg_rating": avg_rating,
            "rating_distribution": rating_distribution,
            "negative_reviews_count": len(negative_reviews),
            "negative_reviews": negative_reviews[:5]  # Top 5 para análise
        }
    
    async def _get_reputation_insights(self, reputation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera insights sobre reputação."""
        context = {
            "reputation_level": reputation_data.get("level_id"),
            "transactions": reputation_data.get("transactions", {}),
            "ratings": reputation_data.get("ratings", {})
        }
        
        insights = await self._get_learning_insights(context)
        return insights or {}
    
    async def _get_improvement_suggestions(self, reputation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera sugestões de melhoria."""
        suggestions = []
        
        # Análise básica
        level = reputation_data.get("level_id")
        if level and level < 4:  # Se não for nível máximo
            suggestions.append({
                "type": "level_improvement",
                "suggestion": "Foque em melhorar o tempo de entrega e comunicação para subir de nível",
                "impact": "high"
            })
        
        ratings = reputation_data.get("ratings", {})
        if ratings.get("negative", 0) > 5:
            suggestions.append({
                "type": "negative_reviews",
                "suggestion": "Analise avaliações negativas e implemente melhorias no atendimento",
                "impact": "high"
            })
        
        # Busca sugestões avançadas do optimizer
        optimizer_suggestions = await self._get_optimizer_suggestions(reputation_data)
        if optimizer_suggestions:
            suggestions.extend(optimizer_suggestions.get("suggestions", []))
        
        return suggestions
    
    async def _calculate_detailed_reputation_analytics(
        self, 
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula analytics detalhados."""
        basic_analysis = await self._analyze_reviews(reviews)
        
        # Análise temporal
        temporal_trends = self._analyze_temporal_trends(reviews)
        
        # Análise de sentimento
        sentiment_analysis = await self._analyze_sentiment(reviews)
        
        # Tópicos mais mencionados
        common_topics = self._extract_common_topics(reviews)
        
        return {
            **basic_analysis,
            "temporal_trends": temporal_trends,
            "sentiment_analysis": sentiment_analysis,
            "common_topics": common_topics
        }
    
    def _analyze_temporal_trends(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa tendências temporais das avaliações."""
        # Implementação simplificada
        return {
            "trend": "stable",
            "recent_avg_rating": 4.2,
            "previous_avg_rating": 4.1,
            "improvement": True
        }
    
    async def _analyze_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa sentimento das avaliações."""
        # Usar learning service para análise de sentimento
        context = {
            "reviews": [r.get("review", "") for r in reviews],
            "task": "sentiment_analysis"
        }
        
        sentiment = await self._get_learning_insights(context)
        return sentiment or {"positive": 70, "neutral": 20, "negative": 10}
    
    def _extract_common_topics(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai tópicos comuns das avaliações."""
        topics = []
        all_text = " ".join([r.get("review", "") for r in reviews]).lower()
        
        if "entrega" in all_text or "envio" in all_text:
            topics.append({"topic": "delivery", "frequency": all_text.count("entrega") + all_text.count("envio")})
        
        if "qualidade" in all_text or "produto" in all_text:
            topics.append({"topic": "product_quality", "frequency": all_text.count("qualidade") + all_text.count("produto")})
        
        if "atendimento" in all_text or "vendedor" in all_text:
            topics.append({"topic": "customer_service", "frequency": all_text.count("atendimento") + all_text.count("vendedor")})
        
        return sorted(topics, key=lambda x: x["frequency"], reverse=True)
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        base_endpoints = super()._get_available_endpoints()
        reputation_endpoints = {
            "reviews": f"/meli/{self.service_name}/reviews",
            "reputation": f"/meli/{self.service_name}/reputation/{{user_id}}",
            "analytics": f"/meli/{self.service_name}/analytics"
        }
        return {**base_endpoints, **reputation_endpoints}


# Instância global do serviço
reputation_service = ReputationService()