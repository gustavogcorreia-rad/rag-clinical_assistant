# src/api_integrations/arxiv.py

import requests
from xml.etree import ElementTree

def buscar_arxiv(query, max_results=30):
    """
    Busca artigos no Arxiv usando a API via RSS (XML).
    Retorna uma lista de dicionários padronizados.
    """
    # Ajuste o termo para URL
    query_url = "+".join(query.split())
    url = f"http://export.arxiv.org/api/query?search_query=all:{query_url}&start=0&max_results={max_results}"
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"Erro ao buscar no Arxiv: {response.status_code}")
    root = ElementTree.fromstring(response.text)
    articles = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ')
        link = ""
        for l in entry.findall('{http://www.w3.org/2005/Atom}link'):
            if l.attrib.get('type') == 'text/html':
                link = l.attrib.get('href')
                break
        if not link:
            link = entry.find('{http://www.w3.org/2005/Atom}id').text
        authors = []
        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
            name = author.find('{http://www.w3.org/2005/Atom}name').text
            if name:
                authors.append(name)
        published = entry.find('{http://www.w3.org/2005/Atom}published').text[:10]  # YYYY-MM-DD
        articles.append({
            "title": title,
            "abstract": summary,
            "link": link,
            "authors": authors,
            "year": published[:4],
            "source": "arxiv"
        })
    return articles