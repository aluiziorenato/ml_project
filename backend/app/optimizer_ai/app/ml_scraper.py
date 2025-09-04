import requests
from bs4 import BeautifulSoup

BASE_URL = "https://lista.mercadolivre.com.br/"


def get_ml_category(title: str) -> str:
    """
    Realiza busca no Mercado Livre pelo título e retorna a categoria do primeiro resultado.
    Se não encontrar, retorna uma categoria de teste válida (pai > subcategoria).
    """
    try:
        search_url = f"{BASE_URL}{title.replace(' ', '-')}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Eletrônicos > Fones de Ouvido"
        soup = BeautifulSoup(response.text, "html.parser")
        # Tenta encontrar o link do primeiro produto
        first_item = soup.find("li", {"class": "ui-search-layout__item"})
        if not first_item:
            return "Eletrônicos > Fones de Ouvido"
        product_link = first_item.find("a", href=True)
        if not product_link:
            return "Eletrônicos > Fones de Ouvido"
        # Acessa a página do produto para extrair a categoria
        prod_resp = requests.get(product_link["href"], headers=headers, timeout=10)
        if prod_resp.status_code != 200:
            return "Eletrônicos > Fones de Ouvido"
        prod_soup = BeautifulSoup(prod_resp.text, "html.parser")
        # Categoria geralmente está em breadcrumbs
        breadcrumb = prod_soup.find("ul", {"class": "andes-breadcrumb__list"})
        if breadcrumb:
            categories = [li.get_text(strip=True) for li in breadcrumb.find_all("li")]
            if len(categories) >= 2:
                return f"{categories[-2]} > {categories[-1]}"
            elif categories:
                return categories[-1]
        return "Eletrônicos > Fones de Ouvido"
    except Exception as e:
        return "Eletrônicos > Fones de Ouvido"
