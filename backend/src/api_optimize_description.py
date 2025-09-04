from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/api/optimize-description")
async def optimize_description(request: Request):
    data = await request.json()
    title = data.get("title", "")
    instruction = data.get("instruction", "")
    # Simulação: IA de copywriting gera sugestões de descrição baseadas no título e diretiva
    # Aqui, a resposta reflete as diretrizes recebidas
    suggestions = [
        f"{title} - Anúncio otimizado para Mercado Livre. {instruction[:120]}...\n\nBenefícios: alta relevância, palavras-chave estratégicas, copy persuasivo e escaneável. Aproveite para se destacar!",
        f"{title}: Copywriting sênior aplicado. Descrição clara, organizada, com técnicas de persuasão e SEO. {instruction[:120]}...",
        f"{title} - Seu anúncio foi revisado por IA especialista, focando em conversão, escaneabilidade e diferenciação. {instruction[:120]}...",
    ]
    return JSONResponse({"suggestions": suggestions})
