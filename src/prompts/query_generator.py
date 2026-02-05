# src/prompts/query_generator.py

from typing import List
from src.graph.nodes import ClinicalNode


# -------------------------------------------------------------
#  AUXILIAR: Extrai texto de forma robusta de qualquer ClinicalNode
# -------------------------------------------------------------
def _node_text(node: ClinicalNode) -> str:
    """
    Extrai texto útil de um ClinicalNode sem assumir atributos específicos.
    Procura campos comuns, examina __dict__, e usa string fallback.
    """
    parts = []

    # Tentativa direta em atributos comuns
    for attr in ["description", "name", "value", "label", "texto", "type"]:
        if hasattr(node, attr):
            val = getattr(node, attr)
            if isinstance(val, str):
                parts.append(val)

    # Varre atributos do objeto dinamicamente
    if hasattr(node, "__dict__"):
        for k, v in vars(node).items():
            if isinstance(v, str) and v not in parts:
                parts.append(v)

    # Fallback final
    if not parts:
        parts.append(str(node))

    return " ".join(parts).lower()


# -------------------------------------------------------------
#  DETECTA TIPO DE HEMORRAGIA
# -------------------------------------------------------------
def _extract_hemorrhage_type(grafo: List[ClinicalNode]) -> str:
    """
    Infere o tipo de hemorragia analisando texto dos nós.
    Não assume atributos fixos.
    """
    for node in grafo:
        text = _node_text(node)

        # Detecção específica
        if "epidural" in text:
            return "epidural hemorrhage"
        if "subdural" in text:
            return "subdural hemorrhage"
        if "subarachnoid" in text or "sah" in text:
            return "subarachnoid hemorrhage"
        if "intracerebral" in text or "intraparenchymal" in text or "ich" in text:
            return "intracerebral hemorrhage"

        # Menção genérica de hemorragia
        if any(term in text for term in ["hemorrhage", "haemorrhage", "hematoma", "haematoma"]):
            return "intracranial hemorrhage"

    # Fallback
    return "intracranial hemorrhage"


# -------------------------------------------------------------
#  DETECTA TRAUMA
# -------------------------------------------------------------
def _has_trauma(grafo: List[ClinicalNode]) -> bool:
    for node in grafo:
        text = _node_text(node)

        if any(term in text for term in ["trauma", "traumatic", "head injury", "head trauma", "fall"]):
            return True

    return False


# -------------------------------------------------------------
#  CONSTRÓI BLOCO BASE DA QUERY POR TIPO DE HEMORRAGIA
# -------------------------------------------------------------
def _base_query_for_hemorrhage(hemorrhage_type: str, traumatic: bool) -> str:
    ht = hemorrhage_type.lower()

    if "epidural" in ht:
        hem_terms = [
            '"epidural hematoma"',
            '"epidural haematoma"',
            '"epidural hemorrhage"'
        ]
    elif "subdural" in ht:
        hem_terms = [
            '"subdural hematoma"',
            '"subdural haematoma"',
            '"acute subdural hematoma"',
            '"chronic subdural hematoma"'
        ]
    elif "subarachnoid" in ht:
        hem_terms = [
            '"subarachnoid hemorrhage"',
            '"subarachnoid haemorrhage"',
            '"aneurysmal subarachnoid hemorrhage"'
        ]
    elif "intracerebral" in ht or "intraparenchymal" in ht:
        hem_terms = [
            '"intracerebral hemorrhage"',
            '"intracerebral haemorrhage"',
            '"intracranial hemorrhage"'
        ]
    else:
        hem_terms = [
            '"intracranial hemorrhage"',
            '"intracranial haemorrhage"',
            '"intracerebral hemorrhage"'
        ]

    hem_block = "(" + " OR ".join(hem_terms) + ")"

    if traumatic:
        context_block = '( "traumatic brain injury" OR "head trauma" OR "head injury" )'
    else:
        context_block = '( spontaneous OR "non-traumatic" OR hypertensive OR "primary intracerebral hemorrhage" )'

    management_block = '(' \
                       '"emergency department" OR "acute management" OR "initial management" OR ' \
                       'treatment OR therapy OR guideline OR "practice guideline" OR consensus OR recommendation ' \
                       ')'

    query = f"{hem_block} AND {context_block} AND {management_block}"
    return query


# -------------------------------------------------------------
#  QUERY ESPECÍFICA
# -------------------------------------------------------------
def gerar_query_especifica(grafo: List[ClinicalNode]) -> str:
    hemorrhage_type = _extract_hemorrhage_type(grafo)
    traumatic = _has_trauma(grafo)
    base_query = _base_query_for_hemorrhage(hemorrhage_type, traumatic)

    # Refinadores clínicos opcionais
    clinical_keywords = []

    for node in grafo:
        desc = _node_text(node)

        if "anticoag" in desc:
            clinical_keywords.append("anticoagulation OR anticoagulants")
        if "antiplatelet" in desc or "antiagregante" in desc:
            clinical_keywords.append("antiplatelet OR aspirin OR clopidogrel")
        if "hypertension" in desc or "hipertensão" in desc:
            clinical_keywords.append("hypertension")

    clinical_keywords = list(set(clinical_keywords))

    if clinical_keywords:
        ck_block = "(" + " OR ".join(clinical_keywords) + ")"
        query = f"{base_query} AND {ck_block}"
    else:
        query = base_query

    return query


# -------------------------------------------------------------
#  QUERY SIMPLIFICADA (FALLBACK)
# -------------------------------------------------------------
def gerar_query_simplificada(grafo: List[ClinicalNode]) -> str:
    hemorrhage_type = _extract_hemorrhage_type(grafo)
    traumatic = _has_trauma(grafo)
    return _base_query_for_hemorrhage(hemorrhage_type, traumatic)