"""
Unit tests for service modules.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.services.seo import (
    optimize_text, 
    _clean_text, 
    _optimize_title, 
    _optimize_meta_description,
    _extract_keywords,
    _generate_slug
)
from app.services.mercadolibre import (
    generate_code_verifier,
    generate_code_challenge,
    build_authorization_url
)


@pytest.mark.unit
class TestSEOService:
    """Test SEO service functionality."""
    
    def test_optimize_text_basic(self):
        """Test basic text optimization."""
        text = "This is a test product with great features"
        result = optimize_text(text, max_length=160)
        
        assert "original" in result
        assert "cleaned" in result
        assert "title" in result
        assert "meta_description" in result
        assert "keywords" in result
        assert "slug" in result
        
        assert result["original"] == text
        assert len(result["title"]) <= 60
        assert len(result["meta_description"]) <= 160
        assert isinstance(result["keywords"], list)
        assert isinstance(result["slug"], str)
    
    def test_optimize_text_with_keywords(self):
        """Test text optimization with suggested keywords."""
        text = "Premium wireless headphones with noise cancellation"
        keywords = ["wireless", "headphones", "premium"]
        result = optimize_text(text, keywords=keywords, max_length=140)
        
        # Keywords should be included in the result
        assert any(keyword in result["keywords"] for keyword in keywords)
        assert len(result["meta_description"]) <= 140
    
    def test_optimize_text_long_content(self):
        """Test optimization with long text content."""
        text = "This is a very long product description that contains many words and should be truncated properly when generating meta descriptions and titles to ensure they fit within SEO guidelines and don't exceed the recommended character limits for search engines."
        result = optimize_text(text, max_length=160)
        
        assert len(result["title"]) <= 60
        assert len(result["meta_description"]) <= 160
        assert result["meta_description"].endswith("...")
    
    def test_optimize_text_short_content(self):
        """Test optimization with short text content."""
        text = "Short text"
        result = optimize_text(text, max_length=160)
        
        assert result["meta_description"] == text  # Should not be truncated
        assert not result["meta_description"].endswith("...")
    
    def test_optimize_text_invalid_input(self):
        """Test optimization with invalid input."""
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            optimize_text("")
        
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            optimize_text(None)
        
        with pytest.raises(ValueError, match="max_length must be positive"):
            optimize_text("Valid text", max_length=0)
        
        with pytest.raises(ValueError, match="max_length must be positive"):
            optimize_text("Valid text", max_length=-1)
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "  This   has\n\nextra   whitespace  and@#$%special chars!  "
        cleaned = _clean_text(dirty_text)
        
        assert cleaned == "This has extra whitespace andspecial chars!"
        assert "  " not in cleaned
        assert "\n" not in cleaned
    
    def test_optimize_title(self):
        """Test title optimization."""
        long_text = "This is a very long title that should be truncated at the appropriate word boundary"
        title = _optimize_title(long_text)
        
        assert len(title) <= 60
        assert title[0].isupper()  # Should be capitalized
        assert not title.endswith(" ")  # Should not end with space
    
    def test_optimize_title_short(self):
        """Test title optimization with short text."""
        short_text = "short title"
        title = _optimize_title(short_text)
        
        assert title == "Short title"  # Should be capitalized
        assert len(title) == len(short_text)
    
    def test_optimize_meta_description(self):
        """Test meta description optimization."""
        long_text = "This is a very long description that needs to be truncated to fit within the meta description length limits while maintaining readability and not cutting off in the middle of important words."
        meta_desc = _optimize_meta_description(long_text, max_length=160)
        
        assert len(meta_desc) <= 160
        assert meta_desc.endswith("...")
        assert not meta_desc.endswith(" ...")  # Should not have space before ellipsis
    
    def test_optimize_meta_description_exact_length(self):
        """Test meta description with exact max length."""
        text = "a" * 160
        meta_desc = _optimize_meta_description(text, max_length=160)
        
        assert len(meta_desc) == 160
        assert not meta_desc.endswith("...")
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "premium wireless headphones with noise cancellation technology"
        keywords = _extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 8
        assert "premium" in keywords
        assert "wireless" in keywords
        assert "headphones" in keywords
        # Stop words should be filtered out
        assert "with" not in keywords
    
    def test_extract_keywords_with_suggestions(self):
        """Test keyword extraction with suggested keywords."""
        text = "premium wireless headphones with noise cancellation"
        suggested = ["wireless", "audio", "technology"]
        keywords = _extract_keywords(text, suggested)
        
        assert "wireless" in keywords  # Should be included (appears in text)
        assert "technology" not in keywords  # Should not be included (not in text)
    
    def test_generate_slug(self):
        """Test URL slug generation."""
        text = "Premium Wireless Headphones - Best Quality!"
        slug = _generate_slug(text)
        
        assert slug == "premium-wireless-headphones-best-quality"
        assert " " not in slug
        assert slug.islower()
        assert not slug.startswith("-")
        assert not slug.endswith("-")
    
    def test_generate_slug_long_text(self):
        """Test slug generation with long text."""
        long_text = "This is a very long product title that should be truncated to fit slug length limits"
        slug = _generate_slug(long_text)
        
        assert len(slug) <= 50
        assert not slug.endswith("-")
    
    def test_generate_slug_special_characters(self):
        """Test slug generation with special characters."""
        text = "Product @#$% Name with Special Characters!"
        slug = _generate_slug(text)
        
        assert slug == "product-name-with-special-characters"
        assert "@" not in slug
        assert "#" not in slug
        assert "$" not in slug
        assert "%" not in slug
        assert "!" not in slug


@pytest.mark.unit
class TestMercadoLibreService:
    """Test Mercado Libre service functionality."""
    
    def test_generate_code_verifier(self):
        """Test code verifier generation."""
        verifier = generate_code_verifier()
        
        assert isinstance(verifier, str)
        assert len(verifier) >= 43  # Minimum length according to RFC 7636
        assert len(verifier) <= 128  # Maximum length according to RFC 7636
        # Should contain only URL-safe characters
        import re
        assert re.match(r'^[A-Za-z0-9\-._~]+$', verifier)
    
    def test_generate_code_verifier_uniqueness(self):
        """Test that code verifiers are unique."""
        verifier1 = generate_code_verifier()
        verifier2 = generate_code_verifier()
        
        assert verifier1 != verifier2
    
    def test_generate_code_challenge(self):
        """Test code challenge generation."""
        verifier = "test_verifier_123456789"
        challenge = generate_code_challenge(verifier)
        
        assert isinstance(challenge, str)
        assert len(challenge) == 43  # Base64url encoded SHA256 hash length
        # Should be base64url encoded (no padding)
        import re
        assert re.match(r'^[A-Za-z0-9\-_]+$', challenge)
        assert "=" not in challenge  # No padding in base64url
    
    def test_generate_code_challenge_consistency(self):
        """Test that same verifier produces same challenge."""
        verifier = "consistent_verifier"
        challenge1 = generate_code_challenge(verifier)
        challenge2 = generate_code_challenge(verifier)
        
        assert challenge1 == challenge2
    
    def test_build_authorization_url(self):
        """Test authorization URL building."""
        client_id = "test_client_id"
        redirect_uri = "https://example.com/callback"
        state = "test_state"
        code_challenge = "test_challenge"
        
        url = build_authorization_url(client_id, redirect_uri, state, code_challenge)
        
        assert url.startswith("https://auth.mercadolibre.com.br/authorization")
        assert f"client_id={client_id}" in url
        assert f"redirect_uri={redirect_uri}" in url
        assert f"state={state}" in url
        assert f"code_challenge={code_challenge}" in url
        assert "response_type=code" in url
        assert "code_challenge_method=S256" in url
    
    def test_build_authorization_url_with_scope(self):
        """Test authorization URL building with scope."""
        url = build_authorization_url(
            "client_id",
            "https://example.com/callback",
            "state",
            "challenge",
            scope="read write"
        )
        
        assert "scope=read%20write" in url
    
    def test_build_authorization_url_without_scope(self):
        """Test authorization URL building without scope."""
        url = build_authorization_url(
            "client_id",
            "https://example.com/callback", 
            "state",
            "challenge"
        )
        
        # Should not contain scope parameter
        assert "scope=" not in url


@pytest.mark.unit
class TestServiceIntegration:
    """Test integration between services."""
    
    @patch('app.services.seo.logger')
    def test_seo_service_logging(self, mock_logger):
        """Test that SEO service logs optimization activities."""
        text = "Test product description"
        optimize_text(text)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Optimized text" in call_args
        assert "chars" in call_args
    
    def test_oauth_flow_integration(self):
        """Test OAuth flow component integration."""
        # Generate verifier and challenge
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        
        # Build authorization URL
        url = build_authorization_url(
            "test_client",
            "https://example.com/callback",
            "test_state",
            challenge
        )
        
        # Verify the complete flow works together
        assert verifier != challenge
        assert len(verifier) >= 43
        assert len(challenge) == 43
        assert "test_client" in url
        assert challenge in url