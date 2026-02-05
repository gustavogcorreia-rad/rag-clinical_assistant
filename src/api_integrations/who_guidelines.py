# src/api_integrations/who_guidelines.py

import requests
from bs4 import BeautifulSoup

def buscar_who(query, max_results=8):
    """
    Busca guidelines/documentos relevantes no WHO IRIS (novo portal).
    Retorna uma lista de dicionários padronizados.
    """
    base_url = "https://iris.who.int"
    search_url = f"{base_url}/discover"
    params = {"query": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    response = requests.get(search_url, params=params, headers=headers, timeout=20)
    if response.status_code != 200:
        print("WHO IRIS search failed:", response.status_code)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    # Novo seletor: títulos de artigos
    for result in soup.find_all("a", class_="search-result-item__title"):
        title = result.text.strip()
        link = base_url + result["href"] if result.get("href") else ""
        # Abstract não está disponível na lista de resultados
        articles.append({
            "title": title,
            "abstract": "",
            "link": link,
            "source": "who"
        })
        if len(articles) >= max_results:
            break
    return articles