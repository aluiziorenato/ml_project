"""
Optimizer AI - FastAPI service for AI-powered copywriting optimization.

This service provides endpoints for generating optimized titles and descriptions
using AI techniques for marketing and copywriting purposes.
"""

import logging
import re
import random
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("optimizer_ai")

# FastAPI app initialization
app = FastAPI(
    title="Optimizer AI - Copywriting Service",
    description="AI-powered service for generating optimized marketing copy, titles, and descriptions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class GenerateTitleRequest(BaseModel):
    """Request model for title generation."""
    text: str = Field(..., min_length=1, max_length=1000, description="Base text or product description")
    keywords: Optional[List[str]] = Field(default=None, description="Target keywords to include")
    tone: Optional[str] = Field(default="professional", description="Tone of voice: professional, casual, exciting, luxury")
    max_length: Optional[int] = Field(default=60, ge=10, le=100, description="Maximum title length in characters")

class GenerateDescriptionRequest(BaseModel):
    """Request model for description generation."""
    text: str = Field(..., min_length=1, max_length=2000, description="Base text or product information")
    keywords: Optional[List[str]] = Field(default=None, description="Target keywords to include")
    tone: Optional[str] = Field(default="professional", description="Tone of voice: professional, casual, exciting, luxury")
    max_length: Optional[int] = Field(default=160, ge=50, le=500, description="Maximum description length in characters")
    cta_style: Optional[str] = Field(default="soft", description="Call-to-action style: soft, direct, urgent")

class TitleResponse(BaseModel):
    """Response model for generated titles."""
    title: str = Field(..., description="Generated optimized title")
    alternatives: List[str] = Field(..., description="Alternative title suggestions")
    keywords_used: List[str] = Field(..., description="Keywords successfully incorporated")
    length: int = Field(..., description="Character length of main title")
    tone: str = Field(..., description="Tone of voice applied")

class DescriptionResponse(BaseModel):
    """Response model for generated descriptions."""
    description: str = Field(..., description="Generated optimized description")
    alternatives: List[str] = Field(..., description="Alternative description suggestions")
    keywords_used: List[str] = Field(..., description="Keywords successfully incorporated")
    length: int = Field(..., description="Character length of main description")
    tone: str = Field(..., description="Tone of voice applied")
    cta_included: bool = Field(..., description="Whether call-to-action was included")

# AI-powered content generation functions
def _clean_text(text: str) -> str:
    """Clean and normalize input text."""
    # Remove extra whitespace and special characters
    cleaned = re.sub(r'\s+', ' ', text.strip())
    cleaned = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', cleaned)
    return cleaned

def _extract_key_concepts(text: str) -> List[str]:
    """Extract key concepts from text for content generation."""
    # Split into words and filter meaningful ones
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out common stop words
    stop_words = {
        'and', 'the', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
        'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
        'man', 'men', 'too', 'any', 'she', 'use', 'her', 'now', 'air', 'may', 'say', 'set', 'end', 'why', 'try'
    }
    
    concepts = [word for word in words if word not in stop_words and len(word) >= 3]
    return list(set(concepts))[:10]  # Return unique concepts, max 10

def _generate_title_variations(base_concepts: List[str], keywords: List[str], tone: str, max_length: int) -> List[str]:
    """Generate title variations using AI-inspired techniques."""
    
    # Tone-specific prefixes and patterns
    tone_patterns = {
        "professional": [
            "Professional {concept} Solutions",
            "Advanced {concept} Technology", 
            "Expert {concept} Services",
            "Premium {concept} Experience",
            "Industry-Leading {concept}"
        ],
        "casual": [
            "Amazing {concept} for Everyone",
            "Your Perfect {concept} Match",
            "Discover Great {concept}",
            "Simple {concept} Made Easy",
            "The Best {concept} Experience"
        ],
        "exciting": [
            "Revolutionary {concept}!",
            "Game-Changing {concept}",
            "Incredible {concept} Innovation",
            "Breakthrough {concept} Technology",
            "Next-Level {concept} Experience"
        ],
        "luxury": [
            "Luxury {concept} Collection",
            "Premium {concept} Experience",
            "Exclusive {concept} Selection",
            "Elite {concept} Solutions",
            "Sophisticated {concept} Design"
        ]
    }
    
    patterns = tone_patterns.get(tone, tone_patterns["professional"])
    all_concepts = base_concepts + (keywords or [])
    
    titles = []
    
    # Generate titles using patterns
    for pattern in patterns[:3]:
        for concept in all_concepts[:3]:
            title = pattern.format(concept=concept.title())
            if len(title) <= max_length:
                titles.append(title)
    
    # Generate keyword-focused titles
    if keywords:
        for keyword in keywords[:2]:
            titles.extend([
                f"Ultimate {keyword.title()} Guide",
                f"Best {keyword.title()} Solutions",
                f"Top {keyword.title()} Recommendations"
            ])
    
    # Filter by length and return unique titles
    valid_titles = [t for t in titles if len(t) <= max_length]
    return list(dict.fromkeys(valid_titles))[:5]  # Remove duplicates, max 5

def _generate_description_variations(base_concepts: List[str], keywords: List[str], tone: str, max_length: int, cta_style: str) -> List[str]:
    """Generate description variations using AI-inspired techniques."""
    
    # CTA phrases based on style
    cta_phrases = {
        "soft": ["Learn more about", "Discover how", "Explore our", "Find out more"],
        "direct": ["Get started today", "Order now", "Contact us", "Try it now"],
        "urgent": ["Don't miss out", "Limited time offer", "Act now", "While supplies last"]
    }
    
    ctas = cta_phrases.get(cta_style, cta_phrases["soft"])
    all_concepts = base_concepts + (keywords or [])
    
    descriptions = []
    
    # Base description templates by tone
    if tone == "professional":
        templates = [
            "Our {concept} solutions deliver exceptional results through innovative technology and expert service.",
            "Experience professional-grade {concept} designed to meet your specific business requirements.",
            "Trusted {concept} platform providing reliable, scalable solutions for modern enterprises."
        ]
    elif tone == "casual":
        templates = [
            "Love what you do with our amazing {concept} that makes everything easier and more fun.",
            "Great {concept} for everyone who wants simple, effective solutions that actually work.",
            "Your new favorite {concept} - designed to fit perfectly into your daily routine."
        ]
    elif tone == "exciting":
        templates = [
            "Revolutionary {concept} that's changing everything! Experience the future of innovation today.",
            "Incredible {concept} breakthrough that delivers amazing results beyond your expectations.",
            "Game-changing {concept} technology that transforms how you work and live."
        ]
    elif tone == "luxury":
        templates = [
            "Exquisite {concept} crafted with premium materials and uncompromising attention to detail.",
            "Luxury {concept} collection featuring sophisticated design and exceptional quality.",
            "Elite {concept} experience designed exclusively for discerning professionals."
        ]
    else:
        templates = [
            "Quality {concept} solutions designed to deliver outstanding performance and reliability.",
            "Innovative {concept} technology that provides effective results for your needs.",
            "Comprehensive {concept} platform offering complete solutions and support."
        ]
    
    # Generate descriptions
    for template in templates:
        for concept in all_concepts[:2]:
            base_desc = template.format(concept=concept)
            
            # Add CTA if there's space
            for cta in ctas[:2]:
                full_desc = f"{base_desc} {cta}."
                if len(full_desc) <= max_length:
                    descriptions.append(full_desc)
                    break
            else:
                # If no CTA fits, use description without CTA
                if len(base_desc) <= max_length:
                    descriptions.append(base_desc)
    
    # Filter and return unique descriptions
    valid_descriptions = [d for d in descriptions if len(d) <= max_length]
    return list(dict.fromkeys(valid_descriptions))[:3]  # Remove duplicates, max 3

@app.get("/", tags=["Health"])
def root():
    """Root endpoint for health check."""
    return {
        "service": "Optimizer AI",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/generate_title", "/generate_description"]
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "optimizer_ai"}

@app.post("/generate_title", response_model=TitleResponse, tags=["AI Generation"])
def generate_title(request: GenerateTitleRequest):
    """
    Generate AI-optimized titles for marketing copy.
    
    This endpoint uses AI-inspired algorithms to create compelling,
    keyword-optimized titles based on the input text and parameters.
    """
    try:
        logger.info(f"Generating title for text: {request.text[:50]}...")
        
        # Clean and process input
        cleaned_text = _clean_text(request.text)
        base_concepts = _extract_key_concepts(cleaned_text)
        
        # Generate title variations
        title_variations = _generate_title_variations(
            base_concepts, 
            request.keywords or [], 
            request.tone, 
            request.max_length
        )
        
        if not title_variations:
            # Fallback title generation
            main_concept = base_concepts[0] if base_concepts else "Solution"
            main_title = f"Premium {main_concept.title()} Experience"[:request.max_length]
            title_variations = [main_title]
        
        main_title = title_variations[0]
        alternatives = title_variations[1:] if len(title_variations) > 1 else []
        
        # Determine which keywords were used
        keywords_used = []
        if request.keywords:
            for keyword in request.keywords:
                if keyword.lower() in main_title.lower():
                    keywords_used.append(keyword)
        
        response = TitleResponse(
            title=main_title,
            alternatives=alternatives,
            keywords_used=keywords_used,
            length=len(main_title),
            tone=request.tone
        )
        
        logger.info(f"Generated title: {main_title}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating title: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Title generation failed: {str(e)}")

@app.post("/generate_description", response_model=DescriptionResponse, tags=["AI Generation"])
def generate_description(request: GenerateDescriptionRequest):
    """
    Generate AI-optimized descriptions for marketing copy.
    
    This endpoint uses AI-inspired algorithms to create compelling,
    keyword-optimized descriptions with appropriate calls-to-action.
    """
    try:
        logger.info(f"Generating description for text: {request.text[:50]}...")
        
        # Clean and process input
        cleaned_text = _clean_text(request.text)
        base_concepts = _extract_key_concepts(cleaned_text)
        
        # Generate description variations
        description_variations = _generate_description_variations(
            base_concepts,
            request.keywords or [],
            request.tone,
            request.max_length,
            request.cta_style
        )
        
        if not description_variations:
            # Fallback description generation
            main_concept = base_concepts[0] if base_concepts else "our product"
            main_description = f"Discover the benefits of {main_concept} with our innovative solution designed for your success."[:request.max_length]
            description_variations = [main_description]
        
        main_description = description_variations[0]
        alternatives = description_variations[1:] if len(description_variations) > 1 else []
        
        # Check if CTA was included
        cta_indicators = ["discover", "learn", "get", "try", "contact", "order", "explore", "find", "don't miss", "act now"]
        cta_included = any(indicator in main_description.lower() for indicator in cta_indicators)
        
        # Determine which keywords were used
        keywords_used = []
        if request.keywords:
            for keyword in request.keywords:
                if keyword.lower() in main_description.lower():
                    keywords_used.append(keyword)
        
        response = DescriptionResponse(
            description=main_description,
            alternatives=alternatives,
            keywords_used=keywords_used,
            length=len(main_description),
            tone=request.tone,
            cta_included=cta_included
        )
        
        logger.info(f"Generated description: {main_description[:100]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Description generation failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )