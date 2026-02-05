# src/output/answer_generator.py

def montar_prompt_rag(query, articles, clinical_factors=None):
    """
    Builds an English-language prompt for the LLM with strong emphasis on
    immediate management of a previously diagnosed intracranial hemorrhage.
    
    All reasoning must be derived strictly from the abstracts provided.
    """
    # ------------------------
    # SECTION 1 — CLINICAL CONTEXT
    # ------------------------
    context_section = ""
    if clinical_factors:
        context_section = (
            "Clinical context (patient comorbidities, risk modifiers, or acute findings): "
            + ", ".join(clinical_factors)
            + ".\n"
        )
    else:
        context_section = "Clinical context: not specified.\n"

    # ------------------------
    # SECTION 2 — ABSTRACTS (EVIDENCE)
    # ------------------------
    evidence_section = ""
    for i, art in enumerate(articles, 1):
        title = art.get("title", "No title available").strip()
        link = art.get("link", "").strip()
        abstract = art.get("abstract", "").strip()

        # Abstract pode estar vazio para alguns artigos do EuropePMC ou Arxiv
        if not abstract:
            abstract = "No abstract available."

        evidence_section += (
            f"\n[{i}] {title}\n"
            f"Source: {link}\n"
            f"Abstract: {abstract}\n"
        )

    # ------------------------
    # SECTION 3 — PROMPT FOR THE LLM
    # ------------------------
    prompt = (
        "You are a senior attending emergency physician with expertise in neurotrauma and neurocritical care.\n"
        "The diagnosis and subtype of intracranial hemorrhage have ALREADY been confirmed by a CT scan and classified by an AI model.\n"
        f"{context_section}\n"
        "Your task is to provide an evidence-based emergency management recommendation based STRICTLY on the provided article abstracts.\n"
        "Focus ONLY on immediate management steps relevant to the current emergency department phase. Specifically address:\n"
        "- Urgent interventions and stabilization priorities\n"
        "- Monitoring and neurologic observation\n"
        "- Blood pressure and coagulopathy management\n"
        "- Medication considerations (antiplatelet/anticoagulant reversal if supported)\n"
        "- Indications for neurosurgical or endovascular intervention\n"
        "- Transfer decisions if neurosurgery is unavailable\n"
        "- Any risk modifiers supported by evidence from the abstracts\n"
        "\nRules:\n"
        "- DO NOT restate or discuss diagnosis. The diagnosis is already known.\n"
        "- DO NOT hallucinate information not explicitly supported by the abstracts.\n"
        "- DO NOT infer anatomy not mentioned in the abstracts.\n"
        "- If guidelines, consensus statements, or systematic reviews are present, give them priority.\n"
        "- Cite supporting articles ONLY using their index in brackets (e.g., [1], [2]).\n"
        "- DO NOT list references at the end. The system will append a formatted reference list.\n"
        "- Final answer must be in English.\n"
        "- Provide a concise, clinically actionable summary.\n"
        "\n### Article Abstracts\n"
        f"{evidence_section}\n"
        "Please answer in English."
    )

    return prompt


# -------------------------------------------------------------
# FORMATAÇÃO DAS REFERÊNCIAS
# -------------------------------------------------------------
def format_references(articles):
    """
    Produz referências em Markdown com:
      1. Número
      2. Título
      3. Link
    """
    refs = []
    for i, art in enumerate(articles, 1):
        title = art.get("title", "No title available").strip()
        link = art.get("link", "").strip()

        # fallback se link estiver ausente
        if not link:
            refs.append(f"{i}. {title} (no link available)")
        else:
            refs.append(f"{i}. [{title}]({link})")

    return "\n".join(refs)