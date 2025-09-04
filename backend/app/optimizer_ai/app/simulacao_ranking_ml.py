import json
from ml_ads_scraper import get_top_ads

TERMO = "roupa social infantil"
MAX_ADS = 10

ads = get_top_ads(TERMO, max_ads=MAX_ADS)

print(f"Simulação de ranqueamento Mercado Livre para o termo: '{TERMO}'\n")
for i, ad in enumerate(ads, 1):
    print(f"#{i} - Score: {ad['score']} | Relevância: {ad['relevancia']} | Vendas: {ad['vendas']} | Avaliação: {ad['avaliacao']} | Frete grátis: {ad['frete_gratis']} | Reputação: {ad['reputacao_vendedor']} | Fotos: {ad['num_fotos']} | Medalhas: {ad['medalhas']}")
    print(f"Título: {ad['titulo']}")
    print(f"URL: {ad['url']}")
    print("---")

# Salva os dados em JSON para análise posterior
with open("simulacao_ads.json", "w", encoding="utf-8") as f:
    json.dump(ads, f, ensure_ascii=False, indent=2)

print("\nArquivo 'simulacao_ads.json' gerado com os dados completos dos anúncios.")
