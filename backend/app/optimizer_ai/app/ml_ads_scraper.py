import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
import spacy

BASE_URL = "https://lista.mercadolivre.com.br/"
nlp = spacy.load("pt_core_news_lg")


def get_top_ads(search_term: str, max_ads: int = 100) -> List[Dict[str, str]]:
    """
    Raspagem real dos anúncios mais bem posicionados usando o termo digitado no título.
    Filtra anúncios patrocinados, em promoção e lojas oficiais.
    Calcula similaridade semântica com NLP e prioriza anúncios mais relevantes.
    Retorna lista de dicts: {titulo, descricao, url, preco, vendas, avaliacao, relevancia}
    """
    ads = []
    try:
        search_url = f"{BASE_URL}{search_term.replace(' ', '-')}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ads
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("li", {"class": "ui-search-layout__item"}, limit=max_ads*2)
        for item in items:
            # Filtra patrocinados
            if item.find(class_="ui-search-item__group__element--ad"):
                continue
            # Filtra lojas oficiais
            loja_oficial = item.find("span", string=lambda t: t and "Loja oficial" in t)
            if loja_oficial:
                continue
            # Filtra promoções
            promocao = item.find("span", string=lambda t: t and ("Promoção" in t or "Desconto" in t or "Oferta" in t))
            if promocao:
                continue
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            url = link_tag["href"]
            title = link_tag.get_text(strip=True)
            # Raspagem da página do anúncio para pegar descrição, preço, vendas, avaliação, reputação, frete, fotos, medalhas
            try:
                prod_resp = requests.get(url, headers=headers, timeout=10)
                if prod_resp.status_code != 200:
                    continue
                prod_soup = BeautifulSoup(prod_resp.text, "html.parser")
                desc_tag = prod_soup.find("p", {"class": "ui-pdp-description__content"})
                descricao = desc_tag.get_text(strip=True) if desc_tag else ""
                preco_tag = prod_soup.find("span", {"class": re.compile(r"price-tag-fraction|ui-pdp-price__second-line")})
                preco = preco_tag.get_text(strip=True) if preco_tag else ""
                vendas_tag = prod_soup.find("span", string=lambda t: t and "vendidos" in t)
                vendas = vendas_tag.get_text(strip=True) if vendas_tag else ""
                avaliacao_tag = prod_soup.find("span", {"class": "ui-pdp-review__rating"})
                avaliacao = avaliacao_tag.get_text(strip=True) if avaliacao_tag else ""
                reputacao_tag = prod_soup.find("span", {"class": "ui-pdp-seller__status__title"})
                reputacao_vendedor = reputacao_tag.get_text(strip=True) if reputacao_tag else ""
                frete_tag = prod_soup.find("p", string=lambda t: t and "Frete grátis" in t)
                frete_gratis = bool(frete_tag)
                fotos = prod_soup.find_all("img", {"class": "ui-pdp-gallery__figure__image"})
                num_fotos = len(fotos)
                medalhas_tag = prod_soup.find("span", {"class": "ui-pdp-seller__medal"})
                medalhas = medalhas_tag.get_text(strip=True) if medalhas_tag else ""
            except Exception:
                descricao = ""
                preco = ""
                vendas = ""
                avaliacao = ""
                reputacao_vendedor = ""
                frete_gratis = False
                num_fotos = 0
                medalhas = ""
            # Similaridade semântica com NLP
            doc_user = nlp(search_term)
            doc_title = nlp(title)
            doc_desc = nlp(descricao)
            sim_title = doc_user.similarity(doc_title)
            sim_desc = doc_user.similarity(doc_desc)
            relevancia = round((sim_title + sim_desc) / 2, 3)
            # Score composto
            score = (
                relevancia * 0.4 +
                (float(vendas.replace(' vendidos', '').replace('.', '').replace(',', '.')) if vendas else 0) * 0.2 +
                (float(avaliacao.replace(',', '.')[:3]) if avaliacao else 0) * 0.1 +
                (1 if frete_gratis else 0) * 0.1 +
                num_fotos * 0.05 +
                (1 if reputacao_vendedor else 0) * 0.1
            )
            ads.append({
                "titulo": title,
                "descricao": descricao,
                "url": url,
                "preco": preco,
                "vendas": vendas,
                "avaliacao": avaliacao,
                "relevancia": relevancia,
                "reputacao_vendedor": reputacao_vendedor,
                "frete_gratis": frete_gratis,
                "num_fotos": num_fotos,
                "medalhas": medalhas,
                "score": round(score, 3)
            })
            if len(ads) >= max_ads:
                break
        # Ordena por score composto
        ads = sorted(ads, key=lambda x: x["score"], reverse=True)
        return ads[:max_ads]
    except Exception:
        return ads


def get_autocomplete_terms(search_term: str) -> List[str]:
    """
    Raspagem dos termos sugeridos pelo autocomplete do Mercado Livre para a palavra-chave digitada.
    """
    try:
        # O autocomplete do ML é carregado via JS, mas existe uma API pública não documentada:
        # https://api.mercadolibre.com/sites/MLB/autocomplete?limit=10&q=termo
        api_url = f"https://api.mercadolibre.com/sites/MLB/autocomplete?limit=10&q={search_term}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(api_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        terms = [item["q"] for item in data.get("results", []) if "q" in item]
        return terms
    except Exception:
        return []


def get_best_terms_and_ads(search_term: str, max_ads: int = 100) -> Dict[str, List]:
    """
    Busca termos do autocomplete, testa cada termo, coleta anúncios e calcula relevância/SIS.
    Retorna os melhores termos e anúncios para a IA em uma única chamada.
    """
    termos = get_autocomplete_terms(search_term)
    if not termos:
        termos = [search_term]
    resultados = []
    for termo in termos:
        anuncios = get_top_ads(termo, max_ads=max_ads//len(termos) if len(termos) > 0 else max_ads)
        # Calcula relevância média dos anúncios para o termo
        relevancias = [ad["relevancia"] for ad in anuncios]
        media_relevancia = round(sum(relevancias)/len(relevancias), 3) if relevancias else 0
        resultados.append({
            "termo": termo,
            "media_relevancia": media_relevancia,
            "anuncios": anuncios
        })
    # Ordena termos por relevância média
    resultados = sorted(resultados, key=lambda x: x["media_relevancia"], reverse=True)
    return {
        "melhores_termos": [r["termo"] for r in resultados[:5]],
        "resultados": resultados[:5]  # Top 5 termos e seus anúncios
    }
