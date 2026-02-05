# src/api_integrations/europepmc.py

import requests

def buscar_europepmc(query, max_results=30):
    """
    Busca artigos científicos no Europe PMC.
    Retorna uma lista de dicionários padronizados.
    """
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": max_results
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise RuntimeError("Erro ao buscar no Europe PMC")
    result = response.json()
    articles = []
    for rec in result.get("resultList", {}).get("result", []):
        title = rec.get("title", "")
        abstract = rec.get("abstractText", "")
        pmcid = rec.get("pmcid") or rec.get("id") or ""
        doi = rec.get("doi")
        if pmcid:
            link = f"https://europepmc.org/article/{rec.get('source', 'MED')}/{pmcid}"
        elif doi:
            link = f"https://doi.org/{doi}"
        else:
            link = ""
        authors = []
        if "authorList" in rec:
            for a in rec["authorList"].get("author", []):
                if isinstance(a, dict):
                    name = a.get("fullName") or a.get("lastName") or ""
                    if name:
                        authors.append(name)
        year = rec.get("pubYear", "")
        journal = rec.get("journalTitle", "")
        articles.append({
            "title": title,
            "abstract": abstract,
            "link": link,
            "authors": authors,
            "year": year,
            "journal": journal,
            "source": "europepmc"
        })
    return articles

def priorizar_artigos(articles):
    PRIORITY_TERMS = ["guideline", "consensus", "systematic review", "meta-analysis", "recommendation"]
    def score(art):
        abstract = art.get("abstract", "").lower()
        title = art.get("title", "").lower()
        return sum(term in abstract or term in title for term in PRIORITY_TERMS)
    return sorted(articles, key=score, reverse=True)

# Teste rápido
if __name__ == "__main__":
    query = "epidural hemorrhage emergency management"
    artigos = buscar_europepmc(query, max_results=5)
    for art in artigos:
        print(f"\nTítulo: {art['title']}\nAno: {art['year']}\nAutores: {', '.join(art['authors'])}\nJournal: {art['journal']}\nLink: {art['link']}\nResumo: {art['abstract'][:200]}...")