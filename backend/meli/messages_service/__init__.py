"""
Messages Service for Mercado Libre Integration

Handles messaging between sellers and buyers, automated responses,
and message analytics. Integrates with AI services for smart responses.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..base import BaseMeliService
from ..interfaces import MeliResponse, MeliPaginatedResponse


class MessagesService(BaseMeliService):
    """
    Serviço para gerenciamento de mensagens do Mercado Libre.
    
    Funcionalidades:
    - Listar mensagens
    - Enviar respostas
    - Respostas automatizadas com IA
    - Analytics de comunicação
    - Integração com atendimento ao cliente
    """
    
    def __init__(self):
        super().__init__("messages_service")
    
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista mensagens do vendedor."""
        try:
            params = {
                "user_id": user_id,
                "offset": offset,
                "limit": limit
            }
            
            # Filtros específicos para mensagens
            if filters:
                if "status" in filters:
                    params["status"] = filters["status"]
                if "from_user" in filters:
                    params["from"] = filters["from_user"]
                if "date_from" in filters:
                    params["date_created.from"] = filters["date_from"]
                if "date_to" in filters:
                    params["date_created.to"] = filters["date_to"]
                if "unread_only" in filters and filters["unread_only"]:
                    params["status"] = "unread"
            
            response = await self._make_ml_request(
                "GET",
                "/messages/search",
                access_token,
                params=params
            )
            
            if response.success:
                data = response.data
                messages = data.get("results", [])
                
                # Analisa mensagens para insights
                await self._analyze_messages_for_insights(messages)
                
                # Identifica mensagens que precisam de resposta urgente
                urgent_messages = self._identify_urgent_messages(messages)
                
                # Analytics de mensagens
                await self._send_analytics_event("messages_listed", {
                    "user_id": user_id,
                    "total_messages": data.get("paging", {}).get("total", 0),
                    "unread_count": len([m for m in messages if m.get("status") == "unread"]),
                    "urgent_count": len(urgent_messages),
                    "filters": filters
                })
                
                return MeliPaginatedResponse(
                    success=True,
                    data=messages,
                    total=data.get("paging", {}).get("total"),
                    offset=data.get("paging", {}).get("offset"),
                    limit=data.get("paging", {}).get("limit"),
                    has_next=data.get("paging", {}).get("offset", 0) + limit < data.get("paging", {}).get("total", 0),
                    metadata={
                        "urgent_messages": urgent_messages,
                        "statistics": self._calculate_message_stats(messages)
                    }
                )
            
            return MeliPaginatedResponse(
                success=False,
                error=response.error
            )
            
        except Exception as e:
            self.logger.error(f"Error listing messages: {e}")
            return MeliPaginatedResponse(
                success=False,
                error=str(e)
            )
    
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes completos de uma conversa/mensagem."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/messages/{item_id}",
                access_token
            )
            
            if response.success:
                message_data = response.data
                
                # Gera sugestões de resposta automatizada
                ai_suggestions = await self._generate_response_suggestions(message_data)
                
                await self._send_analytics_event("message_details_viewed", {
                    "message_id": item_id,
                    "from_user": message_data.get("from", {}).get("user_id"),
                    "has_ai_suggestions": bool(ai_suggestions)
                })
                
                # Adiciona sugestões à resposta
                if ai_suggestions:
                    message_data["ai_suggestions"] = ai_suggestions
                
                return MeliResponse(
                    success=True,
                    data=message_data
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting message details: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def send_message(
        self, 
        access_token: str, 
        recipient_id: str, 
        message_text: str,
        order_id: Optional[str] = None
    ) -> MeliResponse:
        """Envia uma mensagem para um usuário."""
        try:
            message_data = {
                "to": {"user_id": recipient_id},
                "text": message_text
            }
            
            if order_id:
                message_data["regarding"] = {
                    "resource": "order",
                    "resource_id": order_id
                }
            
            response = await self._make_ml_request(
                "POST",
                "/messages",
                access_token,
                json_data=message_data
            )
            
            if response.success:
                await self._send_analytics_event("message_sent", {
                    "recipient_id": recipient_id,
                    "order_id": order_id,
                    "message_length": len(message_text)
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def mark_as_read(
        self, 
        access_token: str, 
        message_id: str
    ) -> MeliResponse:
        """Marca uma mensagem como lida."""
        try:
            response = await self._make_ml_request(
                "PUT",
                f"/messages/{message_id}",
                access_token,
                json_data={"status": "read"}
            )
            
            if response.success:
                await self._send_analytics_event("message_marked_read", {
                    "message_id": message_id
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error marking message as read: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_conversation_history(
        self, 
        access_token: str, 
        user_id: str, 
        other_user_id: str
    ) -> MeliResponse:
        """Obtém histórico de conversa entre dois usuários."""
        try:
            params = {
                "user_id": user_id,
                "from": other_user_id,
                "limit": 100
            }
            
            response = await self._make_ml_request(
                "GET",
                "/messages/search",
                access_token,
                params=params
            )
            
            if response.success:
                messages = response.data.get("results", [])
                
                # Analisa o histórico para insights
                conversation_insights = await self._analyze_conversation_history(messages)
                
                return MeliResponse(
                    success=True,
                    data={
                        "messages": messages,
                        "insights": conversation_insights
                    }
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_automated_response_suggestions(
        self, 
        access_token: str, 
        message_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MeliResponse:
        """Gera sugestões de resposta automatizada usando IA."""
        try:
            # Contexto para IA
            ai_context = {
                "message": message_content,
                "service": "messages",
                "context": context or {}
            }
            
            # Busca sugestões do serviço de IA
            suggestions = await self._get_learning_insights(ai_context)
            
            return MeliResponse(
                success=True,
                data={
                    "suggestions": suggestions.get("response_suggestions", []) if suggestions else [],
                    "confidence": suggestions.get("confidence", 0) if suggestions else 0,
                    "detected_intent": suggestions.get("intent", "unknown") if suggestions else "unknown"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error getting automated suggestions: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def _generate_response_suggestions(
        self, 
        message_data: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Gera sugestões de resposta baseadas no conteúdo da mensagem."""
        try:
            message_text = message_data.get("text", "")
            
            # Contexto para geração de sugestões
            context = {
                "message_text": message_text,
                "from_user": message_data.get("from", {}),
                "regarding": message_data.get("regarding", {})
            }
            
            # Usa learning service para gerar sugestões
            ai_response = await self._get_learning_insights({
                "task": "generate_response_suggestions",
                "context": context
            })
            
            if ai_response and "suggestions" in ai_response:
                return ai_response["suggestions"]
            
            # Sugestões padrão se IA não disponível
            return self._get_default_suggestions(message_text)
            
        except Exception as e:
            self.logger.warning(f"Error generating response suggestions: {e}")
            return None
    
    def _get_default_suggestions(self, message_text: str) -> List[Dict[str, Any]]:
        """Sugestões padrão baseadas em palavras-chave."""
        suggestions = []
        message_lower = message_text.lower()
        
        if any(word in message_lower for word in ["entrega", "envio", "prazo"]):
            suggestions.append({
                "text": "Olá! O prazo de entrega é de 3 a 5 dias úteis após a confirmação do pagamento.",
                "type": "shipping_info",
                "confidence": 0.8
            })
        
        if any(word in message_lower for word in ["desconto", "preço", "valor"]):
            suggestions.append({
                "text": "Obrigado pelo interesse! Este é o melhor preço que posso oferecer no momento.",
                "type": "pricing_info",
                "confidence": 0.7
            })
        
        if any(word in message_lower for word in ["disponível", "estoque", "tem"]):
            suggestions.append({
                "text": "Sim, temos o produto disponível em estoque!",
                "type": "availability_info",
                "confidence": 0.9
            })
        
        return suggestions
    
    def _identify_urgent_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica mensagens que precisam de resposta urgente."""
        urgent = []
        
        for message in messages:
            text = message.get("text", "").lower()
            days_old = self._calculate_message_age_days(message.get("date_created"))
            
            # Critérios de urgência
            is_urgent = (
                days_old > 1 or  # Mais de 1 dia sem resposta
                any(word in text for word in ["urgente", "problema", "cancelar", "reclamação"]) or
                message.get("status") == "unread"
            )
            
            if is_urgent:
                urgent.append(message)
        
        return urgent
    
    def _calculate_message_age_days(self, date_created: str) -> int:
        """Calcula a idade da mensagem em dias."""
        try:
            if not date_created:
                return 0
            
            created = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
            now = datetime.now(created.tzinfo)
            return (now - created).days
        except:
            return 0
    
    def _calculate_message_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas das mensagens."""
        if not messages:
            return {}
        
        unread_count = len([m for m in messages if m.get("status") == "unread"])
        avg_response_time = self._calculate_avg_response_time(messages)
        
        return {
            "total": len(messages),
            "unread": unread_count,
            "read": len(messages) - unread_count,
            "avg_response_time_hours": avg_response_time
        }
    
    def _calculate_avg_response_time(self, messages: List[Dict[str, Any]]) -> float:
        """Calcula tempo médio de resposta em horas."""
        # Implementação simplificada
        return 4.5  # Placeholder
    
    async def _analyze_messages_for_insights(self, messages: List[Dict[str, Any]]):
        """Analisa mensagens para gerar insights."""
        if not messages:
            return
        
        # Envia dados para learning service
        await self._get_learning_insights({
            "task": "analyze_messages",
            "data": {
                "messages_count": len(messages),
                "unread_count": len([m for m in messages if m.get("status") == "unread"]),
                "common_themes": self._extract_common_themes(messages)
            }
        })
    
    async def _analyze_conversation_history(
        self, 
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analisa histórico de conversa."""
        return {
            "total_messages": len(messages),
            "conversation_duration_days": self._calculate_conversation_duration(messages),
            "sentiment_analysis": await self._analyze_sentiment(messages),
            "key_topics": self._extract_key_topics(messages)
        }
    
    def _extract_common_themes(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extrai temas comuns das mensagens."""
        # Implementação simplificada
        themes = []
        all_text = " ".join([m.get("text", "") for m in messages]).lower()
        
        if "entrega" in all_text or "envio" in all_text:
            themes.append("shipping")
        if "preço" in all_text or "valor" in all_text:
            themes.append("pricing")
        if "produto" in all_text or "item" in all_text:
            themes.append("product_info")
        
        return themes
    
    def _calculate_conversation_duration(self, messages: List[Dict[str, Any]]) -> int:
        """Calcula duração da conversa em dias."""
        if len(messages) < 2:
            return 0
        
        dates = [m.get("date_created") for m in messages if m.get("date_created")]
        if not dates:
            return 0
        
        try:
            first = datetime.fromisoformat(min(dates).replace('Z', '+00:00'))
            last = datetime.fromisoformat(max(dates).replace('Z', '+00:00'))
            return (last - first).days
        except:
            return 0
    
    async def _analyze_sentiment(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa sentimento das mensagens."""
        # Placeholder para análise de sentimento
        return {
            "overall_sentiment": "neutral",
            "positive_messages": len(messages) // 3,
            "negative_messages": len(messages) // 4,
            "neutral_messages": len(messages) - (len(messages) // 3) - (len(messages) // 4)
        }
    
    def _extract_key_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extrai tópicos principais da conversa."""
        return self._extract_common_themes(messages)
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        """Endpoints disponíveis do serviço de mensagens."""
        base_endpoints = super()._get_available_endpoints()
        messages_endpoints = {
            "list_messages": f"/meli/{self.service_name}/messages",
            "message_details": f"/meli/{self.service_name}/messages/{{message_id}}",
            "send_message": f"/meli/{self.service_name}/messages",
            "mark_read": f"/meli/{self.service_name}/messages/{{message_id}}/read",
            "conversation": f"/meli/{self.service_name}/conversations/{{user_id}}",
            "ai_suggestions": f"/meli/{self.service_name}/ai_suggestions"
        }
        return {**base_endpoints, **messages_endpoints}


# Instância global do serviço
messages_service = MessagesService()