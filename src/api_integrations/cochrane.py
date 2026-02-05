# src/api_integrations/cochrane.py

import requests
from bs4 import BeautifulSoup

def buscar_cochrane(query, max_results=20):
    """
    Busca revisões sistemáticas na Cochrane Library.
    Retorna uma lista de dicionários padronizados (título, resumo, link, etc.).
    """
    # Monta a URL de busca
    base_url = "https://www.cochranelibrary.com"
    search_url = f"{base_url}/search"
    params = {"text": query, "pageSize": max_results}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(search_url, params=params, headers=headers, timeout=20)
    if response.status_code != 200:
        print("Cochrane search failed:", response.status_code)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    for result in soup.find_all("div", class_="search-results-item"):
        title_tag = result.find("a", class_="result-title")
        title = title_tag.text.strip() if title_tag else ""
        link = base_url + title_tag["href"] if title_tag else ""
        summary_tag = result.find("div", class_="result-abstract")
        abstract = summary_tag.text.strip() if summary_tag else ""
        articles.append({
            "title": title,
            "abstract": abstract,
            "link": link,
            "source": "cochrane"
        })
        if len(articles) >= max_results:
            break
    return articles