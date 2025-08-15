"""
SEO text optimization service.
"""
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("app.seo")


def optimize_text(text: str, keywords: Optional[List[str]] = None, max_length: int = 160) -> Dict[str, str]:
    """
    Optimize text for SEO purposes.
    
    Args:
        text: Original text to optimize
        keywords: List of keywords to emphasize
        max_length: Maximum length for meta descriptions
        
    Returns:
        Dictionary with optimized text variations
    """
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")
    
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    
    # Clean the text
    cleaned_text = _clean_text(text)
    
    # Generate optimized versions
    result = {
        "original": text,
        "cleaned": cleaned_text,
        "title": _optimize_title(cleaned_text, keywords),
        "meta_description": _optimize_meta_description(cleaned_text, keywords, max_length),
        "keywords": _extract_keywords(cleaned_text, keywords),
        "slug": _generate_slug(cleaned_text)
    }
    
    logger.info(f"Optimized text: {len(text)} -> {len(result['cleaned'])} chars")
    return result


def _clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    cleaned = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', cleaned)
    
    return cleaned


def _optimize_title(text: str, keywords: Optional[List[str]] = None) -> str:
    """Generate SEO-optimized title."""
    # Take first 60 characters for title
    title = text[:60].strip()
    
    # Ensure it doesn't end in the middle of a word
    if len(text) > 60:
        last_space = title.rfind(' ')
        if last_space > 30:  # Only if we have enough text
            title = title[:last_space]
    
    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]
    
    return title


def _optimize_meta_description(text: str, keywords: Optional[List[str]] = None, max_length: int = 160) -> str:
    """Generate SEO-optimized meta description."""
    if len(text) <= max_length:
        return text
    
    # Find best cut point
    description = text[:max_length].strip()
    
    # Ensure it doesn't end in the middle of a word
    last_space = description.rfind(' ')
    if last_space > max_length * 0.8:  # Only if we're not cutting too much
        description = description[:last_space]
    
    # Add ellipsis if truncated, but make sure total length doesn't exceed max_length
    if len(text) > len(description):
        if len(description) + 3 <= max_length:
            description += "..."
        else:
            # Adjust to fit ellipsis within max_length
            description = description[:max_length-3] + "..."
    
    return description


def _extract_keywords(text: str, suggested_keywords: Optional[List[str]] = None) -> List[str]:
    """Extract relevant keywords from text."""
    # Convert to lowercase for processing
    lower_text = text.lower()
    
    # Split into words and filter
    words = re.findall(r'\b\w{3,}\b', lower_text)  # Words with 3+ characters
    
    # Count word frequency
    word_count = {}
    for word in words:
        # Skip common stop words
        if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
            word_count[word] = word_count.get(word, 0) + 1
    
    # Get most frequent words
    frequent_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
    keywords = [word for word, count in frequent_words if count > 1]
    
    # Add suggested keywords if they appear in text
    if suggested_keywords:
        for keyword in suggested_keywords:
            keyword_lower = keyword.lower()
            # Check if the keyword (as phrase or individual words) appears in text
            if keyword_lower in lower_text:
                if keyword_lower not in keywords:
                    keywords.append(keyword_lower)
            else:
                # Check individual words of the suggested keyword
                keyword_words = keyword_lower.split()
                for word in keyword_words:
                    if word in lower_text and word not in keywords and len(word) >= 3:
                        keywords.append(word)
    
    return keywords[:8]  # Limit to 8 keywords


def _generate_slug(text: str) -> str:
    """Generate URL-friendly slug."""
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    
    return slug