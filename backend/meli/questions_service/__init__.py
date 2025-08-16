"""
Questions Service for Mercado Libre Integration

Handles Q&A between sellers and buyers, automated answers with AI,
and question analytics. Integrates with knowledge base and learning services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..base import BaseMeliService
from ..interfaces import MeliResponse, MeliPaginatedResponse


class QuestionsService(BaseMeliService):
    """
    Serviço para gerenciamento de perguntas e respostas do Mercado Libre.
    
    Funcionalidades:
    - Listar perguntas
    - Responder perguntas
    - Respostas automatizadas com IA
    - Analytics de Q&A
    - Base de conhecimento
    """
    
    def __init__(self):
        super().__init__("questions_service")
    
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista perguntas do vendedor."""
        try:
            params = {
                "seller_id": user_id,
                "offset": offset,
                "limit": limit
            }
            
            # Filtros específicos para perguntas
            if filters:
                if "status" in filters:
                    params["status"] = filters["status"]
                if "item_id" in filters:
                    params["item"] = filters["item_id"]
                if "date_from" in filters:
                    params["date_created.from"] = filters["date_from"]
                if "date_to" in filters:
                    params["date_created.to"] = filters["date_to"]
                if "unanswered_only" in filters and filters["unanswered_only"]:
                    params["status"] = "UNANSWERED"
            
            response = await self._make_ml_request(
                "GET",
                "/questions/search",
                access_token,
                params=params
            )
            
            if response.success:
                data = response.data
                questions = data.get("results", [])
                
                # Identifica perguntas urgentes ou similares
                urgent_questions = self._identify_urgent_questions(questions)
                similar_questions = await self._find_similar_questions(questions)
                
                # Gera sugestões de resposta automática
                for question in questions:
                    if question.get("status") == "UNANSWERED":
                        ai_suggestion = await self._generate_answer_suggestion(question)
                        if ai_suggestion:
                            question["ai_suggestion"] = ai_suggestion
                
                # Analytics de perguntas
                await self._send_analytics_event("questions_listed", {
                    "user_id": user_id,
                    "total_questions": data.get("paging", {}).get("total", 0),
                    "unanswered_count": len([q for q in questions if q.get("status") == "UNANSWERED"]),
                    "urgent_count": len(urgent_questions),
                    "filters": filters
                })
                
                return MeliPaginatedResponse(
                    success=True,
                    data=questions,
                    total=data.get("paging", {}).get("total"),
                    offset=data.get("paging", {}).get("offset"),
                    limit=data.get("paging", {}).get("limit"),
                    has_next=data.get("paging", {}).get("offset", 0) + limit < data.get("paging", {}).get("total", 0),
                    metadata={
                        "urgent_questions": urgent_questions,
                        "similar_questions": similar_questions,
                        "statistics": self._calculate_question_stats(questions)
                    }
                )
            
            return MeliPaginatedResponse(
                success=False,
                error=response.error
            )
            
        except Exception as e:
            self.logger.error(f"Error listing questions: {e}")
            return MeliPaginatedResponse(
                success=False,
                error=str(e)
            )
    
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes completos de uma pergunta."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/questions/{item_id}",
                access_token
            )
            
            if response.success:
                question_data = response.data
                
                # Gera sugestão de resposta se não respondida
                if question_data.get("status") == "UNANSWERED":
                    ai_suggestion = await self._generate_answer_suggestion(question_data)
                    if ai_suggestion:
                        question_data["ai_suggestion"] = ai_suggestion
                
                # Busca perguntas similares
                similar = await self._find_similar_questions([question_data])
                if similar:
                    question_data["similar_questions"] = similar
                
                await self._send_analytics_event("question_details_viewed", {
                    "question_id": item_id,
                    "item_id": question_data.get("item_id"),
                    "status": question_data.get("status")
                })
                
                return MeliResponse(
                    success=True,
                    data=question_data
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting question details: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def answer_question(
        self, 
        access_token: str, 
        question_id: str, 
        answer_text: str
    ) -> MeliResponse:
        """Responde uma pergunta."""
        try:
            response = await self._make_ml_request(
                "POST",
                f"/answers",
                access_token,
                json_data={
                    "question_id": question_id,
                    "text": answer_text
                }
            )
            
            if response.success:
                # Salva resposta na base de conhecimento
                await self._save_to_knowledge_base(question_id, answer_text)
                
                await self._send_analytics_event("question_answered", {
                    "question_id": question_id,
                    "answer_length": len(answer_text)
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error answering question: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_questions_by_item(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém todas as perguntas de um item específico."""
        try:
            params = {"item": item_id}
            
            response = await self._make_ml_request(
                "GET",
                "/questions/search",
                access_token,
                params=params
            )
            
            if response.success:
                questions = response.data.get("results", [])
                
                # Analisa padrões nas perguntas do item
                insights = await self._analyze_item_questions(item_id, questions)
                
                return MeliResponse(
                    success=True,
                    data={
                        "questions": questions,
                        "insights": insights,
                        "statistics": self._calculate_question_stats(questions)
                    }
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting questions by item: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_automated_answer_suggestions(
        self, 
        access_token: str, 
        question_text: str,
        item_context: Optional[Dict[str, Any]] = None
    ) -> MeliResponse:
        """Gera sugestões de resposta automatizada."""
        try:
            # Busca na base de conhecimento
            knowledge_matches = await self._search_knowledge_base(question_text)
            
            # Gera sugestões com IA
            ai_context = {
                "question": question_text,
                "item_context": item_context or {},
                "service": "questions"
            }
            
            ai_suggestions = await self._get_learning_insights(ai_context)
            
            # Combina resultados
            suggestions = []
            
            # Adiciona matches da base de conhecimento
            if knowledge_matches:
                suggestions.extend(knowledge_matches)
            
            # Adiciona sugestões de IA
            if ai_suggestions and "answer_suggestions" in ai_suggestions:
                suggestions.extend(ai_suggestions["answer_suggestions"])
            
            # Sugestões padrão se necessário
            if not suggestions:
                suggestions = self._get_default_answers(question_text)
            
            return MeliResponse(
                success=True,
                data={
                    "suggestions": suggestions,
                    "confidence": ai_suggestions.get("confidence", 0) if ai_suggestions else 0,
                    "source": "hybrid"  # knowledge_base + ai
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error getting automated suggestions: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_questions_analytics(
        self, 
        access_token: str, 
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> MeliResponse:
        """Obtém analytics detalhados das perguntas."""
        try:
            # Busca perguntas do período
            questions_response = await self.list_items(
                access_token,
                user_id,
                offset=0,
                limit=200,
                filters={
                    "date_from": date_from,
                    "date_to": date_to
                }
            )
            
            if not questions_response.success:
                return MeliResponse(
                    success=False,
                    error=questions_response.error
                )
            
            questions = questions_response.data or []
            
            # Calcula métricas detalhadas
            analytics = self._calculate_detailed_analytics(questions)
            
            # Busca insights e otimizações
            context = {
                "questions_count": len(questions),
                "metrics": analytics
            }
            
            optimizer_suggestions = await self._get_optimizer_suggestions(context)
            learning_insights = await self._get_learning_insights(context)
            
            result = {
                "analytics": analytics,
                "optimization_suggestions": optimizer_suggestions,
                "learning_insights": learning_insights,
                "period": {"from": date_from, "to": date_to}
            }
            
            return MeliResponse(
                success=True,
                data=result
            )
            
        except Exception as e:
            self.logger.error(f"Error getting questions analytics: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def _generate_answer_suggestion(
        self, 
        question_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Gera sugestão de resposta para uma pergunta."""
        try:
            question_text = question_data.get("text", "")
            
            # Busca na base de conhecimento primeiro
            knowledge_match = await self._search_knowledge_base(question_text)
            if knowledge_match:
                return {
                    "text": knowledge_match[0]["answer"],
                    "confidence": knowledge_match[0]["confidence"],
                    "source": "knowledge_base"
                }
            
            # Usa IA se não encontrou na base
            ai_context = {
                "question": question_text,
                "item_id": question_data.get("item_id"),
                "task": "generate_answer"
            }
            
            ai_response = await self._get_learning_insights(ai_context)
            
            if ai_response and "suggested_answer" in ai_response:
                return {
                    "text": ai_response["suggested_answer"],
                    "confidence": ai_response.get("confidence", 0.5),
                    "source": "ai"
                }
            
            # Resposta padrão se necessário
            default_answer = self._get_default_answer(question_text)
            if default_answer:
                return {
                    "text": default_answer,
                    "confidence": 0.3,
                    "source": "default"
                }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating answer suggestion: {e}")
            return None
    
    def _get_default_answer(self, question_text: str) -> Optional[str]:
        """Gera resposta padrão baseada em palavras-chave."""
        question_lower = question_text.lower()
        
        if any(word in question_lower for word in ["entrega", "envio", "prazo"]):
            return "O prazo de entrega é de 3 a 5 dias úteis após a confirmação do pagamento."
        
        if any(word in question_lower for word in ["garantia", "defeito"]):
            return "Oferecemos garantia conforme especificado no anúncio. Em caso de defeito, entre em contato conosco."
        
        if any(word in question_lower for word in ["tamanho", "medida", "dimensão"]):
            return "As medidas estão detalhadas na descrição do produto. Qualquer dúvida específica, posso esclarecer."
        
        if any(word in question_lower for word in ["estoque", "disponível", "tem"]):
            return "Sim, temos o produto disponível em estoque para envio imediato!"
        
        return None
    
    def _get_default_answers(self, question_text: str) -> List[Dict[str, Any]]:
        """Retorna lista de respostas padrão."""
        answers = []
        default_answer = self._get_default_answer(question_text)
        
        if default_answer:
            answers.append({
                "text": default_answer,
                "confidence": 0.6,
                "source": "default"
            })
        
        # Sempre adiciona uma resposta genérica
        answers.append({
            "text": "Obrigado pela pergunta! Vou verificar essa informação e responder em breve.",
            "confidence": 0.3,
            "source": "generic"
        })
        
        return answers
    
    async def _search_knowledge_base(self, question_text: str) -> List[Dict[str, Any]]:
        """Busca respostas na base de conhecimento."""
        # Implementação placeholder - integração com base de conhecimento
        # Aqui seria uma busca em banco de dados ou serviço externo
        return []
    
    async def _save_to_knowledge_base(self, question_id: str, answer_text: str):
        """Salva pergunta/resposta na base de conhecimento."""
        # Implementação placeholder
        self.logger.info(f"Saving Q&A to knowledge base: {question_id}")
    
    def _identify_urgent_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica perguntas urgentes."""
        urgent = []
        
        for question in questions:
            text = question.get("text", "").lower()
            days_old = self._calculate_question_age_days(question.get("date_created"))
            
            is_urgent = (
                days_old > 1 or  # Mais de 1 dia sem resposta
                any(word in text for word in ["urgente", "cancelar", "problema", "defeito"]) or
                question.get("status") == "UNANSWERED"
            )
            
            if is_urgent:
                urgent.append(question)
        
        return urgent
    
    async def _find_similar_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Encontra perguntas similares."""
        # Implementação placeholder - usar ML para similarity
        return []
    
    def _calculate_question_age_days(self, date_created: str) -> int:
        """Calcula idade da pergunta em dias."""
        try:
            if not date_created:
                return 0
            
            created = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
            now = datetime.now(created.tzinfo)
            return (now - created).days
        except:
            return 0
    
    def _calculate_question_stats(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas das perguntas."""
        if not questions:
            return {}
        
        answered = len([q for q in questions if q.get("status") == "ANSWERED"])
        unanswered = len(questions) - answered
        avg_response_time = self._calculate_avg_response_time(questions)
        
        return {
            "total": len(questions),
            "answered": answered,
            "unanswered": unanswered,
            "answer_rate": answered / len(questions) if questions else 0,
            "avg_response_time_hours": avg_response_time
        }
    
    def _calculate_detailed_analytics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula analytics detalhados."""
        basic_stats = self._calculate_question_stats(questions)
        
        # Análise de tópicos
        topics = self._analyze_question_topics(questions)
        
        # Distribuição temporal
        temporal_dist = self._analyze_temporal_distribution(questions)
        
        return {
            **basic_stats,
            "topics": topics,
            "temporal_distribution": temporal_dist,
            "most_asked_items": self._get_most_asked_items(questions)
        }
    
    def _analyze_question_topics(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analisa tópicos das perguntas."""
        topics = {}
        
        for question in questions:
            text = question.get("text", "").lower()
            
            if any(word in text for word in ["entrega", "envio", "prazo"]):
                topics["shipping"] = topics.get("shipping", 0) + 1
            if any(word in text for word in ["tamanho", "medida", "cor"]):
                topics["product_specs"] = topics.get("product_specs", 0) + 1
            if any(word in text for word in ["garantia", "defeito"]):
                topics["warranty"] = topics.get("warranty", 0) + 1
            if any(word in text for word in ["preço", "desconto"]):
                topics["pricing"] = topics.get("pricing", 0) + 1
        
        return topics
    
    def _analyze_temporal_distribution(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analisa distribuição temporal das perguntas."""
        # Implementação simplificada
        return {
            "morning": len(questions) // 4,
            "afternoon": len(questions) // 2,
            "evening": len(questions) // 4
        }
    
    def _get_most_asked_items(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica itens com mais perguntas."""
        item_counts = {}
        
        for question in questions:
            item_id = question.get("item_id")
            if item_id:
                item_counts[item_id] = item_counts.get(item_id, 0) + 1
        
        # Ordena por quantidade de perguntas
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"item_id": item_id, "questions_count": count} for item_id, count in sorted_items[:10]]
    
    def _calculate_avg_response_time(self, questions: List[Dict[str, Any]]) -> float:
        """Calcula tempo médio de resposta."""
        # Implementação placeholder
        return 6.0
    
    async def _analyze_item_questions(self, item_id: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa perguntas específicas de um item."""
        return {
            "total_questions": len(questions),
            "common_concerns": self._extract_common_concerns(questions),
            "suggestion": "Consider adding more details to product description to reduce questions"
        }
    
    def _extract_common_concerns(self, questions: List[Dict[str, Any]]) -> List[str]:
        """Extrai preocupações comuns das perguntas."""
        concerns = []
        all_text = " ".join([q.get("text", "") for q in questions]).lower()
        
        if "entrega" in all_text or "envio" in all_text:
            concerns.append("shipping_concerns")
        if "tamanho" in all_text or "medida" in all_text:
            concerns.append("size_concerns")
        if "garantia" in all_text:
            concerns.append("warranty_concerns")
        
        return concerns
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        """Endpoints disponíveis do serviço de perguntas."""
        base_endpoints = super()._get_available_endpoints()
        questions_endpoints = {
            "list_questions": f"/meli/{self.service_name}/questions",
            "question_details": f"/meli/{self.service_name}/questions/{{question_id}}",
            "answer_question": f"/meli/{self.service_name}/answers",
            "questions_by_item": f"/meli/{self.service_name}/items/{{item_id}}/questions",
            "ai_suggestions": f"/meli/{self.service_name}/ai_suggestions",
            "analytics": f"/meli/{self.service_name}/analytics"
        }
        return {**base_endpoints, **questions_endpoints}


# Instância global do serviço
questions_service = QuestionsService()