# src/retrieval/hybrid_retriever.py

from typing import List, Dict

from src.api_integrations.pubmed import buscar_pubmed
from src.api_integrations.europepmc import buscar_europepmc
from src.api_integrations.arxiv import buscar_arxiv
from src.api_integrations.clinical_trials import buscar_clinical_trials
from src.api_integrations.who_guidelines import buscar_who


# ---------------------------------------------------------
# Mapeamento de fontes disponíveis
# ---------------------------------------------------------
ALL_SOURCES = {
    "pubmed": buscar_pubmed,
    "europepmc": buscar_europepmc,
    "arxiv": buscar_arxiv,
    "clinical_trials": buscar_clinical_trials,
    "who": buscar_who
}


# ---------------------------------------------------------
# FUNÇÃO PRINCIPAL DO RETRIEVER
# ---------------------------------------------------------
def buscar_documentos_relevantes(
    query: str,
    max_results: int = 12,
    sources: List[str] = None
) -> List[Dict]:
    """
    Busca artigos em múltiplas fontes, com fallback automático,
    deduplicação inteligente e retorno limitado aos artigos mais relevantes.

    Parâmetros:
        query: string de busca
        max_results: número máximo total de artigos combinados
        sources: lista de nomes das fontes (ou usa o default)
    """

    # -------------------------------------------------
    # FONTES DEFAULT (PUBMED E EUROPEPMC EM 1º LUGAR)
    # -------------------------------------------------
    if sources is None:
        sources = ["pubmed", "europepmc", "arxiv"]

        # ClinicalTrials e WHO são opcionais (instáveis)
        # Para ativar quando quiser:
        # sources += ["clinical_trials", "who"]

    resultados: List[Dict] = []

    # -------------------------------------------------
    # BUSCA EM CADA FONTE SELECIONADA
    # -------------------------------------------------
    for src in sources:
        func = ALL_SOURCES.get(src)
        if not func:
            continue

        try:
            # OBS: pedimos um pouco mais de cada fonte para permitir
            # dedupe + ranking no pipeline posterior.
            artigos = func(query, max_results=max_results)
            resultados.extend(artigos)

        except Exception as e:
            print(f"[Retriever] Erro ao buscar em '{src}': {e}")

    # -------------------------------------------------
    # DEDUPLICAÇÃO INTELIGENTE
    # -------------------------------------------------
    vistos = set()
    dedup = []

    for art in resultados:
        title = (art.get("title", "") or "").strip().lower()

        # chave única por título
        key = title

        if not title:
            continue

        if key not in vistos:
            vistos.add(key)
            dedup.append(art)

    # -------------------------------------------------
    # RETORNO LIMITADO PELO MAX_RESULTS
    # -------------------------------------------------
    return dedup[:max_results]


# ---------------------------------------------------------
# TESTE RÁPIDO
# ---------------------------------------------------------
if __name__ == "__main__":
    q = "acute management of epidural hemorrhage in emergency settings"
    docs = buscar_documentos_relevantes(q, max_results=8)
    print("\n--- Documentos encontrados ---")
    for doc in docs:
        print(doc["title"])