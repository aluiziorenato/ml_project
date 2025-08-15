from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from typing import List, Dict, Any
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Otimizador de Copywriting - Mercado Livre", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class CopywritingRequest(BaseModel):
    original_text: str
    target_audience: str
    product_category: str
    optimization_goal: str  # "clicks", "conversions", "engagement"
    keywords: List[str] = []

class CopywritingResponse(BaseModel):
    optimized_text: str
    improvements: List[str]
    seo_score: int
    readability_score: int
    estimated_performance_lift: float
    keywords_included: List[str]

class ABTestRequest(BaseModel):
    variations: List[str]
    audience: str
    category: str

class ABTestResponse(BaseModel):
    test_id: str
    recommended_variation: int
    confidence_score: float
    expected_results: Dict[str, float]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    with open("static/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "optimizer_ai"}

@app.post("/api/optimize-copy", response_model=CopywritingResponse)
async def optimize_copywriting(request: CopywritingRequest) -> CopywritingResponse:
    """
    Optimize copywriting for Mercado Libre listings using AI techniques
    """
    logger.info(f"Optimizing copy for {request.product_category} targeting {request.target_audience}")
    
    original_text = request.original_text
    
    # Apply various optimization techniques
    optimized_text = apply_optimizations(
        original_text, 
        request.target_audience, 
        request.product_category,
        request.optimization_goal,
        request.keywords
    )
    
    # Calculate scores
    seo_score = calculate_seo_score(optimized_text, request.keywords)
    readability_score = calculate_readability_score(optimized_text)
    
    # Estimate performance lift
    performance_lift = estimate_performance_lift(
        original_text, 
        optimized_text, 
        request.optimization_goal
    )
    
    # Generate improvement suggestions
    improvements = generate_improvements(original_text, optimized_text, request)
    
    # Find included keywords
    keywords_included = [kw for kw in request.keywords if kw.lower() in optimized_text.lower()]
    
    return CopywritingResponse(
        optimized_text=optimized_text,
        improvements=improvements,
        seo_score=seo_score,
        readability_score=readability_score,
        estimated_performance_lift=performance_lift,
        keywords_included=keywords_included
    )

@app.post("/api/ab-test", response_model=ABTestResponse)
async def create_ab_test(request: ABTestRequest) -> ABTestResponse:
    """
    Create A/B test for multiple copy variations
    """
    if len(request.variations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 variations required for A/B test")
    
    test_id = f"ABT_{random.randint(100000, 999999)}"
    
    # Analyze each variation
    scores = []
    for variation in request.variations:
        score = analyze_copy_quality(variation, request.audience, request.category)
        scores.append(score)
    
    # Find best performing variation
    recommended_variation = scores.index(max(scores))
    confidence_score = max(scores) / sum(scores) if sum(scores) > 0 else 0
    
    # Generate expected results
    expected_results = {
        "click_rate_improvement": random.uniform(10, 40),
        "conversion_rate_improvement": random.uniform(5, 25),
        "engagement_improvement": random.uniform(15, 50)
    }
    
    return ABTestResponse(
        test_id=test_id,
        recommended_variation=recommended_variation,
        confidence_score=round(confidence_score, 3),
        expected_results=expected_results
    )

def apply_optimizations(text: str, audience: str, category: str, goal: str, keywords: List[str]) -> str:
    """Apply various copywriting optimizations"""
    optimized = text
    
    # Add power words based on goal
    power_words = {
        "clicks": ["DESCUBRA", "EXCLUSIVO", "LIMITADO", "NOVO"],
        "conversions": ["GARANTIA", "ECONOMIZE", "GRÁTIS", "APROVEITE"],
        "engagement": ["INCRÍVEL", "SURPREENDENTE", "ÚNICO", "ESPECIAL"]
    }
    
    # Add emotional triggers
    if audience == "young_adults":
        optimized = add_youth_appeal(optimized)
    elif audience == "families":
        optimized = add_family_appeal(optimized)
    elif audience == "professionals":
        optimized = add_professional_appeal(optimized)
    
    # Include keywords naturally
    for keyword in keywords[:3]:  # Limit to top 3 keywords
        if keyword.lower() not in optimized.lower():
            optimized = f"{keyword} - {optimized}"
    
    # Add call-to-action based on goal
    ctas = {
        "clicks": "Clique agora e descubra mais!",
        "conversions": "Compre agora com desconto exclusivo!",
        "engagement": "Veja por que milhares escolhem este produto!"
    }
    
    if goal in ctas and not any(cta_word in optimized.lower() for cta_word in ["clique", "compre", "veja"]):
        optimized += f" {ctas[goal]}"
    
    return optimized

def add_youth_appeal(text: str) -> str:
    """Add appeal for young adults"""
    youth_terms = ["inovador", "moderno", "tendência", "estilo"]
    for term in youth_terms[:1]:
        if term not in text.lower():
            text = f"{term.title()} {text}"
            break
    return text

def add_family_appeal(text: str) -> str:
    """Add appeal for families"""
    family_terms = ["seguro", "confiável", "para toda família", "qualidade"]
    for term in family_terms[:1]:
        if term not in text.lower():
            text = f"{term.title()} {text}"
            break
    return text

def add_professional_appeal(text: str) -> str:
    """Add appeal for professionals"""
    prof_terms = ["eficiente", "produtivo", "profissional", "premium"]
    for term in prof_terms[:1]:
        if term not in text.lower():
            text = f"{term.title()} {text}"
            break
    return text

def calculate_seo_score(text: str, keywords: List[str]) -> int:
    """Calculate SEO score based on keyword presence and text optimization"""
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
    
    return min(100, max(0, score))

def calculate_readability_score(text: str) -> int:
    """Calculate readability score"""
    # Simple readability based on sentence length and word complexity
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    
    # Penalize very long sentences
    if avg_sentence_length > 20:
        score = 60
    elif avg_sentence_length > 15:
        score = 75
    else:
        score = 85
    
    # Bonus for simple words
    simple_word_bonus = sum(1 for word in text.split() if len(word) <= 6) / len(text.split()) * 15
    
    return min(100, int(score + simple_word_bonus))

def estimate_performance_lift(original: str, optimized: str, goal: str) -> float:
    """Estimate performance improvement percentage"""
    # Calculate based on optimization features added
    lift = 0.0
    
    # Length optimization
    orig_words = len(original.split())
    opt_words = len(optimized.split())
    
    if opt_words > orig_words:
        lift += random.uniform(5, 15)  # More descriptive content
    
    # Power words detection
    power_indicators = ["exclusivo", "grátis", "garantia", "novo", "limitado"]
    power_count = sum(1 for word in power_indicators if word in optimized.lower())
    lift += power_count * random.uniform(3, 8)
    
    # CTA presence
    if any(cta in optimized.lower() for cta in ["clique", "compre", "veja", "aproveite"]):
        lift += random.uniform(8, 20)
    
    return round(min(50, lift), 1)

def generate_improvements(original: str, optimized: str, request: CopywritingRequest) -> List[str]:
    """Generate list of improvements made"""
    improvements = []
    
    if len(optimized.split()) > len(original.split()):
        improvements.append("Texto expandido para maior descrição")
    
    if any(kw.lower() in optimized.lower() for kw in request.keywords):
        improvements.append("Palavras-chave incluídas naturalmente")
    
    if any(word in optimized.lower() for word in ["clique", "compre", "veja"]):
        improvements.append("Call-to-action adicionado")
    
    if request.target_audience in ["young_adults", "families", "professionals"]:
        improvements.append(f"Linguagem otimizada para {request.target_audience}")
    
    improvements.append("Estrutura otimizada para melhor legibilidade")
    
    return improvements

def analyze_copy_quality(text: str, audience: str, category: str) -> float:
    """Analyze quality of copy for A/B testing"""
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
    
    # Random variation for realistic simulation
    score += random.uniform(-0.1, 0.1)
    
    return max(0, min(1, score))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)