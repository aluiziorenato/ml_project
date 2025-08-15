from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime, timedelta
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Otimizador de Copywriting - Mercado Livre", 
    version="1.0.0",
    description="API para otimização de copywriting e gerenciamento de testes A/B",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if directory exists
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for demo purposes (in production, use a database)
ab_tests_storage = {}
copy_optimizations = {}
templates_storage = {}

class CopywritingRequest(BaseModel):
    original_text: str
    target_audience: str
    product_category: str
    optimization_goal: str  # "clicks", "conversions", "engagement"
    keywords: List[str] = []

class CopywritingResponse(BaseModel):
    optimization_id: str
    optimized_text: str
    improvements: List[str]
    seo_score: int
    readability_score: int
    estimated_performance_lift: float
    keywords_included: List[str]
    created_at: str

class ABTestRequest(BaseModel):
    name: str
    variations: List[str]
    audience: str
    category: str
    traffic_allocation: float = 1.0  # Percentage of traffic to include
    duration_days: int = 7

class ABTestResponse(BaseModel):
    test_id: str
    name: str
    status: str  # "draft", "running", "completed", "stopped"
    variations: List[Dict[str, Any]]
    traffic_allocation: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_days: int
    results: Dict[str, Any] = {}
    winner: Optional[int] = None
    confidence_level: Optional[float] = None
    created_at: str

class ABTestUpdateRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    traffic_allocation: Optional[float] = None
    duration_days: Optional[int] = None

class ABTestResultsResponse(BaseModel):
    test_id: str
    status: str
    results: Dict[str, Any]
    winner: Optional[int]
    confidence_level: Optional[float]
    statistical_significance: bool
    recommendations: List[str]

class TemplateRequest(BaseModel):
    name: str
    description: str
    category: str
    template_text: str
    variables: List[str] = []
    tags: List[str] = []

class TemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str
    category: str
    template_text: str
    variables: List[str]
    tags: List[str]
    usage_count: int
    created_at: str
    updated_at: str

class TemplateGenerateRequest(BaseModel):
    template_id: str
    variables: Dict[str, str]

class BatchOptimizationRequest(BaseModel):
    texts: List[str]
    target_audience: str
    product_category: str
    optimization_goal: str
    keywords: List[str] = []

class ABTestListResponse(BaseModel):
    tests: List[ABTestResponse]
    total: int
    page: int
    per_page: int

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Optimizer AI Service</h1><p>API available at /docs</p>")

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
    
    optimization_id = f"OPT_{str(uuid.uuid4())[:8].upper()}"
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
    
    # Create response
    response = CopywritingResponse(
        optimization_id=optimization_id,
        optimized_text=optimized_text,
        improvements=improvements,
        seo_score=seo_score,
        readability_score=readability_score,
        estimated_performance_lift=performance_lift,
        keywords_included=keywords_included,
        created_at=datetime.now().isoformat()
    )
    
    # Store the optimization
    copy_optimizations[optimization_id] = {
        "request": request,
        "response": response,
        "created_at": datetime.now().isoformat()
    }
    
    return response

@app.post("/api/ab-test", response_model=ABTestResponse)
async def create_ab_test(request: ABTestRequest) -> ABTestResponse:
    """
    Create A/B test for multiple copy variations
    """
    if len(request.variations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 variations required for A/B test")
    
    if not (0 < request.traffic_allocation <= 1.0):
        raise HTTPException(status_code=400, detail="Traffic allocation must be between 0 and 1")
    
    test_id = f"ABT_{str(uuid.uuid4())[:8].upper()}"
    
    # Create variations with metadata
    variations = []
    for i, variation_text in enumerate(request.variations):
        score = analyze_copy_quality(variation_text, request.audience, request.category)
        variations.append({
            "id": i,
            "text": variation_text,
            "quality_score": score,
            "traffic_weight": 1.0 / len(request.variations),  # Equal distribution initially
            "metrics": {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "click_rate": 0.0,
                "conversion_rate": 0.0
            }
        })
    
    # Create A/B test
    ab_test = ABTestResponse(
        test_id=test_id,
        name=request.name,
        status="draft",
        variations=variations,
        traffic_allocation=request.traffic_allocation,
        start_date=None,
        end_date=None,
        duration_days=request.duration_days,
        results={},
        winner=None,
        confidence_level=None,
        created_at=datetime.now().isoformat()
    )
    
    # Store the test
    ab_tests_storage[test_id] = {
        "request": request,
        "response": ab_test,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    logger.info(f"Created A/B test {test_id}: {request.name}")
    
    return ab_test

@app.get("/api/ab-tests", response_model=ABTestListResponse)
async def list_ab_tests(page: int = 1, per_page: int = 10, status: Optional[str] = None):
    """List all A/B tests with pagination and optional status filter"""
    tests = [test_data["response"] for test_data in ab_tests_storage.values()]
    
    # Filter by status
    if status:
        tests = [t for t in tests if t.status == status]
    
    total = len(tests)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_tests = tests[start_idx:end_idx]
    
    return ABTestListResponse(
        tests=paginated_tests,
        total=total,
        page=page,
        per_page=per_page
    )

@app.get("/api/ab-tests/{test_id}", response_model=ABTestResponse)
async def get_ab_test(test_id: str):
    """Get A/B test details"""
    if test_id not in ab_tests_storage:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    return ab_tests_storage[test_id]["response"]

@app.put("/api/ab-tests/{test_id}", response_model=ABTestResponse)
async def update_ab_test(test_id: str, updates: ABTestUpdateRequest):
    """Update A/B test configuration"""
    if test_id not in ab_tests_storage:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    test_data = ab_tests_storage[test_id]
    ab_test = test_data["response"]
    
    # Update allowed fields
    updated_fields = updates.dict(exclude_unset=True)
    
    for field, value in updated_fields.items():
        if hasattr(ab_test, field):
            setattr(ab_test, field, value)
    
    test_data["updated_at"] = datetime.now().isoformat()
    ab_tests_storage[test_id] = test_data
    
    return ab_test

@app.post("/api/ab-tests/{test_id}/start")
async def start_ab_test(test_id: str):
    """Start an A/B test"""
    if test_id not in ab_tests_storage:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    test_data = ab_tests_storage[test_id]
    ab_test = test_data["response"]
    
    if ab_test.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft tests can be started")
    
    ab_test.status = "running"
    ab_test.start_date = datetime.now().isoformat()
    ab_test.end_date = (datetime.now() + timedelta(days=ab_test.duration_days)).isoformat()
    
    test_data["updated_at"] = datetime.now().isoformat()
    ab_tests_storage[test_id] = test_data
    
    return {"message": f"A/B test {test_id} started successfully"}

@app.post("/api/ab-tests/{test_id}/stop")
async def stop_ab_test(test_id: str):
    """Stop a running A/B test"""
    if test_id not in ab_tests_storage:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    test_data = ab_tests_storage[test_id]
    ab_test = test_data["response"]
    
    if ab_test.status != "running":
        raise HTTPException(status_code=400, detail="Only running tests can be stopped")
    
    ab_test.status = "stopped"
    ab_test.end_date = datetime.now().isoformat()
    
    test_data["updated_at"] = datetime.now().isoformat()
    ab_tests_storage[test_id] = test_data
    
    return {"message": f"A/B test {test_id} stopped successfully"}

@app.get("/api/ab-tests/{test_id}/results", response_model=ABTestResultsResponse)
async def get_ab_test_results(test_id: str):
    """Get A/B test results and analysis"""
    if test_id not in ab_tests_storage:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    test_data = ab_tests_storage[test_id]
    ab_test = test_data["response"]
    
    # Simulate test results for demo (in real implementation, this would come from analytics)
    if ab_test.status in ["running", "completed", "stopped"]:
        # Generate simulated metrics for each variation
        for i, variation in enumerate(ab_test.variations):
            base_impressions = random.randint(1000, 5000)
            click_rate = random.uniform(0.02, 0.08)
            conversion_rate = random.uniform(0.01, 0.05)
            
            variation["metrics"]["impressions"] = base_impressions
            variation["metrics"]["clicks"] = int(base_impressions * click_rate)
            variation["metrics"]["conversions"] = int(variation["metrics"]["clicks"] * conversion_rate)
            variation["metrics"]["click_rate"] = round(click_rate, 4)
            variation["metrics"]["conversion_rate"] = round(conversion_rate, 4)
        
        # Determine winner (highest conversion rate)
        best_variation = max(ab_test.variations, key=lambda v: v["metrics"]["conversion_rate"])
        winner_index = best_variation["id"]
        
        # Calculate confidence level (simplified)
        confidence_level = random.uniform(0.85, 0.99)
        statistical_significance = confidence_level > 0.95
        
        # Generate recommendations
        recommendations = []
        if statistical_significance:
            recommendations.append(f"Variation {winner_index} is the clear winner with {confidence_level:.1%} confidence")
            recommendations.append("Implement the winning variation for best results")
        else:
            recommendations.append("Results are not statistically significant yet")
            recommendations.append("Consider running the test longer for more reliable results")
        
        if best_variation["metrics"]["click_rate"] > 0.05:
            recommendations.append("High click rate indicates strong copy appeal")
        
        ab_test.winner = winner_index
        ab_test.confidence_level = confidence_level
        
        if ab_test.status == "running" and datetime.now() > datetime.fromisoformat(ab_test.end_date.replace('Z', '+00:00')):
            ab_test.status = "completed"
        
        results = {
            "variations": ab_test.variations,
            "winner": winner_index,
            "confidence_level": confidence_level,
            "total_impressions": sum(v["metrics"]["impressions"] for v in ab_test.variations),
            "total_clicks": sum(v["metrics"]["clicks"] for v in ab_test.variations),
            "total_conversions": sum(v["metrics"]["conversions"] for v in ab_test.variations)
        }
        
        return ABTestResultsResponse(
            test_id=test_id,
            status=ab_test.status,
            results=results,
            winner=winner_index,
            confidence_level=confidence_level,
            statistical_significance=statistical_significance,
            recommendations=recommendations
        )
    
    else:
        return ABTestResultsResponse(
            test_id=test_id,
            status=ab_test.status,
            results={},
            winner=None,
            confidence_level=None,
            statistical_significance=False,
            recommendations=["Test has not been started yet"]
        )

@app.delete("/api/ab-tests/{test_id}")
async def delete_ab_test(test_id: str):
    """Delete an A/B test"""
    if test_id not in ab_tests_storage:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    test_data = ab_tests_storage[test_id]
    ab_test = test_data["response"]
    
    if ab_test.status == "running":
        raise HTTPException(status_code=400, detail="Cannot delete running test. Stop it first.")
    
    del ab_tests_storage[test_id]
    return {"message": f"A/B test {test_id} deleted successfully"}

# Template Management Endpoints

@app.post("/api/templates", response_model=TemplateResponse)
async def create_template(request: TemplateRequest):
    """Create a new copywriting template"""
    template_id = f"TPL_{str(uuid.uuid4())[:8].upper()}"
    
    template = TemplateResponse(
        template_id=template_id,
        name=request.name,
        description=request.description,
        category=request.category,
        template_text=request.template_text,
        variables=request.variables,
        tags=request.tags,
        usage_count=0,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    templates_storage[template_id] = template
    logger.info(f"Created template {template_id}: {request.name}")
    
    return template

@app.get("/api/templates", response_model=List[TemplateResponse])
async def list_templates(category: Optional[str] = None, tag: Optional[str] = None):
    """List all templates with optional filters"""
    templates = list(templates_storage.values())
    
    if category:
        templates = [t for t in templates if t.category == category]
    
    if tag:
        templates = [t for t in templates if tag in t.tags]
    
    return templates

@app.get("/api/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific template"""
    if template_id not in templates_storage:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return templates_storage[template_id]

@app.post("/api/templates/{template_id}/generate", response_model=CopywritingResponse)
async def generate_from_template(template_id: str, request: TemplateGenerateRequest):
    """Generate copy from a template"""
    if template_id not in templates_storage:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if request.template_id != template_id:
        raise HTTPException(status_code=400, detail="Template ID mismatch")
    
    template = templates_storage[template_id]
    
    # Replace variables in template
    generated_text = template.template_text
    for var_name, var_value in request.variables.items():
        placeholder = f"{{{var_name}}}"
        generated_text = generated_text.replace(placeholder, var_value)
    
    # Check for unreplaced variables
    import re
    unreplaced = re.findall(r'\{(\w+)\}', generated_text)
    if unreplaced:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing values for variables: {', '.join(unreplaced)}"
        )
    
    # Update usage count
    template.usage_count += 1
    template.updated_at = datetime.now().isoformat()
    templates_storage[template_id] = template
    
    # Generate optimization response
    optimization_id = f"OPT_{str(uuid.uuid4())[:8].upper()}"
    
    response = CopywritingResponse(
        optimization_id=optimization_id,
        optimized_text=generated_text,
        improvements=["Generated from template", f"Used template: {template.name}"],
        seo_score=calculate_seo_score(generated_text, []),
        readability_score=calculate_readability_score(generated_text),
        estimated_performance_lift=random.uniform(5, 15),
        keywords_included=[],
        created_at=datetime.now().isoformat()
    )
    
    return response

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    if template_id not in templates_storage:
        raise HTTPException(status_code=404, detail="Template not found")
    
    del templates_storage[template_id]
    return {"message": f"Template {template_id} deleted successfully"}

# Batch Processing Endpoints

@app.post("/api/optimize-batch", response_model=List[CopywritingResponse])
async def optimize_batch(request: BatchOptimizationRequest):
    """Optimize multiple texts in batch"""
    if len(request.texts) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 texts allowed per batch")
    
    results = []
    for text in request.texts:
        # Create individual optimization request
        individual_request = CopywritingRequest(
            original_text=text,
            target_audience=request.target_audience,
            product_category=request.product_category,
            optimization_goal=request.optimization_goal,
            keywords=request.keywords
        )
        
        # Optimize the text
        optimization = await optimize_copywriting(individual_request)
        results.append(optimization)
    
    return results

# Analytics and Stats Endpoints

@app.get("/api/optimizations/{optimization_id}")
async def get_optimization(optimization_id: str):
    """Get a specific optimization result"""
    if optimization_id not in copy_optimizations:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    return copy_optimizations[optimization_id]["response"]

@app.get("/api/stats/optimizations")
async def get_optimization_stats():
    """Get optimization statistics"""
    if not copy_optimizations:
        return {
            "total_optimizations": 0,
            "avg_seo_score": 0,
            "avg_readability_score": 0,
            "avg_performance_lift": 0,
            "popular_goals": {},
            "popular_categories": {}
        }
    
    optimizations = [opt["response"] for opt in copy_optimizations.values()]
    
    avg_seo = sum(opt.seo_score for opt in optimizations) / len(optimizations)
    avg_readability = sum(opt.readability_score for opt in optimizations) / len(optimizations)
    avg_lift = sum(opt.estimated_performance_lift for opt in optimizations) / len(optimizations)
    
    # Count popular goals and categories
    goals = {}
    categories = {}
    
    for opt_data in copy_optimizations.values():
        goal = opt_data["request"].optimization_goal
        category = opt_data["request"].product_category
        
        goals[goal] = goals.get(goal, 0) + 1
        categories[category] = categories.get(category, 0) + 1
    
    return {
        "total_optimizations": len(optimizations),
        "avg_seo_score": round(avg_seo, 1),
        "avg_readability_score": round(avg_readability, 1),
        "avg_performance_lift": round(avg_lift, 1),
        "popular_goals": goals,
        "popular_categories": categories
    }

@app.get("/api/stats/ab-tests")
async def get_ab_test_stats():
    """Get A/B test statistics"""
    if not ab_tests_storage:
        return {
            "total_tests": 0,
            "running_tests": 0,
            "completed_tests": 0,
            "avg_confidence": 0,
            "test_statuses": {}
        }
    
    tests = [test_data["response"] for test_data in ab_tests_storage.values()]
    
    running_tests = sum(1 for test in tests if test.status == "running")
    completed_tests = sum(1 for test in tests if test.status == "completed")
    
    # Calculate average confidence for completed tests
    completed_with_confidence = [test for test in tests if test.confidence_level is not None]
    avg_confidence = sum(test.confidence_level for test in completed_with_confidence) / max(len(completed_with_confidence), 1)
    
    # Count test statuses
    statuses = {}
    for test in tests:
        statuses[test.status] = statuses.get(test.status, 0) + 1
    
    return {
        "total_tests": len(tests),
        "running_tests": running_tests,
        "completed_tests": completed_tests,
        "avg_confidence": round(avg_confidence, 3),
        "test_statuses": statuses
    }

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