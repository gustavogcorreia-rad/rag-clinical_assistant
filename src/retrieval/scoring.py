# src/retrieval/scoring.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any


PEDIATRIC_TERMS = [
    "neonatal", "neonate", "newborn", "infant", "pediatric", "paediatric", "child", "children"
]

ISCHEMIC_STROKE_TERMS = [
    "ischemic stroke", "ischaemic stroke", "large vessel occlusion", "lvo",
    "endovascular thrombectomy", "mechanical thrombectomy", "stent retriever", "thrombectomy"
]

TBI_TERMS = [
    "traumatic brain injury", "tbi", "brain injury guidelines", "modified brain injury guidelines",
    "mbig", "decompressive craniectomy for traumatic brain injury"
]

GENERAL_MGMT_TERMS = [
    "acute management", "emergency management", "initial management", "guideline",
    "practice guideline", "consensus", "recommendation", "therapy", "treatment",
    "critical care", "intensive care", "neurocritical"
]

GUIDELINE_REVIEW_TERMS = [
    "guideline", "practice guideline", "consensus", "recommendation",
    "systematic review", "meta-analysis", "meta analysis", "review"
]


def _normalize_hemorrhage_type(ht: str) -> str:
    ht = (ht or "").lower().strip()
    if "epidural" in ht:
        return "edh"
    if "subdural" in ht:
        return "sdh"
    if "subarach" in ht:
        return "sah"
    if "intraventric" in ht:
        return "ivh"
    if "intraparench" in ht or "intracerebral" in ht or "parenchymal" in ht:
        return "iph"
    # fallback
    return "ich"


def _text_blob(article: Dict[str, Any]) -> str:
    title = (article.get("title") or "")
    abstract = (article.get("abstract") or "")
    journal = (article.get("journal") or "")
    return f"{title} {abstract} {journal}".lower()


def _count_hits(text: str, terms: List[str]) -> int:
    return sum(1 for t in terms if t in text)


def _any_hit(text: str, terms: List[str]) -> bool:
    return any(t in text for t in terms)


@dataclass(frozen=True)
class HemorrhageProfile:
    key: str
    core_terms: List[str]
    management_terms: List[str]
    subtype_terms: List[str]
    off_context_penalties: List[str]


# 5 perfis estáveis — sem explosão combinatória
PROFILES: Dict[str, HemorrhageProfile] = {
    "edh": HemorrhageProfile(
        key="edh",
        core_terms=["epidural hematoma", "epidural haematoma", "epidural hemorrhage", "extradural hematoma", "extradural haemorrhage"],
        management_terms=["craniotomy", "neurosurgery", "surgical evacuation", "mass effect", "midline shift", "glasgow coma scale", "gcs"],
        subtype_terms=["temporal bone", "middle meningeal", "lucid interval"],
        off_context_penalties=["aneurysmal", "coiling", "clipping", "nimodipine", "vasospasm"]
    ),
    "sdh": HemorrhageProfile(
        key="sdh",
        core_terms=["subdural hematoma", "subdural haematoma", "acute subdural hematoma", "chronic subdural hematoma"],
        management_terms=["burr hole", "craniotomy", "neurosurgery", "surgical evacuation", "midline shift", "mass effect", "gcs"],
        subtype_terms=["bridging veins", "membrane", "drain", "recurrence"],
        off_context_penalties=["aneurysmal", "coiling", "clipping", "nimodipine", "vasospasm"]
    ),
    "iph": HemorrhageProfile(
        key="iph",
        core_terms=["intracerebral hemorrhage", "intracerebral haemorrhage", "intraparenchymal hemorrhage", "intraparenchymal haemorrhage", "primary intracerebral hemorrhage"],
        management_terms=["blood pressure", "antihypertensive", "reversal", "anticoagulation", "pcc", "vitamin k", "hemostasis", "icu", "neurocritical"],
        subtype_terms=["hematoma expansion", "spot sign", "perihematomal edema"],
        off_context_penalties=["coiling", "clipping", "nimodipine", "vasospasm"]
    ),
    "sah": HemorrhageProfile(
        key="sah",
        core_terms=["subarachnoid hemorrhage", "subarachnoid haemorrhage", "aneurysmal subarachnoid hemorrhage", "sah"],
        management_terms=["nimodipine", "vasospasm", "aneurysm", "coiling", "clipping", "external ventricular drain", "evd", "hydrocephalus", "angiography", "cta"],
        subtype_terms=["rebleeding", "delayed cerebral ischemia", "dci", "hunt hess", "wfns"],
        off_context_penalties=["burr hole", "chronic subdural", "bridging veins"]
    ),
    "ivh": HemorrhageProfile(
        key="ivh",
        core_terms=["intraventricular hemorrhage", "intraventricular haemorrhage", "ivh"],
        management_terms=["external ventricular drain", "evd", "hydrocephalus", "intracranial pressure", "fibrinolysis", "ventriculostomy"],
        subtype_terms=["obstructive hydrocephalus", "ventricular cast"],
        off_context_penalties=["coiling", "clipping", "nimodipine", "vasospasm"]  # IVH puro tende a ser diferente de SAH aneurismal
    ),
    # fallback geral
    "ich": HemorrhageProfile(
        key="ich",
        core_terms=["intracranial hemorrhage", "intracranial haemorrhage", "intracerebral hemorrhage"],
        management_terms=GENERAL_MGMT_TERMS,
        subtype_terms=[],
        off_context_penalties=[]
    ),
}


# Mapa de sinais clínicos -> termos para boost
SIGNALS: Dict[str, Dict[str, List[str]]] = {
    "altered_consciousness": {"boost": ["airway", "intubation", "gcs", "coma", "intracranial pressure", "icu", "neurocritical"]},
    "severe_headache": {"boost": ["thunderclap", "headache", "sentinel", "aneurysm", "subarachnoid"]},
    "hypertension": {"boost": ["blood pressure", "hypertension", "antihypertensive", "bp control"]},
    "coagulopathy": {"boost": ["coagulopathy", "reversal", "prothrombin complex", "pcc", "vitamin k", "fresh frozen plasma"]},
    "high_inr": {"boost": ["inr", "warfarin", "pcc", "vitamin k", "reversal"]},
    "thrombocytopenia": {"boost": ["thrombocytopenia", "platelet", "platelet transfusion"]},
    "antiplatelet_use": {"boost": ["antiplatelet", "aspirin", "clopidogrel", "platelet transfusion"]},
    "vascular_malformation": {"boost": ["aneurysm", "arteriovenous malformation", "avm", "vascular malformation", "coiling", "clipping", "angiography"]},
    "recent_trauma": {"boost": ["traumatic", "head injury", "tbi", "trauma"]},
    "neurosurgery_available": {"boost": ["neurosurgery", "surgical", "craniotomy", "coiling", "clipping"]},
    "transfer_planned": {"boost": ["transfer", "tertiary center", "neurosurgical center"]},
}


def hard_exclude(article_text: str, traumatic: bool) -> Tuple[bool, str]:
    """
    Retorna (excluir?, motivo).
    """
    # 1) Excluir pediatria sempre (como você pediu)
    if _any_hit(article_text, PEDIATRIC_TERMS):
        return True, "pediatrics"

    # 2) Excluir isquemia/trombectomia se NÃO houver hemorragia no texto
    has_hem = _any_hit(article_text, ["hemorrhage", "haemorrhage", "hematoma", "haematoma", "sah", "ivh"])
    if _any_hit(article_text, ISCHEMIC_STROKE_TERMS) and not has_hem:
        return True, "ischemia_without_hemorrhage"

    # 3) Se não traumático, excluir conteúdo fortemente TBI-guideline
    if not traumatic and _any_hit(article_text, TBI_TERMS):
        return True, "tbi_off_context"

    return False, ""


def score_article(
    article: Dict[str, Any],
    profile: HemorrhageProfile,
    positive_signals: List[str],
    traumatic: bool
) -> float:
    """
    Score simples, interpretável, e fácil de ajustar.
    """
    text = _text_blob(article)

    score = 0.0

    # Base: management terms e guideline/review
    score += 2.0 * _count_hits(text, GUIDELINE_REVIEW_TERMS)
    score += 1.0 * _count_hits(text, profile.management_terms)

    # Core/subtype match
    score += 4.0 * _count_hits(text, profile.core_terms)
    score += 1.5 * _count_hits(text, profile.subtype_terms)

    # Penalizar desvios do perfil
    score -= 2.0 * _count_hits(text, profile.off_context_penalties)

    # Penalizações contextuais
    if not traumatic:
        score -= 2.0 * _count_hits(text, ["traumatic", "tbi", "head injury", "brain injury"])
    else:
        score += 1.0 * _count_hits(text, ["traumatic", "tbi", "head injury", "brain injury"])

    # Boost pelos sinais clínicos positivos
    for sig in positive_signals:
        terms = SIGNALS.get(sig, {}).get("boost", [])
        score += 1.2 * _count_hits(text, terms)

    # Pequeno bônus por PubMed/EuropePMC (se quiser priorizar medicina vs preprint)
    src = (article.get("source") or "").lower()
    if src in ("pubmed", "europepmc"):
        score += 0.5
    if src == "arxiv":
        score -= 0.3

    return score


def rank_and_filter_articles(
    articles: List[Dict[str, Any]],
    hemorrhage_type: str,
    dados_clinicos: Dict[str, Any],
    top_k: int = 8
) -> List[Dict[str, Any]]:
    """
    1) hard exclude
    2) score
    3) sort desc
    4) return top_k
    """
    ht_key = _normalize_hemorrhage_type(hemorrhage_type)
    profile = PROFILES.get(ht_key, PROFILES["ich"])

    traumatic = bool(dados_clinicos.get("recent_trauma"))

    # sinais positivos (checkboxes True)
    positive_signals = [k for k, v in dados_clinicos.items() if v is True]

    kept: List[Tuple[float, Dict[str, Any]]] = []
    for art in articles:
        text = _text_blob(art)
        exclude, _reason = hard_exclude(text, traumatic)
        if exclude:
            continue
        s = score_article(art, profile, positive_signals, traumatic)
        kept.append((s, art))

    # fallback: se ficou vazio, devolve os originais sem hard exclude (mas ainda tirando pediatria)
    if not kept:
        fallback = []
        for art in articles:
            text = _text_blob(art)
            if _any_hit(text, PEDIATRIC_TERMS):
                continue
            fallback.append(art)
        return fallback[:top_k]

    kept.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in kept[:top_k]]