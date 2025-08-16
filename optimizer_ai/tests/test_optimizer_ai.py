"""
Unit tests for optimizer_ai module endpoints and functionality
"""
import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
from main import app

class TestOptimizerAIEndpoints:
    """Test all optimizer AI endpoints"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "optimizer_ai"

    def test_optimize_copy_endpoint(self):
        """Test the text optimization endpoint"""
        request_data = {
            "original_text": "Smartphone barato em promoção",
            "target_audience": "young_adults",
            "product_category": "electronics",
            "optimization_goal": "conversions",
            "keywords": ["smartphone", "celular", "android"],
            "segment": "b2c_popular",
            "budget_range": "medium",
            "priority_metrics": ["seo", "readability", "compliance"]
        }
        
        response = self.client.post("/api/optimize-copy", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Check required fields
        assert "optimized_text" in data
        assert "improvements" in data
        assert "seo_score" in data
        assert "readability_score" in data
        assert "sentiment_score" in data
        assert "compliance_score" in data
        assert "estimated_performance_lift" in data
        assert "keywords_included" in data
        assert "suggested_keywords" in data
        assert "segment_adaptations" in data
        assert "ml_confidence" in data
        
        # Check data types and ranges
        assert isinstance(data["optimized_text"], str)
        assert isinstance(data["improvements"], list)
        assert 0 <= data["seo_score"] <= 100
        assert 0 <= data["readability_score"] <= 100
        assert 0 <= data["sentiment_score"] <= 1
        assert 0 <= data["compliance_score"] <= 100
        assert isinstance(data["estimated_performance_lift"], float)
        assert isinstance(data["keywords_included"], list)
        assert isinstance(data["suggested_keywords"], list)
        assert isinstance(data["segment_adaptations"], dict)
        assert 0 <= data["ml_confidence"] <= 1

    def test_ab_test_endpoint(self):
        """Test A/B test creation endpoint"""
        request_data = {
            "variations": [
                "Smartphone Samsung Galaxy - melhor preço",
                "Galaxy Samsung - oferta imperdível",
                "Samsung Galaxy smartphone com desconto"
            ],
            "audience": "young_adults",
            "category": "electronics"
        }
        
        response = self.client.post("/api/ab-test", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "test_id" in data
        assert "recommended_variation" in data
        assert "confidence_score" in data
        assert "expected_results" in data
        
        # Check data types and ranges
        assert data["test_id"].startswith("ABT_")
        assert 0 <= data["recommended_variation"] < len(request_data["variations"])
        assert 0 <= data["confidence_score"] <= 1
        assert isinstance(data["expected_results"], dict)

    def test_ab_test_insufficient_variations(self):
        """Test A/B test with insufficient variations"""
        request_data = {
            "variations": ["Single variation"],
            "audience": "young_adults",
            "category": "electronics"
        }
        
        response = self.client.post("/api/ab-test", json=request_data)
        assert response.status_code == 400
        assert "At least 2 variations required" in response.json()["detail"]

    def test_keywords_suggest_endpoint(self):
        """Test keyword suggestions endpoint"""
        request_data = {
            "product_category": "electronics",
            "product_title": "Smartphone Samsung Galaxy S24",
            "target_audience": "young_adults",
            "competitor_analysis": True,
            "max_suggestions": 10
        }
        
        response = self.client.post("/api/keywords/suggest", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "suggested_keywords" in data
        assert "category_trends" in data
        assert "competitor_keywords" in data
        assert "optimization_opportunities" in data
        
        # Check data structure
        assert isinstance(data["suggested_keywords"], list)
        assert len(data["suggested_keywords"]) <= request_data["max_suggestions"]
        
        # Check keyword structure
        if data["suggested_keywords"]:
            keyword = data["suggested_keywords"][0]
            assert "keyword" in keyword
            assert "score" in keyword
            assert "volume_estimate" in keyword
            assert "competition" in keyword

    def test_segment_optimization_endpoint(self):
        """Test segment optimization endpoint"""
        request_data = {
            "text": "Produto de qualidade com ótimo preço",
            "target_segments": ["b2b", "b2c_premium", "millennial"],
            "product_category": "electronics"
        }
        
        response = self.client.post("/api/segment-optimization", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "optimized_texts" in data
        assert "performance_predictions" in data
        assert "recommendations" in data
        
        # Check that we have data for all requested segments
        for segment in request_data["target_segments"]:
            assert segment in data["optimized_texts"]
            assert segment in data["performance_predictions"]
            assert segment in data["recommendations"]
            
            # Check data types
            assert isinstance(data["optimized_texts"][segment], str)
            assert isinstance(data["performance_predictions"][segment], float)
            assert isinstance(data["recommendations"][segment], list)

    def test_compliance_check_endpoint(self):
        """Test compliance checking endpoint"""
        request_data = {
            "text": "MELHOR DO BRASIL! Produto milagroso que cura tudo! Garantido 100%!",
            "product_category": "health"
        }
        
        response = self.client.post("/api/compliance/check", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "is_compliant" in data
        assert "violations" in data
        assert "compliance_score" in data
        assert "risk_level" in data
        assert "recommendations" in data
        
        # This text should have violations
        assert data["is_compliant"] == False
        assert len(data["violations"]) > 0
        assert data["risk_level"] in ["low", "medium", "high"]
        
        # Check violation structure
        if data["violations"]:
            violation = data["violations"][0]
            assert "type" in violation
            assert "description" in violation
            assert "suggestion" in violation

    def test_compliance_check_clean_text(self):
        """Test compliance check with clean text"""
        request_data = {
            "text": "Smartphone Samsung Galaxy com boa qualidade e preço justo",
            "product_category": "electronics"
        }
        
        response = self.client.post("/api/compliance/check", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        # Clean text should have fewer violations
        assert data["compliance_score"] >= 70

    def test_auto_test_endpoint(self):
        """Test auto testing endpoint"""
        request_data = {
            "optimized_text": "Smartphone Samsung Galaxy - melhor escolha para jovens",
            "original_text": "Smartphone Samsung usado",
            "product_category": "electronics",
            "target_audience": "young_adults",
            "budget": 1000.0
        }
        
        response = self.client.post("/api/auto-test", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "test_id" in data
        assert "original_performance" in data
        assert "optimized_performance" in data
        assert "improvement_metrics" in data
        assert "test_status" in data
        assert "recommendations" in data
        
        # Check test ID format
        assert data["test_id"].startswith("AT_")
        
        # Check status
        assert data["test_status"] in ["completed", "failed"]

class TestOptimizerAIFunctions:
    """Test optimizer AI utility functions"""
    
    def setup_method(self):
        """Setup for function tests"""
        # Import functions from main module
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
        from main import (
            calculate_advanced_seo_score,
            calculate_sentiment_score,
            check_compliance,
            optimize_for_segment,
            suggest_keywords_ai,
            apply_optimizations
        )
        self.calculate_advanced_seo_score = calculate_advanced_seo_score
        self.calculate_sentiment_score = calculate_sentiment_score
        self.check_compliance = check_compliance
        self.optimize_for_segment = optimize_for_segment
        self.suggest_keywords_ai = suggest_keywords_ai
        self.apply_optimizations = apply_optimizations

    def test_calculate_advanced_seo_score(self):
        """Test SEO score calculation"""
        text = "Smartphone Samsung Galaxy com excelente qualidade e preço acessível"
        keywords = ["smartphone", "samsung", "galaxy"]
        
        score = self.calculate_advanced_seo_score(text, keywords)
        assert 0 <= score <= 100
        assert isinstance(score, int)

    def test_calculate_sentiment_score(self):
        """Test sentiment score calculation"""
        positive_text = "Produto excelente e fantástico com qualidade superior"
        negative_text = "Produto ruim e péssimo com muitos defeitos"
        neutral_text = "Produto disponível para compra"
        
        positive_score = self.calculate_sentiment_score(positive_text)
        negative_score = self.calculate_sentiment_score(negative_text)
        neutral_score = self.calculate_sentiment_score(neutral_text)
        
        assert 0 <= positive_score <= 1
        assert 0 <= negative_score <= 1
        assert 0 <= neutral_score <= 1
        
        # Positive text should have higher sentiment score
        assert positive_score > negative_score

    def test_check_compliance(self):
        """Test compliance checking"""
        compliant_text = "Smartphone com boa qualidade"
        non_compliant_text = "MELHOR DO BRASIL produto milagroso"
        
        compliant_result = self.check_compliance(compliant_text, "electronics")
        non_compliant_result = self.check_compliance(non_compliant_text, "electronics")
        
        assert compliant_result.compliance_score > non_compliant_result.compliance_score
        assert len(non_compliant_result.violations) > 0

    def test_optimize_for_segment(self):
        """Test segment optimization"""
        text = "Produto de qualidade"
        segment = "b2b"
        keywords = ["profissional", "eficiência"]
        
        optimized = self.optimize_for_segment(text, segment, keywords)
        assert isinstance(optimized, str)
        assert len(optimized) >= len(text)  # Should add content

    @pytest.mark.asyncio
    async def test_suggest_keywords_ai(self):
        """Test AI keyword suggestions"""
        keywords = await self.suggest_keywords_ai("electronics", "Smartphone Samsung", "young_adults")
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        if keywords:
            keyword = keywords[0]
            assert "keyword" in keyword
            assert "score" in keyword
            assert "volume_estimate" in keyword
            assert "competition" in keyword

    def test_apply_optimizations(self):
        """Test text optimizations"""
        text = "Smartphone usado"
        audience = "young_adults"
        category = "electronics"
        goal = "conversions"
        keywords = ["smartphone", "moderno"]
        
        optimized = self.apply_optimizations(text, audience, category, goal, keywords)
        assert isinstance(optimized, str)
        assert len(optimized) >= len(text)  # Should add content

if __name__ == "__main__":
    pytest.main([__file__])