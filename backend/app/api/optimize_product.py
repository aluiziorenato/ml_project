# Endpoint FastAPI para otimização integrada
from fastapi import APIRouter, Body
from app.ai.seo_intelligence import analyze_seo
from app.ai.optimizer_ai import optimize_copy

router = APIRouter()

@router.post("/api/optimize-product")
def optimize_product(
    title: str = Body(...),
    category_id: str = Body(...),
    product_data: dict = Body(...),
    selected_titles: list = Body([]),
    selected_keywords: list = Body([])
):
    # 1. Chama SEO Intelligence
    seo_result = analyze_seo(title, category_id)
    # 2. Chama Optimizer AI com seleção do usuário
    optimized = optimize_copy(selected_titles, selected_keywords, product_data)
    return {
        "seo": seo_result,
        "optimized": optimized
    }
