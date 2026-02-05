# src/agent.py

from src.graph.builder import construir_grafo_clinico
from src.prompts.query_generator import gerar_query_automatica
from src.retrieval.hybrid_retriever import buscar_documentos_relevantes

def processar(dados_clinicos: dict):
    """
    Função principal do agente.
    Recebe os dados clínicos do front-end,
    monta o grafo, gera a query clínica, busca artigos e retorna resposta/resumo inicial.
    """
    # 1. Construir grafo clínico
    grafo = construir_grafo_clinico(dados_clinicos)
    
    # 2. Gerar query automática para o RAG
    query = gerar_query_automatica(grafo)
    
    # 3. Buscar artigos relevantes (PubMed, por enquanto)
    artigos = buscar_documentos_relevantes(query, max_results=5)
    
    # 4. Montar resposta clínica inicial (futura integração: answer_generator.py)
    if artigos:
        resposta = "Foram encontrados os seguintes artigos relevantes no PubMed:\n\n"
        for art in artigos:
            resposta += f"- [{art['title']}]({art['link']})\n"
    else:
        resposta = "Nenhum artigo relevante foi encontrado para a consulta."
    
    # 5. Referências (links e, futuramente, citação detalhada)
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