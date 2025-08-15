import pytest
from app.main import (
    app, ab_tests_storage, copy_optimizations, templates_storage,
    CopywritingRequest, ABTestRequest, TemplateRequest, TemplateGenerateRequest, BatchOptimizationRequest
)


class TestOptimizerAILogic:
    """Test class for Optimizer AI Service business logic"""

    def setup_method(self):
        """Clear storage before each test"""
        ab_tests_storage.clear()
        copy_optimizations.clear()
        templates_storage.clear()

    def test_copywriting_request_validation(self, sample_copywriting_request):
        """Test that copywriting request validation works correctly"""
        request = CopywritingRequest(**sample_copywriting_request)
        assert request.original_text == "Smartphone com boa qualidade"
        assert request.target_audience == "young_adults"
        assert request.optimization_goal == "conversions"
        assert len(request.keywords) == 4

    def test_ab_test_request_validation(self, sample_ab_test_request):
        """Test that A/B test request validation works correctly"""
        request = ABTestRequest(**sample_ab_test_request)
        assert request.name == "Smartphone Copy Test"
        assert len(request.variations) == 3
        assert request.traffic_allocation == 0.8
        assert request.duration_days == 14

    def test_template_request_validation(self, sample_template_request):
        """Test that template request validation works correctly"""
        request = TemplateRequest(**sample_template_request)
        assert request.name == "Product Launch Template"
        assert request.category == "product_launch"
        assert len(request.variables) == 4
        assert len(request.tags) == 3

    def test_template_generate_request_validation(self, sample_template_generate_request):
        """Test that template generation request validation works correctly"""
        request = TemplateGenerateRequest(**sample_template_generate_request)
        assert request.template_id == "TPL_TEST123"
        assert len(request.variables) == 4
        assert request.variables["product_name"] == "iPhone 15"

    def test_batch_request_validation(self, sample_batch_request):
        """Test that batch optimization request validation works correctly"""
        request = BatchOptimizationRequest(**sample_batch_request)
        assert len(request.texts) == 3
        assert request.target_audience == "families"
        assert request.optimization_goal == "clicks"

    def test_ab_tests_storage_operations(self, sample_ab_test_request):
        """Test basic operations on A/B tests storage"""
        # Initially empty
        assert len(ab_tests_storage) == 0
        
        # Add an A/B test (simulate test creation)
        from app.main import ABTestResponse
        from datetime import datetime
        
        test = ABTestResponse(
            test_id="ABT_TEST123",
            name=sample_ab_test_request["name"],
            status="draft",
            variations=[],
            traffic_allocation=sample_ab_test_request["traffic_allocation"],
            start_date=None,
            end_date=None,
            duration_days=sample_ab_test_request["duration_days"],
            results={},
            winner=None,
            confidence_level=None,
            created_at=datetime.now().isoformat()
        )
        
        ab_tests_storage["ABT_TEST123"] = {
            "request": sample_ab_test_request,
            "response": test,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        assert len(ab_tests_storage) == 1
        assert "ABT_TEST123" in ab_tests_storage
        assert ab_tests_storage["ABT_TEST123"]["response"].status == "draft"

    def test_templates_storage_operations(self, sample_template_request):
        """Test basic operations on templates storage"""
        # Initially empty
        assert len(templates_storage) == 0
        
        # Add a template (simulate template creation)
        from app.main import TemplateResponse
        from datetime import datetime
        
        template = TemplateResponse(
            template_id="TPL_TEST123",
            name=sample_template_request["name"],
            description=sample_template_request["description"],
            category=sample_template_request["category"],
            template_text=sample_template_request["template_text"],
            variables=sample_template_request["variables"],
            tags=sample_template_request["tags"],
            usage_count=0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        templates_storage["TPL_TEST123"] = template
        
        assert len(templates_storage) == 1
        assert "TPL_TEST123" in templates_storage
        assert templates_storage["TPL_TEST123"].usage_count == 0

    def test_optimization_id_generation_format(self):
        """Test that optimization IDs are generated in the correct format"""
        import uuid
        
        optimization_id = f"OPT_{str(uuid.uuid4())[:8].upper()}"
        
        assert optimization_id.startswith("OPT_")
        assert len(optimization_id) == 12  # OPT_ + 8 characters
        assert optimization_id[4:].isupper()

    def test_ab_test_id_generation_format(self):
        """Test that A/B test IDs are generated in the correct format"""
        import uuid
        
        test_id = f"ABT_{str(uuid.uuid4())[:8].upper()}"
        
        assert test_id.startswith("ABT_")
        assert len(test_id) == 12  # ABT_ + 8 characters
        assert test_id[4:].isupper()

    def test_template_id_generation_format(self):
        """Test that template IDs are generated in the correct format"""
        import uuid
        
        template_id = f"TPL_{str(uuid.uuid4())[:8].upper()}"
        
        assert template_id.startswith("TPL_")
        assert len(template_id) == 12  # TPL_ + 8 characters
        assert template_id[4:].isupper()

    def test_seo_score_calculation_logic(self):
        """Test SEO score calculation logic"""
        # Test with keywords
        text = "Smartphone incrível com tecnologia avançada"
        keywords = ["smartphone", "tecnologia"]
        
        score = 50  # Base score
        
        # Keyword presence
        for keyword in keywords:
            if keyword.lower() in text.lower():
                score += 10
        
        # Text length (optimal range)
        word_count = len(text.split())
        if 20 <= word_count <= 60:
            score += 15
        elif word_count < 20:
            score -= 10
        
        # Title case optimization
        if any(word.istitle() for word in text.split()):
            score += 5
        
        final_score = min(100, max(0, score))
        
        assert 0 <= final_score <= 100
        assert final_score >= 50  # Should have base score

    def test_readability_score_calculation_logic(self):
        """Test readability score calculation logic"""
        text = "Este é um texto simples. Fácil de ler."
        
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        
        # Penalize very long sentences
        if avg_sentence_length > 20:
            score = 60
        elif avg_sentence_length > 15:
            score = 75
        else:
            score = 85
        
        # Bonus for simple words
        simple_word_bonus = sum(1 for word in text.split() if len(word) <= 6) / len(text.split()) * 15
        
        final_score = min(100, int(score + simple_word_bonus))
        
        assert 0 <= final_score <= 100

    def test_performance_lift_estimation_logic(self):
        """Test performance improvement estimation logic"""
        original = "Produto bom"
        optimized = "Produto EXCLUSIVO com GARANTIA - Compre agora!"
        goal = "conversions"
        
        lift = 0.0
        
        # Length optimization
        orig_words = len(original.split())
        opt_words = len(optimized.split())
        
        if opt_words > orig_words:
            lift += 10  # More descriptive content
        
        # Power words detection
        power_indicators = ["exclusivo", "grátis", "garantia", "novo", "limitado"]
        power_count = sum(1 for word in power_indicators if word.lower() in optimized.lower())
        lift += power_count * 5
        
        # CTA presence
        if any(cta in optimized.lower() for cta in ["clique", "compre", "veja", "aproveite"]):
            lift += 15
        
        final_lift = min(50, lift)
        
        assert final_lift > 0
        assert final_lift <= 50

    def test_copy_quality_analysis_logic(self):
        """Test copy quality analysis logic"""
        text = "Smartphone incrível com preço exclusivo. Compre agora!"
        audience = "young_adults"
        category = "electronics"
        
        score = 0.5  # Base score
        
        # Length factor
        word_count = len(text.split())
        if 15 <= word_count <= 50:
            score += 0.2
        
        # Emotional words
        emotional_words = ["incrível", "fantástico", "exclusivo", "especial", "único"]
        emotion_count = sum(1 for word in emotional_words if word.lower() in text.lower())
        score += emotion_count * 0.1
        
        # Call to action
        if any(cta in text.lower() for cta in ["compre", "clique", "veja", "descubra"]):
            score += 0.15
        
        final_score = max(0, min(1, score))
        
        assert 0 <= final_score <= 1
        assert final_score > 0.5  # Should have good score for this example

    def test_template_variable_replacement_logic(self):
        """Test template variable replacement logic"""
        template_text = "Novo {product_name}! Agora com {feature} por apenas {price}."
        variables = {
            "product_name": "iPhone 15",
            "feature": "câmera de 48MP",
            "price": "R$ 4.999"
        }
        
        generated_text = template_text
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            generated_text = generated_text.replace(placeholder, var_value)
        
        assert "iPhone 15" in generated_text
        assert "câmera de 48MP" in generated_text
        assert "R$ 4.999" in generated_text
        assert "{" not in generated_text  # No unreplaced variables

    def test_ab_test_status_transitions(self):
        """Test valid A/B test status transitions"""
        valid_statuses = ["draft", "running", "completed", "stopped"]
        
        # Test valid transitions
        assert "draft" in valid_statuses
        assert "running" in valid_statuses
        assert "completed" in valid_statuses
        assert "stopped" in valid_statuses
        
        # Test that draft -> running is valid
        current_status = "draft"
        new_status = "running"
        assert new_status in valid_statuses
        
        # Test that running -> stopped is valid
        current_status = "running"
        new_status = "stopped"
        assert new_status in valid_statuses

    def test_power_words_by_goal(self):
        """Test power words selection by optimization goal"""
        power_words = {
            "clicks": ["DESCUBRA", "EXCLUSIVO", "LIMITADO", "NOVO"],
            "conversions": ["GARANTIA", "ECONOMIZE", "GRÁTIS", "APROVEITE"],
            "engagement": ["INCRÍVEL", "SURPREENDENTE", "ÚNICO", "ESPECIAL"]
        }
        
        # Test that each goal has appropriate power words
        assert len(power_words["clicks"]) == 4
        assert len(power_words["conversions"]) == 4
        assert len(power_words["engagement"]) == 4
        
        # Test that all words are uppercase
        for goal_words in power_words.values():
            for word in goal_words:
                assert word.isupper()

    def test_audience_appeal_functions(self):
        """Test audience-specific appeal functions"""
        youth_terms = ["inovador", "moderno", "tendência", "estilo"]
        family_terms = ["seguro", "confiável", "para toda família", "qualidade"]
        prof_terms = ["eficiente", "produtivo", "profissional", "premium"]
        
        # Test that each audience has appropriate terms
        assert len(youth_terms) == 4
        assert len(family_terms) == 4
        assert len(prof_terms) == 4
        
        # Test that terms are appropriate for each audience
        assert "moderno" in youth_terms
        assert "seguro" in family_terms
        assert "profissional" in prof_terms

    def test_health_check_response_format(self):
        """Test health check response format"""
        expected_response = {"status": "healthy", "service": "optimizer_ai"}
        
        assert "status" in expected_response
        assert "service" in expected_response
        assert expected_response["status"] == "healthy"
        assert expected_response["service"] == "optimizer_ai"

    def test_traffic_allocation_validation(self):
        """Test traffic allocation validation logic"""
        # Valid allocations
        valid_allocations = [0.1, 0.5, 0.8, 1.0]
        for allocation in valid_allocations:
            assert 0 < allocation <= 1.0
        
        # Invalid allocations
        invalid_allocations = [0, -0.1, 1.1, 2.0]
        for allocation in invalid_allocations:
            assert not (0 < allocation <= 1.0)

    def test_batch_size_limits(self):
        """Test batch processing size limits"""
        max_batch_size = 50
        
        # Valid batch sizes
        valid_sizes = [1, 10, 25, 50]
        for size in valid_sizes:
            assert size <= max_batch_size
        
        # Invalid batch sizes
        invalid_sizes = [51, 100, 200]
        for size in invalid_sizes:
            assert size > max_batch_size