# src/agent.py

from src.graph.builder import construir_grafo_clinico
from src.prompts.query_generator import gerar_query_especifica, gerar_query_simplificada
from src.retrieval.hybrid_retriever import buscar_documentos_relevantes
from src.retrieval.filters import filtrar_e_ranquear_artigos
from src.output.answer_generator import montar_prompt_rag, format_references
from src.output.llm_openai import consultar_gpt4o

def processar(dados_clinicos: dict):
    grafo = construir_grafo_clinico(dados_clinicos)

    query_especifica = gerar_query_especifica(grafo)
    artigos = buscar_documentos_relevantes(query_especifica, max_results=40)

    query_utilizada = query_especifica

    if not artigos:
        query_simplificada = gerar_query_simplificada(grafo)
        artigos = buscar_documentos_relevantes(query_simplificada, max_results=40)
        query_utilizada = query_simplificada

    hemorrhage_type = (dados_clinicos.get("hemorrhage_type") or "").lower()

    # Filtra + ranqueia contextual e retorna TOP 8
    artigos = filtrar_e_ranquear_artigos(
        articles=artigos,
        hemorrhage_type=hemorrhage_type,
        dados_clinicos=dados_clinicos,
        top_k=8
    )

    fatores_positivos = [k.replace("_", " ") for k, v in dados_clinicos.items() if v is True]

    prompt = montar_prompt_rag(query_utilizada, artigos, clinical_factors=fatores_positivos)
    resposta_llm = consultar_gpt4o(prompt, max_tokens=900, temperature=0.2, model="gpt-4o")

    referencias = format_references(artigos)
    return resposta_llm, referencias


if __name__ == "__main__":
    mock_dados = {
        "hemorrhage_type": "intraparenchymal hemorrhage",
        "hypertension": True,
        "altered_consciousness": True,
        "severe_headache": True,
        "recent_trauma": False,
        "vascular_malformation": True,
        "neurosurgery_available": True,
        "transfer_planned": False,
    }
    r, ref = processar(mock_dados)
    print("Resposta LLM:\n", r)
    print("Referências:\n", ref)