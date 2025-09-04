"""
Módulo dedicado para funções de SEO do serviço optimizer_ai.
Inclui cálculo de score, sugestão de palavras-chave, legibilidade, etc.
"""
from typing import List, Dict, Any
import random
import textstat
from transformers import DistilBertTokenizer, DistilBertModel
import torch

# Carregamento único do modelo
_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
_model = DistilBertModel.from_pretrained('distilbert-base-uncased')

# Função para gerar embeddings de texto
def gerar_embedding(texto):
    inputs = _tokenizer(texto, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = _model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

# Função para calcular similaridade semântica entre dois textos
def similaridade_semantica(texto1, texto2):
    emb1 = gerar_embedding(texto1)
    emb2 = gerar_embedding(texto2)
    sim = float(torch.nn.functional.cosine_similarity(torch.tensor(emb1), torch.tensor(emb2), dim=0))
    return sim

# Função para sugerir termos SEO a partir de textos de referência
def sugerir_termos_seo(textos, num_termos=8):
    tokens = []
    for texto in textos:
        tokens += _tokenizer.tokenize(texto)
    termos = list(set([t for t in tokens if len(t) > 3]))
    termos_freq = sorted(termos, key=lambda x: tokens.count(x), reverse=True)
    return termos_freq[:num_termos]

# Função para validar título SEO
def validar_titulo_seo(titulo, max_len=65):
    cta = ["compre", "aproveite", "garanta", "clique", "veja", "descubra"]
    if any(word in titulo.lower() for word in cta):
        return False
    return len(titulo) <= max_len

# Score de SEO avançado
def calculate_advanced_seo_score(text: str, keywords: List[str]) -> int:
    """
    Calcula o score avançado de SEO considerando densidade de palavras-chave, estrutura de título, etc.
    """
    score = 0
    text_lower = text.lower()
    # Keyword density (25 points)
    keyword_count = sum(text_lower.count(kw.lower()) for kw in keywords)
    total_words = len(text.split())
    if total_words > 0:
        density = keyword_count / total_words
        if 0.01 <= density <= 0.03:
            score += 25
        elif density > 0:
            score += max(0, 25 - abs(density - 0.02) * 500)
    # Title structure (20 points)
    sentences = text.split('.')
    if sentences and len(sentences[0]) < 60:
        score += 20
    # Readability (20 points)
    readability = textstat.flesch_reading_ease(text)
    if readability >= 60:
        score += 20
    elif readability >= 30:
        score += 10
    # Text length (15 points)
    if 150 <= len(text) <= 300:
        score += 15
    elif 100 <= len(text) <= 500:
        score += 10
    # Call to action presence (10 points)
    cta_words = ["compre", "clique", "veja", "descubra", "aproveite", "garanta"]
    if any(cta in text_lower for cta in cta_words):
        score += 10
    # Emotional words (10 points)
    emotional_words = ["incrível", "fantástico", "exclusivo", "especial", "único", "melhor"]
    emotion_count = sum(1 for word in emotional_words if word in text_lower)
    score += min(10, emotion_count * 2)
    return min(100, score)

def calculate_seo_score(text: str, keywords: List[str]) -> int:
    """
    Calcula o score simples de SEO.
    """
    score = 50
    for keyword in keywords:
        if keyword.lower() in text.lower():
            score += 10
    word_count = len(text.split())
    if 20 <= word_count <= 60:
        score += 15
    elif word_count < 20:
        score -= 10
    if any(word.istitle() for word in text.split()):
        score += 5
    return min(100, max(0, score))

def calculate_readability_score(text: str) -> int:
    """
    Calcula o score de legibilidade do texto.
    """
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    if avg_sentence_length > 20:
        score = 60
    elif avg_sentence_length > 15:
        score = 75
    else:
        score = 85
    simple_word_bonus = sum(1 for word in text.split() if len(word) <= 6) / len(text.split()) * 15
    return min(100, int(score + simple_word_bonus))

async def suggest_keywords_ai(category: str, title: str, audience: str) -> List[Dict[str, Any]]:
    """
    Sugere palavras-chave relevantes para SEO.
    """
    category_keywords = {
        "electronics": ["smartphone", "tecnologia", "gadget", "inovação", "conectividade"],
        "clothing": ["moda", "estilo", "tendência", "conforto", "qualidade"],
        "home": ["casa", "decoração", "funcional", "design", "prático"],
        "books": ["conhecimento", "leitura", "educação", "cultura", "aprendizado"],
        "sports": ["fitness", "performance", "esporte", "saúde", "ativo"]
    }
    base_keywords = category_keywords.get(category, ["qualidade", "produto", "excelente"])
    audience_modifiers = {
        "young_adults": ["moderno", "inovador", "cool"],
        "professionals": ["profissional", "eficiente", "produtivo"],
        "families": ["seguro", "confiável", "família"],
        "seniors": ["fácil", "simples", "tradicional"]
    }
    modifiers = audience_modifiers.get(audience, ["versátil", "prático"])
    suggested = []
    for i, keyword in enumerate(base_keywords + modifiers):
        suggested.append({
            "keyword": keyword,
            "score": random.uniform(0.7, 1.0),
            "volume_estimate": random.randint(1000, 10000),
            "competition": random.choice(["low", "medium", "high"])
        })
    return suggested[:10]
