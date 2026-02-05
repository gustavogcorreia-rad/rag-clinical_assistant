# src/graph/builder.py

from typing import List
from .nodes import ClinicalNode, CLINICAL_FACTORS


def construir_grafo_clinico(dados_clinicos: dict) -> List[ClinicalNode]:
    """
    Recebe o dicionário de dados clínicos (provido pelo front-end / modelo)
    e retorna uma lista de ClinicalNodes que representam um grafo simples.

    - Cada ClinicalNode é criado com:
        name  -> nome interno do fator clínico (ex.: "hypertension", "recent_trauma")
        value -> valor correspondente (bool, str, float, etc.)
    - Fatores sem valor (ausentes ou None) são ignorados para manter o grafo enxuto.
    """
    grafo: List[ClinicalNode] = []

    for fator in CLINICAL_FACTORS:
        if fator not in dados_clinicos:
            continue

        value = dados_clinicos[fator]

        # Ignora fatores explicitamente não informados
        if value is None:
            continue

        node = ClinicalNode(name=fator, value=value)
        grafo.append(node)

    return grafo


# Exemplo de uso (para testes manuais)
if __name__ == "__main__":
    # Simulação de dados clínicos (mock)
    dados_clinicos = {
        "hemorrhage_type": "epidural hemorrhage",
        "hemorrhage_probability": 0.90,
        "hypertension": True,
        "diabetes": False,
        "chronic_liver_disease": False,
        "coagulopathy": True,
        # ... demais campos omitidos para exemplo
    }
    grafo = construir_grafo_clinico(dados_clinicos)
    for node in grafo:
        print(node)