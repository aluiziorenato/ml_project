from pydantic import BaseModel

class ProdutoOut(BaseModel):
    id: int
    nome: str
    categoria: str
    sazonalidade: str
    vendas: int
    concorrentes: int
    demandaAlta: bool = False
    baixaConcorrencia: bool = False
