import pytest
import sys
import os

# Add the parent directory to the Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_copywriting_request():
    """Sample copywriting optimization request for testing"""
    return {
        "original_text": "Smartphone com boa qualidade",
        "target_audience": "young_adults",
        "product_category": "electronics",
        "optimization_goal": "conversions",
        "keywords": ["smartphone", "celular", "tecnologia", "qualidade"]
    }

@pytest.fixture
def sample_ab_test_request():
    """Sample A/B test request for testing"""
    return {
        "name": "Smartphone Copy Test",
        "variations": [
            "Smartphone com boa qualidade e preço baixo",
            "Celular incrível com tecnologia avançada",
            "O melhor smartphone do mercado com garantia"
        ],
        "audience": "young_adults",
        "category": "electronics",
        "traffic_allocation": 0.8,
        "duration_days": 14
    }

@pytest.fixture
def sample_template_request():
    """Sample template request for testing"""
    return {
        "name": "Product Launch Template",
        "description": "Template for launching new products",
        "category": "product_launch",
        "template_text": "Novo {product_name}! Agora com {feature} por apenas {price}. {call_to_action}",
        "variables": ["product_name", "feature", "price", "call_to_action"],
        "tags": ["launch", "promotion", "new"]
    }

@pytest.fixture
def sample_template_generate_request():
    """Sample template generation request for testing"""
    return {
        "template_id": "TPL_TEST123",
        "variables": {
            "product_name": "iPhone 15",
            "feature": "câmera de 48MP",
            "price": "R$ 4.999",
            "call_to_action": "Compre agora!"
        }
    }

@pytest.fixture
def sample_batch_request():
    """Sample batch optimization request for testing"""
    return {
        "texts": [
            "Produto de qualidade",
            "Melhor preço do mercado",
            "Entrega rápida garantida"
        ],
        "target_audience": "families",
        "product_category": "home",
        "optimization_goal": "clicks",
        "keywords": ["qualidade", "preço", "entrega"]
    }