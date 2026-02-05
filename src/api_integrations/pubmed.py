# src/api_integrations/pubmed.py

import os
import requests
from xml.etree import ElementTree


NCBI_BASE_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_BASE_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _get_ncbi_common_params():
    """
    Retorna parâmetros opcionais recomendados pela NCBI,
    se você quiser configurá-los via variáveis de ambiente.
    """
    params = {}
    email = os.environ.get("NCBI_EMAIL")
    tool = os.environ.get("NCBI_TOOL")  # ex.: "ich_rag_assistant"
    api_key = os.environ.get("NCBI_API_KEY")

    if email:
        params["email"] = email
    if tool:
        params["tool"] = tool
    if api_key:
        params["api_key"] = api_key

    return params


def _parse_abstract(article_elem) -> str:
    """
    Alguns artigos têm múltiplos <AbstractText>. Junta todos em um único texto.
    """
    abstract_texts = article_elem.findall(".//Abstract/AbstractText")
    if not abstract_texts:
        return ""

    parts = []
    for elem in abstract_texts:
        txt = (elem.text or "").strip()
        if txt:
            parts.append(txt)
    return " ".join(parts)


def buscar_pubmed(query: str, max_results: int = 30):
    """
    Busca artigos no PubMed com base na query.
    Retorna uma lista de dicionários padronizados:
      [
        {
          "title": str,
          "abstract": str,
          "link": str,
          "authors": [str, ...],
          "year": str,
          "journal": str,
          "source": "pubmed"
        },
        ...
      ]
    """

    # Cap de segurança para não pedir demais ao E-utilities
    max_results = min(max_results, 50)

    # ----------------------------------------------------------------------
    # 1. ESEARCH – obter lista de PMIDs
    # ----------------------------------------------------------------------
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "xml",
    }
    params.update(_get_ncbi_common_params())

    resp = requests.get(NCBI_BASE_ESEARCH, params=params, timeout=15)

    if resp.status_code != 200:
        raise RuntimeError(f"Erro ao buscar no PubMed (esearch). HTTP {resp.status_code}")

    try:
        root = ElementTree.fromstring(resp.text)
    except Exception as e:
        raise RuntimeError(f"Erro ao parsear XML do PubMed (esearch): {e}")

    idlist = [idtag.text for idtag in root.findall(".//IdList/Id") if idtag.text]

    if not idlist:
        return []

    # ----------------------------------------------------------------------
    # 2. EFETCH – obter detalhes dos artigos
    # ----------------------------------------------------------------------
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(idlist),
        "retmode": "xml",
    }
    fetch_params.update(_get_ncbi_common_params())

    fetch_resp = requests.get(NCBI_BASE_EFETCH, params=fetch_params, timeout=30)

    if fetch_resp.status_code != 200:
        raise RuntimeError(f"Erro ao recuperar detalhes dos artigos no PubMed (efetch). HTTP {fetch_resp.status_code}")

    try:
        fetch_root = ElementTree.fromstring(fetch_resp.text)
    except Exception as e:
        raise RuntimeError(f"Erro ao parsear XML do PubMed (efetch): {e}")

    articles = []

    for article in fetch_root.findall(".//PubmedArticle"):
        # Título
        title = article.findtext(".//ArticleTitle") or ""

        # Resumo (pode ter múltiplos blocos)
        abstract = _parse_abstract(article)

        # PMID e link
        pmid = article.findtext(".//PMID") or ""
        link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

        # Autores
        authors = []
        for a in article.findall(".//Author"):
            lastname = a.findtext("LastName") or ""
            firstname = a.findtext("ForeName") or ""
            if lastname and firstname:
                authors.append(f"{firstname} {lastname}")

        # Ano (tenta Year, senão MedlineDate)
        year = article.findtext(".//JournalIssue/PubDate/Year") or ""
        if not year:
            medline_date = article.findtext(".//JournalIssue/PubDate/MedlineDate") or ""
            # Ex.: "2024 Jan-Feb" → pega primeiro token numérico
            for token in medline_date.split():
                if token.isdigit() and len(token) == 4:
                    year = token
                    break

        # Journal
        journal = article.findtext(".//Journal/Title") or ""

        articles.append({
            "title": title.strip(),
            "abstract": abstract.strip(),
            "link": link.strip(),
            "authors": authors,
            "year": year.strip(),
            "journal": journal.strip(),
            "source": "pubmed",
        })

    return articles


def priorizar_artigos(articles):
    """
    Coloca guidelines, consensos e revisões sistemáticas no topo da lista.
    Usa termo no título ou abstract.
    """
    PRIORITY_TERMS = [
        "guideline",
        "guidelines",
        "consensus",
        "systematic review",
        "meta-analysis",
        "metaanalysis",
        "recommendation",
        "practice guideline",
        "review"
    ]

    def score(art):
        abstract = art.get("abstract", "").lower()
        title = art.get("title", "").lower()
        return sum(term in abstract or term in title for term in PRIORITY_TERMS)

    return sorted(articles, key=score, reverse=True)


# Teste rápido
if __name__ == "__main__":
    q = "intracranial hemorrhage emergency management guideline"
    arts = buscar_pubmed(q, max_results=5)
    for i, art in enumerate(arts, 1):
        print(f"\n[{i}] {art['title']} ({art['year']})")
        print("Journal:", art["journal"])
        print("Link:", art["link"])
        print("Authors:", ", ".join(art["authors"]))
        print("Abstract snippet:", art["abstract"][:300], "...")