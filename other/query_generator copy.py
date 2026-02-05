# src/prompts/query_generator.py

def gerar_query_automatica(grafo_clinico):
    """
    Gera uma query otimizada para busca em PubMed sobre conduta/tratamento em hemorragia intracraniana,
    incluindo fatores positivos relevantes.
    """
    # 1. Tipo de hemorragia
    hemorrhage_type = None
    fatores_positivos = []

    for node in grafo_clinico:
        if node.name == "hemorrhage_type":
            hemorrhage_type = node.value
        elif node.name == "hemorrhage_probability":
            continue  # Ignorar probabilidade na query
        elif node.value:
            fatores_positivos.append(node.name.replace("_", " "))

    # 2. Termo base central: sempre focar em "management", "treatment", "guidelines"
    termos_central = ["intracranial hemorrhage"]
    if hemorrhage_type and hemorrhage_type != "intracranial hemorrhage":
        termos_central.append(hemorrhage_type)
    query_terms = " OR ".join(termos_central)

    # 3. Adiciona foco em tratamento/conduta
    focus_terms = "(treatment OR management OR guidelines)"

    # 4. Inclui fatores clínicos positivos (como AND, se houver)
    if fatores_positivos:
        fatores_str = " AND ".join(fatores_positivos)
        query = f"({query_terms}) AND {focus_terms} AND {fatores_str}"
    else:
        query = f"({query_terms}) AND {focus_terms}"

    return query

# Exemplo de uso para teste rápido
if __name__ == "__main__":
    from src.graph.nodes import ClinicalNode

    grafo = [
        ClinicalNode("hemorrhage_type", "epidural hemorrhage"),
        ClinicalNode("hemorrhage_probability", 0.90),
        ClinicalNode("hypertension", True),
        ClinicalNode("antiplatelet_use", True),
        ClinicalNode("recent_trauma", True)
    ]
    print(gerar_query_automatica(grafo))