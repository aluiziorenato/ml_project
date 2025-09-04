from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import api_endpoints, api_tests, oauth, auth, proxy, seo, categories, anuncios, meli_services_router, metrics, campaigns, promotions, products
from .config import settings
from app.routers import meli_routes
from app.startup import create_admin_user
from app.monitoring.sentry_config import init_sentry
from app.monitoring.middleware import MonitoringMiddleware
from src.api_optimize_description import router as optimize_description_router
import logging

# Initialize Sentry before other imports
init_sentry()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI(
    title="ML Integration Backend - Mercado Livre Automation",
    description="""
    Sistema integrado de automação para vendas no Mercado Livre com IA e Machine Learning.
    
    ## Funcionalidades
    
    * **Autenticação JWT** - Sistema seguro de autenticação com tokens JWT
    * **Integração Mercado Livre** - OAuth2 e APIs oficiais do Mercado Livre
    * **Gerenciamento de Produtos** - CRUD completo de produtos
    * **SEO e Otimização** - Ferramentas para otimização de anúncios
    * **Testes Automatizados** - Suite completa de testes
    
    ## Segurança
    
    A API utiliza autenticação JWT. Para endpoints protegidos, inclua o header:
    `Authorization: Bearer <seu_token>`
    """,
    version="2.0.0",
    terms_of_service="https://github.com/aluiziorenato/ml_project",
    contact={
        "name": "ML Project Team",
        "url": "https://github.com/aluiziorenato/ml_project",
        "email": "contato@mlproject.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operações de autenticação e autorização"
        },
        {
            "name": "Mercado Livre",
            "description": "Integração com APIs do Mercado Livre"
        },
        {
            "name": "Products",
            "description": "Gerenciamento de produtos"
        },
        {
            "name": "SEO",
            "description": "Otimização e SEO"
        },
        {
            "name": "Testing",
            "description": "Testes e validações"
        },
        {
            "name": "Health",
            "description": "Health checks e monitoramento"
        },
        {
            "name": "Metrics",
            "description": "Métricas Prometheus e monitoramento do sistema"
        }
    ]
)
app.include_router(auth.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Rotas
app.include_router(meli_routes.router, prefix="/meli", tags=["Mercado Livre"])
app.include_router(meli_services_router.router, prefix="/meli", tags=["Mercado Livre Services"])
app.include_router(auth.router)  # aqui ele já traz o prefix="/api/auth"
app.include_router(api_endpoints.router)
app.include_router(api_tests.router)
app.include_router(oauth.router)
app.include_router(proxy.router)
app.include_router(seo.router)
app.include_router(categories.router)
app.include_router(anuncios.router)
app.include_router(optimize_description_router)

# Novos endpoints de campanhas, promoções e produtos
app.include_router(campaigns.router, prefix="/api", tags=["Campaigns"])
app.include_router(promotions.router, prefix="/api", tags=["Promotions"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(metrics.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.on_event("startup")
def startup_event():
    create_admin_user()
    
@app.get("/health")
def health():
    return {"status": "ok"}
