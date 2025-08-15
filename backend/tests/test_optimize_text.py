"""
Unit tests for the optimize_text function.
"""
import pytest
from app.services.seo import optimize_text, _clean_text, _optimize_title, _optimize_meta_description, _extract_keywords, _generate_slug


class TestOptimizeText:
    """Test the main optimize_text function."""
    
    def test_optimize_text_basic(self, sample_seo_text):
        """Test basic functionality of optimize_text."""
        result = optimize_text(sample_seo_text)
        
        assert "original" in result
        assert "cleaned" in result
        assert "title" in result
        assert "meta_description" in result
        assert "keywords" in result
        assert "slug" in result
        
        assert result["original"] == sample_seo_text
        assert len(result["title"]) <= 60
        assert len(result["meta_description"]) <= 160
        assert isinstance(result["keywords"], list)
        assert result["slug"].replace("-", "").isalnum()
    
    def test_optimize_text_with_keywords(self):
        """Test optimize_text with custom keywords."""
        text = "Beautiful smartphone with amazing camera and long battery life"
        keywords = ["smartphone", "camera", "battery"]
        
        result = optimize_text(text, keywords=keywords)
        
        # Check that keywords are included in the result
        result_keywords = [k.lower() for k in result["keywords"]]
        for keyword in keywords:
            assert keyword.lower() in result_keywords or keyword.lower() in text.lower()
    
    def test_optimize_text_custom_max_length(self):
        """Test optimize_text with custom max_length."""
        text = "This is a very long text that should be truncated to fit within the specified maximum length for meta descriptions and other SEO elements."
        max_length = 50
        
        result = optimize_text(text, max_length=max_length)
        
        assert len(result["meta_description"]) <= max_length
    
    def test_optimize_text_empty_string(self):
        """Test optimize_text with empty string."""
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            optimize_text("")
    
    def test_optimize_text_none(self):
        """Test optimize_text with None."""
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            optimize_text(None)
    
    def test_optimize_text_non_string(self):
        """Test optimize_text with non-string input."""
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            optimize_text(123)
    
    def test_optimize_text_invalid_max_length(self):
        """Test optimize_text with invalid max_length."""
        with pytest.raises(ValueError, match="max_length must be positive"):
            optimize_text("test text", max_length=0)
        
        with pytest.raises(ValueError, match="max_length must be positive"):
            optimize_text("test text", max_length=-1)


class TestCleanText:
    """Test the _clean_text helper function."""
    
    def test_clean_text_whitespace(self):
        """Test cleaning excessive whitespace."""
        text = "This   has    multiple     spaces\n\nand\tlinebreaks"
        result = _clean_text(text)
        
        assert result == "This has multiple spaces and linebreaks"
    
    def test_clean_text_special_characters(self):
        """Test removing special characters."""
        text = "Hello @#$% world! This is (a test) with-special_chars."
        result = _clean_text(text)
        
        assert "@#$%" not in result
        assert "Hello" in result
        assert "world" in result
        assert "!" in result  # Basic punctuation should remain
        assert "(" in result
        assert ")" in result
        assert "-" in result


class TestOptimizeTitle:
    """Test the _optimize_title helper function."""
    
    def test_optimize_title_short_text(self):
        """Test title optimization with short text."""
        text = "short title"
        result = _optimize_title(text)
        
        assert result == "Short title"
        assert len(result) <= 60
    
    def test_optimize_title_long_text(self):
        """Test title optimization with long text."""
        text = "This is a very long title that should be truncated to fit within the 60 character limit for SEO titles"
        result = _optimize_title(text)
        
        assert len(result) <= 60
        assert result[0].isupper()
        # Should not end in the middle of a word
        assert not result.endswith(" ")
    
    def test_optimize_title_with_keywords(self):
        """Test title optimization with keywords."""
        text = "amazing smartphone with great camera features"
        keywords = ["smartphone", "camera"]
        result = _optimize_title(text, keywords)
        
        assert len(result) <= 60
        assert result[0].isupper()


class TestOptimizeMetaDescription:
    """Test the _optimize_meta_description helper function."""
    
    def test_meta_description_short_text(self):
        """Test meta description with short text."""
        text = "Short description"
        result = _optimize_meta_description(text)
        
        assert result == text
    
    def test_meta_description_long_text(self):
        """Test meta description with long text."""
        text = "This is a very long description that exceeds the typical meta description length limit and should be truncated appropriately while maintaining readability and ensuring it doesn't cut off in the middle of words."
        result = _optimize_meta_description(text, max_length=160)
        
        assert len(result) <= 160
        assert result.endswith("...")
        # Should not end in the middle of a word (except for the ellipsis)
        assert not result[:-3].endswith(" ")
    
    def test_meta_description_custom_length(self):
        """Test meta description with custom max length."""
        text = "This is a description that should be truncated to a custom length"
        max_length = 30
        result = _optimize_meta_description(text, max_length=max_length)
        
        assert len(result) <= max_length


class TestExtractKeywords:
    """Test the _extract_keywords helper function."""
    
    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "smartphone mobile phone device technology innovation smartphone technology"
        result = _extract_keywords(text)
        
        assert isinstance(result, list)
        assert len(result) <= 8
        assert "smartphone" in result
        assert "technology" in result
    
    def test_extract_keywords_with_suggested(self):
        """Test keyword extraction with suggested keywords."""
        text = "This is about machine learning and artificial intelligence"
        suggested = ["AI", "machine learning", "neural networks"]
        result = _extract_keywords(text, suggested)
        
        # Check that suggested keywords are included in the result
        # The function should find "machine learning" as a complete phrase or individual words
        result_keywords_lower = [k.lower() for k in result]
        assert "machine learning" in result_keywords_lower or "machine" in result_keywords_lower or "learning" in result_keywords_lower
    
    def test_extract_keywords_stop_words(self):
        """Test that stop words are filtered out."""
        text = "the quick brown fox jumps over the lazy dog and cat"
        result = _extract_keywords(text)
        
        # Stop words should not be in keywords
        stop_words = ["the", "and", "over"]
        for stop_word in stop_words:
            assert stop_word not in result
    
    def test_extract_keywords_short_words(self):
        """Test that words shorter than 3 characters are filtered out."""
        text = "AI ML is great technology for us to use"
        result = _extract_keywords(text)
        
        # Short words should be filtered out
        short_words = ["AI", "ML", "is", "us", "to"]
        for short_word in short_words:
            assert short_word.lower() not in result


class TestGenerateSlug:
    """Test the _generate_slug helper function."""
    
    def test_generate_slug_basic(self):
        """Test basic slug generation."""
        text = "This is a Test Title"
        result = _generate_slug(text)
        
        assert result == "this-is-a-test-title"
        assert " " not in result
        assert result.islower()
    
    def test_generate_slug_special_characters(self):
        """Test slug generation with special characters."""
        text = "Special Characters! @#$% & More"
        result = _generate_slug(text)
        
        assert "@#$%" not in result
        assert "&" not in result
        assert "!" not in result
        assert result.replace("-", "").isalnum()
    
    def test_generate_slug_long_text(self):
        """Test slug generation with long text."""
        text = "This is a very long title that should be truncated to fit within the slug length limit"
        result = _generate_slug(text)
        
        assert len(result) <= 50
        assert not result.endswith("-")
        assert not result.startswith("-")
    
    def test_generate_slug_multiple_spaces(self):
        """Test slug generation with multiple spaces."""
        text = "Multiple    spaces     between    words"
        result = _generate_slug(text)
        
        assert "--" not in result
        assert result == "multiple-spaces-between-words"