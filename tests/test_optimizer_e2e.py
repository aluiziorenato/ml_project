"""
End-to-end tests for optimizer_ai module
Tests complete workflows and real scenarios
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'optimizer_ai', 'app'))
from main import app

class TestOptimizerAIE2E:
    """End-to-end tests for optimizer AI workflows"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_complete_optimization_workflow(self):
        """Test complete text optimization workflow"""
        
        # Step 1: Start with basic text
        original_text = "Vendo smartphone Samsung usado em bom estado"
        
        # Step 2: Optimize the text
        optimization_request = {
            "original_text": original_text,
            "target_audience": "young_adults",
            "product_category": "electronics",
            "optimization_goal": "conversions",
            "keywords": ["smartphone", "samsung", "android", "moderno"],
            "segment": "millennial",
            "budget_range": "medium",
            "priority_metrics": ["seo", "readability", "compliance"]
        }
        
        optimization_response = self.client.post("/api/optimize-copy", json=optimization_request)
        assert optimization_response.status_code == 200
        optimization_result = optimization_response.json()
        
        optimized_text = optimization_result["optimized_text"]
        assert optimized_text != original_text
        assert optimization_result["seo_score"] > 0
        assert optimization_result["compliance_score"] > 0
        
        # Step 3: Check compliance of optimized text
        compliance_request = {
            "text": optimized_text,
            "product_category": "electronics"
        }
        
        compliance_response = self.client.post("/api/compliance/check", json=compliance_request)
        assert compliance_response.status_code == 200
        compliance_result = compliance_response.json()
        
        # Step 4: Get keyword suggestions for further optimization
        keyword_request = {
            "product_category": "electronics",
            "product_title": optimized_text,
            "target_audience": "young_adults",
            "competitor_analysis": True,
            "max_suggestions": 5
        }
        
        keyword_response = self.client.post("/api/keywords/suggest", json=keyword_request)
        assert keyword_response.status_code == 200
        keyword_result = keyword_response.json()
        
        # Step 5: Create segment variations
        segment_request = {
            "text": optimized_text,
            "target_segments": ["b2c_popular", "millennial", "gen_z"],
            "product_category": "electronics"
        }
        
        segment_response = self.client.post("/api/segment-optimization", json=segment_request)
        assert segment_response.status_code == 200
        segment_result = segment_response.json()
        
        # Step 6: Auto-test the optimization
        auto_test_request = {
            "optimized_text": optimized_text,
            "original_text": original_text,
            "product_category": "electronics",
            "target_audience": "young_adults",
            "budget": 1000.0
        }
        
        auto_test_response = self.client.post("/api/auto-test", json=auto_test_request)
        assert auto_test_response.status_code == 200
        auto_test_result = auto_test_response.json()
        
        # Verify the complete workflow produced meaningful results
        assert len(keyword_result["suggested_keywords"]) > 0
        assert len(segment_result["optimized_texts"]) == 3
        assert auto_test_result["test_status"] in ["completed", "failed"]
        
        print("✅ Complete optimization workflow test passed")

    def test_ab_testing_workflow(self):
        """Test A/B testing workflow with multiple variations"""
        
        # Create multiple text variations
        variations = [
            "Smartphone Samsung Galaxy - Oportunidade única!",
            "Samsung Galaxy - Preço especial por tempo limitado",
            "Galaxy Samsung smartphone com desconto exclusivo",
            "Smartphone Samsung - Melhor custo-benefício do mercado"
        ]
        
        # Step 1: Create A/B test
        ab_test_request = {
            "variations": variations,
            "audience": "young_adults",
            "category": "electronics"
        }
        
        ab_test_response = self.client.post("/api/ab-test", json=ab_test_request)
        assert ab_test_response.status_code == 200
        ab_test_result = ab_test_response.json()
        
        recommended_variation = ab_test_result["recommended_variation"]
        assert 0 <= recommended_variation < len(variations)
        
        # Step 2: Get the recommended text and optimize it further
        best_text = variations[recommended_variation]
        
        optimization_request = {
            "original_text": best_text,
            "target_audience": "young_adults",
            "product_category": "electronics",
            "optimization_goal": "clicks",
            "keywords": ["smartphone", "samsung", "galaxy"],
            "segment": "gen_z",
            "budget_range": "medium",
            "priority_metrics": ["seo", "engagement"]
        }
        
        optimization_response = self.client.post("/api/optimize-copy", json=optimization_request)
        assert optimization_response.status_code == 200
        optimization_result = optimization_response.json()
        
        # Step 3: Check compliance of the final optimized text
        compliance_request = {
            "text": optimization_result["optimized_text"],
            "product_category": "electronics"
        }
        
        compliance_response = self.client.post("/api/compliance/check", json=compliance_request)
        assert compliance_response.status_code == 200
        compliance_result = compliance_response.json()
        
        # Verify workflow results
        assert ab_test_result["confidence_score"] > 0
        assert optimization_result["estimated_performance_lift"] >= 0
        assert compliance_result["compliance_score"] >= 0
        
        print("✅ A/B testing workflow test passed")

    def test_multi_segment_campaign_optimization(self):
        """Test optimization for multiple segments in a campaign"""
        
        base_text = "Produto de qualidade premium com tecnologia avançada"
        segments = ["b2b", "b2c_premium", "millennial", "professionals"]
        
        # Step 1: Optimize for all segments
        segment_request = {
            "text": base_text,
            "target_segments": segments,
            "product_category": "electronics"
        }
        
        segment_response = self.client.post("/api/segment-optimization", json=segment_request)
        assert segment_response.status_code == 200
        segment_result = segment_response.json()
        
        # Step 2: Check compliance for each segment variation
        compliance_results = {}
        for segment in segments:
            segment_text = segment_result["optimized_texts"][segment]
            
            compliance_request = {
                "text": segment_text,
                "product_category": "electronics"
            }
            
            compliance_response = self.client.post("/api/compliance/check", json=compliance_request)
            assert compliance_response.status_code == 200
            compliance_results[segment] = compliance_response.json()
        
        # Step 3: Get keyword suggestions for the best performing segment
        best_segment = max(segment_result["performance_predictions"].items(), 
                          key=lambda x: x[1])[0]
        best_text = segment_result["optimized_texts"][best_segment]
        
        keyword_request = {
            "product_category": "electronics",
            "product_title": best_text,
            "target_audience": "professionals",
            "competitor_analysis": True,
            "max_suggestions": 8
        }
        
        keyword_response = self.client.post("/api/keywords/suggest", json=keyword_request)
        assert keyword_response.status_code == 200
        keyword_result = keyword_response.json()
        
        # Step 4: Auto-test the best segment optimization
        auto_test_request = {
            "optimized_text": best_text,
            "original_text": base_text,
            "product_category": "electronics",
            "target_audience": "professionals",
            "budget": 2000.0
        }
        
        auto_test_response = self.client.post("/api/auto-test", json=auto_test_request)
        assert auto_test_response.status_code == 200
        auto_test_result = auto_test_response.json()
        
        # Verify results
        assert len(segment_result["optimized_texts"]) == len(segments)
        for segment in segments:
            assert segment in compliance_results
            assert compliance_results[segment]["compliance_score"] >= 0
        
        assert len(keyword_result["suggested_keywords"]) > 0
        assert auto_test_result["test_status"] in ["completed", "failed"]
        
        print("✅ Multi-segment campaign optimization test passed")

    def test_compliance_edge_cases(self):
        """Test compliance checking with various edge cases"""
        
        test_cases = [
            {
                "text": "PRODUTO INCRÍVEL E ÚNICO NO MERCADO!!!",
                "category": "electronics",
                "expected_violations": True
            },
            {
                "text": "Smartphone Samsung com garantia do fabricante e voltagem 110/220V",
                "category": "electronics", 
                "expected_violations": False
            },
            {
                "text": "Remédio milagroso que cura tudo",
                "category": "health",
                "expected_violations": True
            },
            {
                "text": "Suplemento alimentar - consulte um médico antes do uso",
                "category": "health",
                "expected_violations": False
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            compliance_request = {
                "text": test_case["text"],
                "product_category": test_case["category"]
            }
            
            compliance_response = self.client.post("/api/compliance/check", json=compliance_request)
            assert compliance_response.status_code == 200
            compliance_result = compliance_response.json()
            
            if test_case["expected_violations"]:
                assert len(compliance_result["violations"]) > 0
                assert compliance_result["compliance_score"] < 100
            else:
                # Clean text might still have minor violations, so we check for higher score
                assert compliance_result["compliance_score"] >= 70
        
        print("✅ Compliance edge cases test passed")

if __name__ == "__main__":
    pytest.main([__file__])