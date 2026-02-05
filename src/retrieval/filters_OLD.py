# src/retrieval/filters.py

from typing import List, Dict

# Termos que indicam contexto de hemorragia
HEM_TERMS = [
    "hemorrhage", "haemorrhage",
    "hematoma", "haematoma",
    "intracranial bleed", "cerebral bleed"
]

# Termos que indicam artigos de stroke isquêmico (fora de escopo)
STROKE_ISCHEMIC_TERMS = [
    "ischemic stroke", "ischaemic stroke",
    "acute ischemic stroke", "ais",
    "large vessel occlusion", "lvo",
    "endovascular thrombectomy", "thrombectomy",
    "stent retriever", "mechanical thrombectomy"
]

# Termos que indicam contexto neonatal ou pediátrico específico
PEDIATRIC_TERMS = [
    "neonatal", "neonate", "pediatric", "paediatric",
    "infant", "newborn"
]


def _texto_artigo(art: Dict) -> str:
    """
    Função auxiliar segura para montar um texto combinando título + abstract,
    sem quebrar caso algum campo esteja ausente.
    """
    title = art.get("title", "") or ""
    abstract = art.get("abstract", "") or ""
    return f"{title} {abstract}".lower()


def filtrar_artigos_por_contexto(
    articles: List[Dict],
    hemorrhage_type: str,
    traumatic: bool
) -> List[Dict]:
    """
    Remove artigos claramente fora do contexto de hemorragia intracraniana:

    - descarta stroke isquêmico puro (sem menção a hemorragia);
    - descarta estudos exclusivamente de trombectomia em isquemia;
    - descarta artigos neonatais/pediátricos MUITO fora do escopo (opcional);
    - mantém guidelines gerais de TBI mesmo sem "hemorrhage";
    - nunca retorna lista vazia (fallback).

    O filtro é conservador: só remove artigos definitivamente irrelevantes.
    """

    ht = hemorrhage_type.lower().strip() if hemorrhage_type else ""
    filtrados = []

    for art in articles:
        texto = _texto_artigo(art)

        # ---------------------------------------
        # 1) Filtro de isquemia pura
        # ---------------------------------------
        # Se menciona termos de stroke isquêmico E NÃO fala nada de hemorragia,
        # então é irrelevante para o nosso contexto.
        if any(term in texto for term in STROKE_ISCHEMIC_TERMS):
            if not any(ht in texto for ht in HEM_TERMS):
                # Trombectomia puramente isquêmica → descarta
                continue

        # ---------------------------------------
        # 2) Evitar artigos neonatais/pediátricos se o caso não for pediátrico
        # (pode ser ajustado no futuro se você quiser inclusão seletiva)
        # ---------------------------------------
        if any(term in texto for term in PEDIATRIC_TERMS):
            # Estudos de hemorragia intracraniana em neonatos são outro universo;
            # se você não estiver lidando com isso, normalmente é ruído.
            continue

        # ---------------------------------------
        # 3) Se é caso traumático, artigos com trauma são mais relevantes
        # (Aqui não removemos, apenas permitimos todos. Filtro de ranking pode vir depois.)
        # ---------------------------------------
        # Nada a filtrar ainda — mantemos para possível expansão.

        # ---------------------------------------
        # Se não caiu nos casos irrelevantes, mantemos
        # ---------------------------------------
        filtrados.append(art)

    # ---------------------------------------
    # Fallback: se o filtro ficar agressivo demais
    # ---------------------------------------
    if not filtrados:
        return articles

    return filtrados