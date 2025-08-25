"""
Unit tests for service layer functionality.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import httpx
from datetime import datetime, timedelta

from app.services.seo import optimize_text, _clean_text as clean_text, _extract_keywords as extract_keywords, _generate_slug as generate_slug
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
        text = "This is a sample product description for testing."
        result = optimize_text(text)
        
        assert isinstance(result, dict)
        assert "original" in result
        assert "title" in result
        assert "meta_description" in result
        assert "keywords" in result
        assert "slug" in result
        assert result["original"] == text
        
    def test_optimize_text_with_custom_max_length(self):
        """Test text optimization with custom max length."""
        text = "This is a very long product description that should be truncated."
        max_length = 30
        result = optimize_text(text, max_length=max_length)
        
        assert len(result["meta_description"]) <= max_length
        
    def test_optimize_text_with_keywords(self):
        """Test text optimization with provided keywords."""
        text = "This is a sample product description."
        keywords = ["sample", "product", "description"]
        result = optimize_text(text, keywords=keywords)
        
        # Check that provided keywords are included
        for keyword in keywords:
            assert keyword in result["keywords"]
            
    def test_optimize_text_empty_string(self):
        """Test optimization with empty string."""
        result = optimize_text("")
        
        assert result["original"] == ""
        assert result["title"] == ""
        assert result["meta_description"] == ""
        assert result["keywords"] == []
        assert result["slug"] == ""
        
    def test_optimize_text_none_input(self):
        """Test optimization with None input."""
        with pytest.raises((TypeError, AttributeError)):
            optimize_text(None)
            
    def test_optimize_text_non_string_input(self):
        """Test optimization with non-string input."""
        with pytest.raises((TypeError, AttributeError)):
            optimize_text(123)
            
    def test_optimize_text_invalid_max_length(self):
        """Test optimization with invalid max_length."""
        text = "Sample text"
        
        with pytest.raises((ValueError, TypeError)):
            optimize_text(text, max_length=0)
            
        with pytest.raises((ValueError, TypeError)):
            optimize_text(text, max_length=-1)


@pytest.mark.unit
class TestSEOUtilityFunctions:
    """Test SEO utility functions."""
    
    def test_clean_text_whitespace(self):
        """Test text cleaning with whitespace."""
        text = "  This   has   extra   spaces  "
        cleaned = clean_text(text)
        
        assert cleaned == "This has extra spaces"
        
    def test_clean_text_special_characters(self):
        """Test text cleaning with special characters."""
        text = "Text with special chars: @#$%^&*()"
        cleaned = clean_text(text)
        
        # Should remove or handle special characters appropriately
        assert len(cleaned) <= len(text)
        
    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "This is a sample product description for testing keyword extraction."
        keywords = extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # Common words should be filtered out
        assert "is" not in keywords
        assert "a" not in keywords
        
    def test_extract_keywords_with_suggested(self):
        """Test keyword extraction with suggested keywords."""
        text = "Sample product description"
        suggested = ["product", "quality", "best"]
        keywords = extract_keywords(text, suggested_keywords=suggested)
        
        # Should include relevant suggested keywords
        assert "product" in keywords
        
    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text."""
        keywords = extract_keywords("")
        
        assert isinstance(keywords, list)
        assert len(keywords) == 0
        
    def test_generate_slug_basic(self):
        """Test basic slug generation."""
        text = "This is a Sample Product Title"
        slug = generate_slug(text)
        
        assert isinstance(slug, str)
        assert " " not in slug
        assert slug.islower()
        assert "this-is-a-sample-product-title" == slug or slug.replace("-", "") == text.lower().replace(" ", "")
        
    def test_generate_slug_special_characters(self):
        """Test slug generation with special characters."""
        text = "Product Title with Special Chars!@#$%"
        slug = generate_slug(text)
        
        # Should remove special characters
        assert "!" not in slug
        assert "@" not in slug
        assert "#" not in slug
        
    def test_generate_slug_long_text(self):
        """Test slug generation with long text."""
        text = "This is a very long product title that should be truncated appropriately for SEO purposes"
        slug = generate_slug(text)
        
        # Should be reasonably short
        assert len(slug) < len(text)
        
    def test_generate_slug_multiple_spaces(self):
        """Test slug generation with multiple consecutive spaces."""
        text = "Product    Title    With    Spaces"
        slug = generate_slug(text)
        
        # Should not have consecutive dashes
        assert "--" not in slug


@pytest.mark.unit
class TestMercadoLibreService:
    """Test Mercado Libre service functionality."""
    
    def test_generate_code_verifier(self):
        """Test code verifier generation."""
        verifier = generate_code_verifier()
        
        assert isinstance(verifier, str)
        assert len(verifier) >= 43  # PKCE requirement
        assert len(verifier) <= 128  # PKCE requirement
        
        # Should be different each time
        verifier2 = generate_code_verifier()
        assert verifier != verifier2
        
    def test_generate_code_challenge(self):
        """Test code challenge generation."""
        verifier = "test_code_verifier_123"
        challenge = generate_code_challenge(verifier)
        
        assert isinstance(challenge, str)
        assert len(challenge) > 0
        
        # Same verifier should produce same challenge
        challenge2 = generate_code_challenge(verifier)
        assert challenge == challenge2
        
    def test_build_authorization_url(self):
        """Test authorization URL building."""
        client_id = "test_client_123"
        redirect_uri = "http://localhost:8000/callback"
        state = "test_state_456"
        code_challenge = "test_challenge_789"
        
        url = build_authorization_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
            scope="read write"
        )
        
        assert isinstance(url, str)
        assert url.startswith("https://auth.mercadolivre.com.br/authorization")
        assert client_id in url
        assert redirect_uri in url
        assert state in url
        assert code_challenge in url
        
    def test_build_authorization_url_default_scope(self):
        """Test authorization URL building with default scope."""
        url = build_authorization_url(
            client_id="test_client",
            redirect_uri="http://localhost:8000/callback",
            state="test_state",
            code_challenge="test_challenge"
        )
        
        # Should include default scope
        assert "scope=" in url


@pytest.mark.unit  
class TestServiceErrorHandling:
    """Test service error handling scenarios."""
    
    def test_seo_optimize_with_invalid_input(self):
        """Test SEO optimization error handling."""
        # Test various invalid inputs
        invalid_inputs = [None, 123, [], {}, object()]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((TypeError, AttributeError)):
                optimize_text(invalid_input)
                
    def test_seo_optimize_with_invalid_max_length(self):
        """Test SEO optimization with invalid max_length values."""
        text = "Sample text"
        invalid_lengths = [0, -1, -10, "invalid"]
        
        for invalid_length in invalid_lengths:
            with pytest.raises((ValueError, TypeError)):
                optimize_text(text, max_length=invalid_length)
                
    def test_mercadolibre_authorization_url_missing_params(self):
        """Test authorization URL building with missing parameters."""
        with pytest.raises(TypeError):
            build_authorization_url()  # Missing required parameters
            
        with pytest.raises((TypeError, ValueError)):
            build_authorization_url(client_id="")  # Empty client_id
            
    def test_code_challenge_with_invalid_verifier(self):
        """Test code challenge generation with invalid verifier."""
        invalid_verifiers = [None, "", 123, []]
        
        for invalid_verifier in invalid_verifiers:
            with pytest.raises((TypeError, AttributeError)):
                generate_code_challenge(invalid_verifier)


@pytest.mark.unit
class TestServiceMocking:
    """Test service behavior with mocked dependencies."""
    
    @patch('app.services.seo.extract_keywords')
    def test_optimize_text_with_mocked_keywords(self, mock_extract):
        """Test text optimization with mocked keyword extraction."""
        # Mock the keyword extraction
        mock_extract.return_value = ["mocked", "keywords", "test"]
        
        text = "Sample product description"
        result = optimize_text(text)
        
        mock_extract.assert_called_once_with(text, suggested_keywords=None)
        assert result["keywords"] == ["mocked", "keywords", "test"]
        
    @patch('app.services.seo.generate_slug')
    def test_optimize_text_with_mocked_slug(self, mock_slug):
        """Test text optimization with mocked slug generation."""
        # Mock the slug generation
        mock_slug.return_value = "mocked-slug"
        
        text = "Sample product description"
        result = optimize_text(text)
        
        mock_slug.assert_called_once_with(text)
        assert result["slug"] == "mocked-slug"
        
    @patch('hashlib.sha256')
    @patch('base64.urlsafe_b64encode')
    def test_code_challenge_generation_mocked(self, mock_b64encode, mock_sha256):
        """Test code challenge generation with mocked crypto functions."""
        # Mock the hash and encoding
        mock_hash = Mock()
        mock_hash.digest.return_value = b"mocked_hash"
        mock_sha256.return_value = mock_hash
        mock_b64encode.return_value = b"mocked_encoded"
        
        verifier = "test_verifier"
        result = generate_code_challenge(verifier)
        
        mock_sha256.assert_called_once_with(verifier.encode('utf-8'))
        mock_b64encode.assert_called_once_with(b"mocked_hash")
        
    @patch('secrets.token_urlsafe')
    def test_code_verifier_generation_mocked(self, mock_token):
        """Test code verifier generation with mocked secrets."""
        mock_token.return_value = "mocked_verifier_token"
        
        result = generate_code_verifier()
        
        mock_token.assert_called_once_with(32)
        assert result == "mocked_verifier_token"


@pytest.mark.unit
class TestServiceIntegration:
    """Test integration between different service functions."""
    
    def test_seo_optimization_workflow(self):
        """Test complete SEO optimization workflow."""
        text = "High-quality wireless bluetooth headphones with noise cancellation"
        
        result = optimize_text(text, max_length=120)
        
        # Verify all components work together
        assert result["original"] == text
        assert len(result["meta_description"]) <= 120
        assert isinstance(result["keywords"], list)
        assert len(result["keywords"]) > 0
        assert isinstance(result["slug"], str)
        assert len(result["slug"]) > 0
        
        # Keywords should be relevant to the text
        text_words = text.lower().split()
        for keyword in result["keywords"][:3]:  # Check first few keywords
            assert any(keyword in word for word in text_words)
            
    def test_mercadolibre_oauth_workflow(self):
        """Test Mercado Libre OAuth workflow components."""
        # Generate verifier and challenge
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        
        # Build authorization URL
        url = build_authorization_url(
            client_id="test_client_id",
            redirect_uri="http://localhost:8000/oauth/callback",
            state="random_state_123",
            code_challenge=challenge,
            scope="offline_access read write"
        )
        
        # Verify the workflow produces valid results
        assert len(verifier) >= 43
        assert len(challenge) > 0
        assert "test_client_id" in url
        assert challenge in url
        assert "random_state_123" in url
        
    def test_service_error_propagation(self):
        """Test that errors are properly propagated between services."""
        # Test error propagation in SEO service
        with pytest.raises((TypeError, AttributeError)):
            result = optimize_text(None)
            
        # Test error propagation in Mercado Libre service
        with pytest.raises((TypeError, AttributeError)):
            challenge = generate_code_challenge(None)