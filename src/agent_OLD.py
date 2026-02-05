# src/agent.py

from typing import Dict, Tuple, List

from src.graph.builder import construir_grafo_clinico
from src.prompts.query_generator import gerar_query_especifica, gerar_query_simplificada
from src.retrieval.hybrid_retriever import buscar_documentos_relevantes
from src.retrieval.filters import filtrar_artigos_por_contexto
from src.output.answer_generator import montar_prompt_rag, format_references
from src.output.llm_openai import consultar_gpt4o
from src.api_integrations.europepmc import priorizar_artigos  # funciona p/ qualquer fonte


def processar(dados_clinicos: Dict) -> Tuple[str, str]:
    """
    Pipeline principal do agente de suporte à decisão:

    1. Constrói grafo clínico a partir dos dados recebidos do front-end.
    2. Gera query específica para hemorragia intracraniana (tipo + contexto).
    3. Faz busca híbrida em bases (PubMed, EuropePMC, etc.).
    4. Aplica fallback com query simplificada se necessário.
    5. Filtra artigos claramente fora de contexto (stroke isquêmico puro, neonatal etc.).
    6. Prioriza guidelines / revisões / consensos.
    7. Monta prompt RAG e consulta o LLM (GPT-4o).
    8. Formata a lista de referências.

    Retorna:
        (resposta_llm, referencias_markdown)
    """

    # -------------------------------------------------
    # 1. Grafo clínico
    # -------------------------------------------------
    grafo = construir_grafo_clinico(dados_clinicos)

    # -------------------------------------------------
    # 2. Query específica
    # -------------------------------------------------
    query_especifica = gerar_query_especifica(grafo)

    # usar um retmax maior para permitir filtro e priorização
    artigos: List[Dict] = buscar_documentos_relevantes(query_especifica, max_results=20)
    query_utilizada = query_especifica

    # -------------------------------------------------
    # 3. Fallback com query simplificada (se nada veio)
    # -------------------------------------------------
    if not artigos:
        query_simplificada = gerar_query_simplificada(grafo)
        artigos = buscar_documentos_relevantes(query_simplificada, max_results=20)
        query_utilizada = query_simplificada

    # Se ainda assim nada for encontrado, evita chamar o LLM à toa
    if not artigos:
        msg = (
            "⚠️ No relevant scientific articles were found for this specific combination of "
            "intracranial hemorrhage type and clinical factors.\n\n"
            "Please consider broadening the clinical query or reviewing the case manually."
        )
        return msg, "No references available."

    # -------------------------------------------------
    # 4. Filtro por contexto clínico
    # -------------------------------------------------
    hemorrhage_type = (dados_clinicos.get("hemorrhage_type") or "").lower()
    traumatic = bool(dados_clinicos.get("recent_trauma"))

    artigos = filtrar_artigos_por_contexto(artigos, hemorrhage_type, traumatic)

    if not artigos:
        msg = (
            "⚠️ All retrieved articles were filtered out as clinically irrelevant "
            "(e.g., pure ischemic stroke or neonatal-only content).\n\n"
            "No suitable evidence was found for this clinical scenario."
        )
        return msg, "No references available."

    # -------------------------------------------------
    # 5. Prioriza (guidelines, systematic reviews, etc.)
    #    A função priorizar_artigos funciona para qualquer fonte,
    #    pois usa apenas título/abstract.
    # -------------------------------------------------
    artigos = priorizar_artigos(artigos)
    artigos = artigos[:6]  # envia só os 6 mais relevantes para o LLM

    if not artigos:
        msg = (
            "⚠️ It was not possible to select relevant articles after prioritization.\n\n"
            "No suitable evidence could be used for this query."
        )
        return msg, "No references available."

    # -------------------------------------------------
    # 6. Prepara fatores clínicos positivos para o prompt
    # -------------------------------------------------
    fatores_positivos = [
        k.replace("_", " ")
        for k, v in dados_clinicos.items()
        if isinstance(v, bool) and v is True
    ]

    # -------------------------------------------------
    # 7. Monta prompt RAG e consulta LLM
    # -------------------------------------------------
    prompt = montar_prompt_rag(query_utilizada, artigos, clinical_factors=fatores_positivos)

    resposta_llm = consultar_gpt4o(
        prompt,
        max_tokens=800,
        temperature=0.2,
        model="gpt-4o"
    )

    # -------------------------------------------------
    # 8. Monta referências em Markdown
    # -------------------------------------------------
    referencias = format_references(artigos)

    return resposta_llm, referencias


# Teste manual:
if __name__ == "__main__":
    mock_dados = {
        "hemorrhage_type": "epidural hemorrhage",
        "hypertension": True,
        "diabetes": False,
        "antiplatelet_use": True,
        "recent_trauma": True
    }
    r, ref = processar(mock_dados)
    print("Resposta LLM:\n", r)
    print("\nReferências:\n", ref)