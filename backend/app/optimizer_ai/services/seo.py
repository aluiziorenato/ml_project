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
    cleaned = re.sub(r'\s+', ' ', text.strip())
    cleaned = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', cleaned)
    return cleaned

def _optimize_title(text: str, keywords: Optional[List[str]] = None) -> str:
    """Generate SEO-optimized title."""
    title = text[:60].strip()
    if len(text) > 60:
        last_space = title.rfind(' ')
        if last_space > 30:
            title = title[:last_space]
    if title:
        title = title[0].upper() + title[1:]
    return title

def _optimize_meta_description(text: str, keywords: Optional[List[str]] = None, max_length: int = 160) -> str:
    """Generate SEO-optimized meta description."""
    if len(text) <= max_length:
        return text
    description = text[:max_length].strip()
    last_space = description.rfind(' ')
    if last_space > max_length * 0.8:
        description = description[:last_space]
    if len(text) > len(description):
        if len(description) + 3 <= max_length:
            description += "..."
        else:
            description = description[:max_length-3] + "..."
    return description

def _extract_keywords(text: str, suggested_keywords: Optional[List[str]] = None) -> List[str]:
    """Extract relevant keywords from text."""
    words = re.findall(r'\b\w{4,}\b', text.lower())
    keywords = list(set(words))
    if suggested_keywords:
        keywords.extend([kw.lower() for kw in suggested_keywords if kw.lower() not in keywords])
    return sorted(set(keywords))

def _generate_slug(text: str) -> str:
    """Generate URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    return slug
