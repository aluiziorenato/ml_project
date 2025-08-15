"""
Model and service snapshot regression tests using pytest-regressions.

These tests capture the output of model processing and service functions
to detect unintended changes in business logic over time.
"""
import pytest
from app.services.seo import optimize_text
from app.services.mercadolibre import (
    generate_code_verifier,
    generate_code_challenge,
    build_authorization_url
)


class TestSEOServiceSnapshots:
    """Test SEO service function snapshots for regression detection."""

    def test_optimize_text_basic_snapshot(self, data_regression):
        """Test basic SEO text optimization snapshot."""
        result = optimize_text(
            text="This is a sample product description for testing",
            keywords=None,
            max_length=160
        )
        
        data_regression.check(result)

    def test_optimize_text_with_keywords_snapshot(self, data_regression):
        """Test SEO optimization with keywords snapshot."""
        result = optimize_text(
            text="Modern electronics and technology products for consumers with advanced features",
            keywords=["electronics", "technology", "modern", "advanced"],
            max_length=150
        )
        
        data_regression.check(result)

    def test_optimize_text_long_content_snapshot(self, data_regression):
        """Test SEO optimization with long content snapshot."""
        long_text = """
        This is a comprehensive product description that contains multiple sentences 
        and detailed information about the product features, specifications, and benefits. 
        The text is intentionally long to test how the optimization handles content 
        that exceeds the maximum meta description length and needs to be truncated 
        appropriately while maintaining readability and keyword density.
        """
        
        result = optimize_text(
            text=long_text,
            keywords=["product", "features", "comprehensive"],
            max_length=160
        )
        
        data_regression.check(result)

    def test_optimize_text_short_content_snapshot(self, data_regression):
        """Test SEO optimization with short content snapshot."""
        result = optimize_text(
            text="Short product name",
            keywords=["product"],
            max_length=160
        )
        
        data_regression.check(result)

    def test_optimize_text_special_characters_snapshot(self, data_regression):
        """Test SEO optimization with special characters snapshot."""
        result = optimize_text(
            text="Product! With @special #characters & symbols (test) - version 2.0",
            keywords=["product", "special", "version"],
            max_length=120
        )
        
        data_regression.check(result)

    def test_optimize_text_different_max_lengths_snapshot(self, data_regression):
        """Test SEO optimization with different max lengths."""
        base_text = "This is a product description that will be tested with different maximum length constraints"
        
        results = {}
        for max_len in [50, 100, 200]:
            result = optimize_text(
                text=base_text,
                keywords=["product", "description"],
                max_length=max_len
            )
            results[f"max_length_{max_len}"] = result
        
        data_regression.check(results)

    def test_optimize_text_keywords_extraction_snapshot(self, data_regression):
        """Test keyword extraction functionality snapshot."""
        text_with_repeated_words = """
        Machine learning and artificial intelligence are transforming technology.
        Machine learning algorithms enable intelligent systems to learn and adapt.
        Technology advancement through machine learning creates intelligent solutions.
        """
        
        result = optimize_text(
            text=text_with_repeated_words,
            keywords=["artificial", "intelligence"],
            max_length=160
        )
        
        data_regression.check(result)

    def test_optimize_text_edge_cases_snapshot(self, data_regression):
        """Test SEO optimization edge cases snapshot."""
        edge_cases = {}
        
        # Test with minimal text
        edge_cases["minimal"] = optimize_text("A", max_length=160)
        
        # Test with exact max length
        exact_text = "a" * 160
        edge_cases["exact_length"] = optimize_text(exact_text, max_length=160)
        
        # Test with numbers and mixed content
        edge_cases["mixed_content"] = optimize_text(
            "Product 123 with 4.5 rating and 99% satisfaction in 2024",
            keywords=["product", "rating"],
            max_length=80
        )
        
        data_regression.check(edge_cases)


class TestMercadoLibreServiceSnapshots:
    """Test Mercado Libre service function snapshots."""

    def test_code_verifier_generation_properties_snapshot(self, data_regression):
        """Test code verifier generation properties snapshot."""
        # Generate multiple verifiers to test consistency
        verifiers = []
        for i in range(5):
            verifier = generate_code_verifier()
            verifiers.append({
                "length": len(verifier),
                "is_string": isinstance(verifier, str),
                "has_valid_chars": all(c.isalnum() or c in '-._~' for c in verifier)
            })
        
        data_regression.check({"verifier_properties": verifiers})

    def test_code_challenge_generation_snapshot(self, data_regression):
        """Test code challenge generation snapshot."""
        # Use a fixed verifier to get consistent challenge
        test_verifier = "test_verifier_123"
        challenge = generate_code_challenge(test_verifier)
        
        result = {
            "challenge": challenge,
            "challenge_length": len(challenge),
            "is_string": isinstance(challenge, str),
            "verifier_used": test_verifier
        }
        
        data_regression.check(result)

    def test_authorization_url_building_snapshot(self, data_regression):
        """Test authorization URL building snapshot."""
        # Use fixed parameters for consistent snapshot
        url = build_authorization_url(
            state="test_state_456",
            code_challenge="test_challenge_789",
            redirect_uri="https://example.com/callback"
        )
        
        # Parse URL components for snapshot (without exposing full URL)
        result = {
            "has_client_id": "client_id=test_client_123" in url,
            "has_redirect_uri": "redirect_uri=" in url,
            "has_state": "state=test_state_456" in url,
            "has_code_challenge": "code_challenge=test_challenge_789" in url,
            "has_scope": "scope=" in url,
            "is_https": url.startswith("https://"),
            "base_domain": url.split("?")[0],
            "param_count": len(url.split("?")[1].split("&")) if "?" in url else 0
        }
        
        data_regression.check(result)


class TestModelDataTransformations:
    """Test data transformation and processing functions."""

    def test_seo_slug_generation_patterns_snapshot(self, data_regression):
        """Test slug generation patterns for various inputs."""
        from app.services.seo import _generate_slug
        
        test_cases = [
            "Simple Product Name",
            "Product With Special Characters!@#",
            "Product-with-hyphens-already",
            "Product_with_underscores",
            "Product with números 123 and símbolos",
            "Very Long Product Name That Should Be Truncated Because It Exceeds Maximum Length",
            "Mixed CASE product Name",
            "   Product with extra spaces   "
        ]
        
        results = {}
        for i, text in enumerate(test_cases):
            slug = _generate_slug(text)
            results[f"case_{i+1}"] = {
                "original": text,
                "slug": slug,
                "length": len(slug)
            }
        
        data_regression.check(results)

    def test_seo_keyword_extraction_patterns_snapshot(self, data_regression):
        """Test keyword extraction patterns."""
        from app.services.seo import _extract_keywords
        
        test_texts = [
            "Technology product with advanced features and modern design",
            "The quick brown fox jumps over the lazy dog repeatedly",
            "Machine learning artificial intelligence deep learning neural networks",
            "Product review: excellent quality, great price, fast shipping, recommended",
            "Short text",
            "Repetitive repetitive repetitive word word word test test test"
        ]
        
        results = {}
        for i, text in enumerate(test_texts):
            keywords = _extract_keywords(text, ["quality", "technology"])
            results[f"text_{i+1}"] = {
                "original": text,
                "keywords": keywords,
                "keyword_count": len(keywords)
            }
        
        data_regression.check(results)

    def test_seo_title_optimization_patterns_snapshot(self, data_regression):
        """Test title optimization patterns."""
        from app.services.seo import _optimize_title
        
        test_cases = [
            "short title",
            "This is a medium length title that should work well",
            "This is a very long title that will definitely exceed the maximum length limit and should be truncated",
            "title with special characters!@#$%",
            "TITLE IN ALL CAPS",
            "title with numbers 123 and symbols &*(",
            "a",  # single character
            ""   # empty string
        ]
        
        results = {}
        for i, text in enumerate(test_cases):
            if text:  # Skip empty string to avoid errors
                title = _optimize_title(text, ["special", "keywords"])
                results[f"case_{i+1}"] = {
                    "original": text,
                    "optimized": title,
                    "length": len(title)
                }
        
        data_regression.check(results)

    def test_seo_meta_description_optimization_snapshot(self, data_regression):
        """Test meta description optimization patterns."""
        from app.services.seo import _optimize_meta_description
        
        test_cases = [
            ("Short description", 160),
            ("Medium length description that should fit within normal limits", 160),
            ("Very long description that will definitely exceed the maximum length and needs to be truncated properly while maintaining readability", 160),
            ("Description for short limit", 50),
            ("Perfect length description text", 30),
            ("Text with special characters !@#$%^&*()", 100)
        ]
        
        results = {}
        for i, (text, max_len) in enumerate(test_cases):
            description = _optimize_meta_description(text, None, max_len)
            results[f"case_{i+1}"] = {
                "original": text,
                "max_length": max_len,
                "optimized": description,
                "final_length": len(description)
            }
        
        data_regression.check(results)


class TestIntegrationSnapshots:
    """Test integration between different components."""

    def test_complete_seo_optimization_workflow_snapshot(self, data_regression):
        """Test complete SEO optimization workflow."""
        test_scenarios = [
            {
                "name": "e_commerce_product",
                "text": "Premium wireless headphones with noise cancellation and 30-hour battery life",
                "keywords": ["wireless", "headphones", "premium", "battery"],
                "max_length": 155
            },
            {
                "name": "service_description", 
                "text": "Professional web development services using modern technologies and best practices",
                "keywords": ["web", "development", "professional", "modern"],
                "max_length": 140
            },
            {
                "name": "blog_article",
                "text": "How to improve your website's search engine optimization for better visibility",
                "keywords": ["SEO", "website", "optimization", "visibility"],
                "max_length": 160
            }
        ]
        
        results = {}
        for scenario in test_scenarios:
            result = optimize_text(
                text=scenario["text"],
                keywords=scenario["keywords"],
                max_length=scenario["max_length"]
            )
            results[scenario["name"]] = result
        
        data_regression.check(results)