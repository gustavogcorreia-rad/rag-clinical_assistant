# src/agent.py

from src.graph.builder import construir_grafo_clinico
from src.prompts.query_generator import gerar_query_especifica, gerar_query_simplificada
from src.retrieval.hybrid_retriever import buscar_documentos_relevantes

def processar(dados_clinicos: dict):
    grafo = construir_grafo_clinico(dados_clinicos)
    
    # Query específica
    query_especifica = gerar_query_especifica(grafo)
    artigos = buscar_documentos_relevantes(query_especifica, max_results=5)
    
    # Se não encontrar, faz fallback para query simplificada
    fallback_usado = False
    if not artigos:
        query_simplificada = gerar_query_simplificada(grafo)
        artigos = buscar_documentos_relevantes(query_simplificada, max_results=5)
        fallback_usado = True

    # Monta resposta
    if artigos:
        if fallback_usado:
            resposta = (
                "Nenhum artigo foi encontrado para a busca clínica específica; "
                "os resultados abaixo referem-se a uma busca ampliada:\n\n"
            )
        else:
            resposta = "Foram encontrados os seguintes artigos relevantes:\n\n"
        for art in artigos:
            resposta += f"- [{art['title']}]({art['link']})\n"
    else:
        resposta = "Nenhum artigo relevante foi encontrado para a consulta."
    
    referencias = "\n".join([art['link'] for art in artigos]) if artigos else ""
    return resposta, referencias

# Teste local (pode ser removido em produção)
if __name__ == "__main__":
    mock_dados = {
        "hemorrhage_type": "epidural hemorrhage",
        "hypertension": True,
        "diabetes": False,
        "antiplatelet_use": True,
        "recent_trauma": True
    }
    r, ref = processar(mock_dados)
    print(r)
    print(ref)