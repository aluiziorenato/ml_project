"""
Unit tests for Pydantic models in the Optimizer AI service.
Tests model creation, validation, and serialization.
"""
import pytest
from pydantic import ValidationError
from typing import List, Dict, Any
import json

# Import models from the main module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import (
    CopywritingRequest,
    CopywritingResponse,
    SegmentOptimizationRequest,
    SegmentOptimizationResponse,
    KeywordSuggestionRequest,
    KeywordSuggestionResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    AutoTestRequest,
    ABTestRequest,
    ABTestResponse
)


@pytest.mark.models
class TestCopywritingRequest:
    """Test CopywritingRequest model validation and creation."""
    
    def test_create_valid_copywriting_request(self):
        """Test creating a valid copywriting request."""
        data = {
            "original_text": "Produto de qualidade",
            "target_audience": "young_adults",
            "product_category": "electronics",
            "optimization_goal": "clicks",
            "keywords": ["smartphone", "qualidade"],
            "segment": "b2c_premium",
            "budget_range": "high",
            "priority_metrics": ["seo", "readability"]
        }
        
        request = CopywritingRequest(**data)
        
        assert request.original_text == "Produto de qualidade"
        assert request.target_audience == "young_adults"
        assert request.product_category == "electronics"
        assert request.optimization_goal == "clicks"
        assert request.keywords == ["smartphone", "qualidade"]
        assert request.segment == "b2c_premium"
        assert request.budget_range == "high"
        assert request.priority_metrics == ["seo", "readability"]
    
    def test_create_minimal_copywriting_request(self):
        """Test creating a request with only required fields."""
        data = {
            "original_text": "Produto básico",
            "target_audience": "general",
            "product_category": "home",
            "optimization_goal": "conversions"
        }
        
        request = CopywritingRequest(**data)
        
        assert request.original_text == "Produto básico"
        assert request.keywords == []  # Default empty list
        assert request.segment == "general"  # Default value
        assert request.budget_range == "medium"  # Default value
        assert request.priority_metrics == ["seo", "readability"]  # Default value
    
    def test_copywriting_request_serialization(self):
        """Test JSON serialization of copywriting request."""
        data = {
            "original_text": "Teste de serialização",
            "target_audience": "professionals",
            "product_category": "books",
            "optimization_goal": "engagement",
            "keywords": ["educação", "conhecimento"]
        }
        
        request = CopywritingRequest(**data)
        json_str = request.model_dump_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["original_text"] == "Teste de serialização"
        assert parsed["keywords"] == ["educação", "conhecimento"]
    
    def test_copywriting_request_validation_empty_text(self):
        """Test validation with empty original text."""
        data = {
            "original_text": "",
            "target_audience": "families",
            "product_category": "toys",
            "optimization_goal": "clicks"
        }
        
        # Should accept empty string (business logic may handle this)
        request = CopywritingRequest(**data)
        assert request.original_text == ""
    
    def test_copywriting_request_validation_invalid_goal(self):
        """Test that model accepts any string for optimization_goal."""
        data = {
            "original_text": "Produto test",
            "target_audience": "young_adults",
            "product_category": "electronics",
            "optimization_goal": "invalid_goal"  # Not in enum but should accept
        }
        
        request = CopywritingRequest(**data)
        assert request.optimization_goal == "invalid_goal"


@pytest.mark.models
class TestCopywritingResponse:
    """Test CopywritingResponse model validation and creation."""
    
    def test_create_valid_copywriting_response(self):
        """Test creating a valid copywriting response."""
        data = {
            "optimized_text": "Smartphone premium com qualidade superior",
            "improvements": ["Adicionadas palavras-chave", "Melhorada legibilidade"],
            "seo_score": 85,
            "readability_score": 78,
            "sentiment_score": 0.75,
            "compliance_score": 90,
            "estimated_performance_lift": 23.5,
            "keywords_included": ["smartphone", "premium"],
            "suggested_keywords": ["tecnologia", "inovação"],
            "segment_adaptations": {"b2b": "Texto profissional"},
            "ml_confidence": 0.92
        }
        
        response = CopywritingResponse(**data)
        
        assert response.optimized_text == "Smartphone premium com qualidade superior"
        assert len(response.improvements) == 2
        assert response.seo_score == 85
        assert response.sentiment_score == 0.75
        assert response.ml_confidence == 0.92
    
    def test_copywriting_response_score_validation(self):
        """Test that scores are within expected ranges."""
        data = {
            "optimized_text": "Texto otimizado",
            "improvements": ["Melhoria 1"],
            "seo_score": 100,  # Valid upper bound
            "readability_score": 0,  # Valid lower bound
            "sentiment_score": 1.0,  # Valid upper bound for float
            "compliance_score": 50,
            "estimated_performance_lift": 0.0,
            "keywords_included": [],
            "suggested_keywords": [],
            "segment_adaptations": {},
            "ml_confidence": 0.5
        }
        
        response = CopywritingResponse(**data)
        
        assert response.seo_score == 100
        assert response.readability_score == 0
        assert response.sentiment_score == 1.0
        assert response.estimated_performance_lift == 0.0
    
    def test_copywriting_response_serialization(self):
        """Test JSON serialization of copywriting response."""
        data = {
            "optimized_text": "Produto otimizado para teste",
            "improvements": ["Teste de serialização"],
            "seo_score": 75,
            "readability_score": 80,
            "sentiment_score": 0.6,
            "compliance_score": 85,
            "estimated_performance_lift": 15.0,
            "keywords_included": ["teste"],
            "suggested_keywords": ["qualidade"],
            "segment_adaptations": {"test": "value"},
            "ml_confidence": 0.8
        }
        
        response = CopywritingResponse(**data)
        json_str = response.model_dump_json()
        
        parsed = json.loads(json_str)
        assert parsed["optimized_text"] == "Produto otimizado para teste"
        assert parsed["seo_score"] == 75
        assert parsed["sentiment_score"] == 0.6


@pytest.mark.models
class TestKeywordSuggestionModels:
    """Test keyword suggestion related models."""
    
    def test_keyword_suggestion_request(self):
        """Test keyword suggestion request model."""
        data = {
            "product_category": "electronics",
            "product_title": "Smartphone Android",
            "target_audience": "tech_enthusiasts",
            "competitor_analysis": True,
            "max_suggestions": 15
        }
        
        request = KeywordSuggestionRequest(**data)
        
        assert request.product_category == "electronics"
        assert request.product_title == "Smartphone Android"
        assert request.competitor_analysis == True
        assert request.max_suggestions == 15
    
    def test_keyword_suggestion_request_defaults(self):
        """Test keyword suggestion request with default values."""
        data = {
            "product_category": "books",
            "product_title": "Livro de programação",
            "target_audience": "developers"
        }
        
        request = KeywordSuggestionRequest(**data)
        
        assert request.competitor_analysis == True  # Default
        assert request.max_suggestions == 10  # Default
    
    def test_keyword_suggestion_response(self):
        """Test keyword suggestion response model."""
        data = {
            "suggested_keywords": [
                {"keyword": "programação", "score": 0.9, "volume_estimate": 5000, "competition": "medium"}
            ],
            "category_trends": ["python", "javascript"],
            "competitor_keywords": ["coding", "development"],
            "optimization_opportunities": ["Low competition in niche market"]
        }
        
        response = KeywordSuggestionResponse(**data)
        
        assert len(response.suggested_keywords) == 1
        assert response.suggested_keywords[0]["keyword"] == "programação"
        assert response.category_trends == ["python", "javascript"]
        assert len(response.optimization_opportunities) == 1


@pytest.mark.models
class TestComplianceModels:
    """Test compliance checking models."""
    
    def test_compliance_check_request(self):
        """Test compliance check request model."""
        data = {
            "text": "Produto excelente com garantia",
            "product_category": "electronics"
        }
        
        request = ComplianceCheckRequest(**data)
        
        assert request.text == "Produto excelente com garantia"
        assert request.product_category == "electronics"
    
    def test_compliance_check_response_compliant(self):
        """Test compliance check response for compliant text."""
        data = {
            "is_compliant": True,
            "violations": [],
            "compliance_score": 95,
            "risk_level": "low",
            "recommendations": ["Texto em conformidade"]
        }
        
        response = ComplianceCheckResponse(**data)
        
        assert response.is_compliant == True
        assert len(response.violations) == 0
        assert response.compliance_score == 95
        assert response.risk_level == "low"
    
    def test_compliance_check_response_with_violations(self):
        """Test compliance check response with violations."""
        data = {
            "is_compliant": False,
            "violations": [
                {"type": "prohibited_word", "description": "Palavra proibida", "suggestion": "Remover palavra"}
            ],
            "compliance_score": 60,
            "risk_level": "medium",
            "recommendations": ["Corrigir violações"]
        }
        
        response = ComplianceCheckResponse(**data)
        
        assert response.is_compliant == False
        assert len(response.violations) == 1
        assert response.violations[0]["type"] == "prohibited_word"
        assert response.risk_level == "medium"


@pytest.mark.models
class TestSegmentOptimizationModels:
    """Test segment optimization models."""
    
    def test_segment_optimization_request(self):
        """Test segment optimization request model."""
        data = {
            "text": "Produto versátil",
            "target_segments": ["b2b", "b2c_premium", "millennial"],
            "product_category": "software"
        }
        
        request = SegmentOptimizationRequest(**data)
        
        assert request.text == "Produto versátil"
        assert len(request.target_segments) == 3
        assert "b2b" in request.target_segments
        assert request.product_category == "software"
    
    def test_segment_optimization_response(self):
        """Test segment optimization response model."""
        data = {
            "optimized_texts": {
                "b2b": "Solução empresarial eficiente",
                "b2c_premium": "Produto premium exclusivo"
            },
            "performance_predictions": {
                "b2b": 0.85,
                "b2c_premium": 0.78
            },
            "recommendations": {
                "b2b": ["Use tom profissional"],
                "b2c_premium": ["Enfatize exclusividade"]
            }
        }
        
        response = SegmentOptimizationResponse(**data)
        
        assert len(response.optimized_texts) == 2
        assert response.optimized_texts["b2b"] == "Solução empresarial eficiente"
        assert response.performance_predictions["b2b"] == 0.85
        assert len(response.recommendations["b2b"]) == 1


@pytest.mark.models
class TestABTestModels:
    """Test A/B testing models."""
    
    def test_ab_test_request(self):
        """Test A/B test request model."""
        data = {
            "variations": [
                "Produto excelente qualidade",
                "Produto premium superior",
                "Produto inovador moderno"
            ],
            "audience": "young_adults",
            "category": "electronics"
        }
        
        request = ABTestRequest(**data)
        
        assert len(request.variations) == 3
        assert request.audience == "young_adults"
        assert request.category == "electronics"
    
    def test_ab_test_response(self):
        """Test A/B test response model."""
        data = {
            "test_id": "ABT_123456",
            "recommended_variation": 1,
            "confidence_score": 0.92,
            "expected_results": {
                "click_rate_improvement": 25.5,
                "conversion_rate_improvement": 15.2
            }
        }
        
        response = ABTestResponse(**data)
        
        assert response.test_id == "ABT_123456"
        assert response.recommended_variation == 1
        assert response.confidence_score == 0.92
        assert response.expected_results["click_rate_improvement"] == 25.5


@pytest.mark.models
class TestAutoTestModel:
    """Test auto testing model."""
    
    def test_auto_test_request(self):
        """Test auto test request model."""
        data = {
            "optimized_text": "Smartphone premium com tecnologia avançada",
            "original_text": "Smartphone básico",
            "product_category": "electronics",
            "target_audience": "tech_enthusiasts",
            "budget": 1500.00
        }
        
        request = AutoTestRequest(**data)
        
        assert request.optimized_text == "Smartphone premium com tecnologia avançada"
        assert request.original_text == "Smartphone básico"
        assert request.product_category == "electronics"
        assert request.budget == 1500.00


@pytest.mark.errors
@pytest.mark.models
class TestModelValidationErrors:
    """Test model validation error scenarios."""
    
    def test_copywriting_request_missing_required_fields(self):
        """Test creating request with missing required fields."""
        data = {
            "original_text": "Produto test"
            # Missing required fields
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CopywritingRequest(**data)
        
        error = exc_info.value
        assert len(error.errors()) > 0
    
    def test_copywriting_response_invalid_score_types(self):
        """Test response with invalid score types."""
        data = {
            "optimized_text": "Texto otimizado",
            "improvements": ["Melhoria"],
            "seo_score": "invalid",  # Should be int
            "readability_score": 75,
            "sentiment_score": 0.5,
            "compliance_score": 80,
            "estimated_performance_lift": 10.0,
            "keywords_included": [],
            "suggested_keywords": [],
            "segment_adaptations": {},
            "ml_confidence": 0.8
        }
        
        with pytest.raises(ValidationError):
            CopywritingResponse(**data)
    
    def test_keyword_suggestion_request_negative_max_suggestions(self):
        """Test keyword request with negative max suggestions."""
        data = {
            "product_category": "electronics",
            "product_title": "Smartphone",
            "target_audience": "general",
            "max_suggestions": -5  # Invalid negative value
        }
        
        # Model should accept this but business logic might handle it
        request = KeywordSuggestionRequest(**data)
        assert request.max_suggestions == -5
    
    def test_segment_optimization_empty_segments(self):
        """Test segment optimization with empty segments list."""
        data = {
            "text": "Produto test",
            "target_segments": [],  # Empty list
            "product_category": "electronics"
        }
        
        request = SegmentOptimizationRequest(**data)
        assert len(request.target_segments) == 0
    
    def test_ab_test_request_single_variation(self):
        """Test A/B test with insufficient variations."""
        data = {
            "variations": ["Single variation"],  # Need at least 2 for A/B test
            "audience": "general",
            "category": "electronics"
        }
        
        # Model allows this, business logic should validate
        request = ABTestRequest(**data)
        assert len(request.variations) == 1


@pytest.mark.models
class TestModelDefaults:
    """Test model default values."""
    
    def test_copywriting_request_defaults(self):
        """Test all default values in copywriting request."""
        data = {
            "original_text": "Produto",
            "target_audience": "general",
            "product_category": "electronics",
            "optimization_goal": "clicks"
        }
        
        request = CopywritingRequest(**data)
        
        assert request.keywords == []
        assert request.segment == "general"
        assert request.budget_range == "medium"
        assert request.priority_metrics == ["seo", "readability"]
    
    def test_keyword_suggestion_request_defaults(self):
        """Test default values in keyword suggestion request."""
        data = {
            "product_category": "books",
            "product_title": "Programming Book",
            "target_audience": "developers"
        }
        
        request = KeywordSuggestionRequest(**data)
        
        assert request.competitor_analysis == True
        assert request.max_suggestions == 10