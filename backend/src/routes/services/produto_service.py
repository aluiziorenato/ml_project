from src.models.produto import Produto

def buscar_produtos_filtrados(filtros: dict):
    query = Produto.select()

    if filtros.get("categoria"):
        query = query.where(Produto.categoria == filtros["categoria"])

    if filtros.get("sazonalidade"):
        query = query.where(Produto.sazonalidade == filtros["sazonalidade"])

    query = query.where(Produto.usuario_id == filtros["usuario_id"])

    produtos = query.execute()

    # Adiciona tags inteligentes
    for p in produtos:
        p.demandaAlta = p.vendas > 1000
        p.baixaConcorrencia = p.concorrentes < 5

    return produtos
