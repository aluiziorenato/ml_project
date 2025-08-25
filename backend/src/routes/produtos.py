from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from src.services.produto_service import buscar_produtos_filtrados
from src.schemas.produto import ProdutoOut
from src.auth import verificar_token

router = APIRouter()

@router.get("/api/produtos", response_model=List[ProdutoOut])
def listar_produtos(
    categoria: Optional[str] = Query(None),
    sazonalidade: Optional[str] = Query(None),
    usuario=Depends(verificar_token)
):
    filtros = {
        "categoria": categoria,
        "sazonalidade": sazonalidade,
        "usuario_id": usuario["id"]
    }
    return buscar_produtos_filtrados(filtros)
