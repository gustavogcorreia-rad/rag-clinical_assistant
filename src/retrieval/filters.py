# src/retrieval/filters.py

from typing import List, Dict, Any
from src.retrieval.scoring import rank_and_filter_articles


def filtrar_e_ranquear_artigos(
    articles: List[Dict[str, Any]],
    hemorrhage_type: str,
    dados_clinicos: Dict[str, Any],
    top_k: int = 8
) -> List[Dict[str, Any]]:
    """
    Filtra e ranqueia artigos de forma contextual, retornando apenas os top_k.
    - Exclui pediatria
    - Remove isquemia/trombectomia quando fora de contexto
    - Penaliza TBI quando não traumático
    - Dá boost por sinais clínicos (checkboxes) e por perfil do tipo de hemorragia
    """
    return rank_and_filter_articles(
        articles=articles,
        hemorrhage_type=hemorrhage_type,
        dados_clinicos=dados_clinicos,
        top_k=top_k
    )