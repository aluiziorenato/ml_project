from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import random
from typing import List, Dict, Any, Optional
import logging
import re
import httpx
import json
from datetime import datetime
import asyncio
import textstat
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import spacy
    nlp = spacy.load("pt_core_news_sm")
except:
    nlp = None
    logger.warning("Spacy Portuguese model not found. Install with: python -m spacy download pt_core_news_sm")

from app.optimizer_ai.services.seo import *

app = FastAPI(
    title="Otimizador de Copywriting AI - Mercado Livre",
    description="""
    Sistema avançado de otimização de copywriting com IA para Mercado Livre.
    ## Funcionalidades Avançadas
    * **Personalização por Segmento** - Adaptação automática para diferentes audiências
    * **Teste Automático via Simulador** - Integração com o simulador para validação
    * **Sugestão de Palavras-chave** - Geração inteligente baseada em ML
    * **Validação de Compliance** - Verificação automática das regras do Mercado Livre
    * **Análise SEO Avançada** - Score detalhado e otimizações específicas
    * **Análise de Sentimento** - Avaliação emocional do texto
    * **Detecção de Plágio** - Verificação de originalidade
    ## Segmentos Suportados
    * B2B (Business to Business)
    * B2C Premium
    * B2C Popular  
    * Millennials
    * Gen Z
    * Família
    * Profissionais
    """,
    version="2.0.0",
    contact={
        "name": "ML Project - Optimizer Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Optimization", "description": "Otimização de textos e copywriting"},
        {"name": "Segmentation", "description": "Personalização por segmento"},
        {"name": "Testing", "description": "Testes automáticos e validação"},
        {"name": "Keywords", "description": "Sugestão e análise de palavras-chave"},
        {"name": "Compliance", "description": "Validação de compliance"},
        {"name": "Analytics", "description": "Analytics e métricas"},
        {"name": "Health", "description": "Health checks e monitoramento"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ...continuação do código original, incluindo modelos, endpoints e lógica...
