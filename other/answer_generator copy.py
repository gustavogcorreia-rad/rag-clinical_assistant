# src/output/answer_generator.py

def montar_prompt_rag(query, articles, clinical_factors=None):
    """
    Builds an English prompt for LLM using the retrieved articles and clinical context.
    """
    # 1. Clinical context (in English)
    context = ""
    if clinical_factors:
        context = "Clinical context for the case: " + ", ".join(clinical_factors) + ".\n"

    # 2. Evidence section
    evidence = ""
    for i, art in enumerate(articles, 1):
        evidence += (
            f"\n[{i}] {art['title']}\n"
            f"Source: {art['link']}\n"
            f"Abstract: {art.get('abstract', '').strip()}\n"
        )

    # 3. LLM prompt (in English)
    prompt = (
        f"{context}"
        "You are a medical expert. Read the following article abstracts and answer strictly based on the information in the texts:\n"
        "- What is the evidence-based management or clinical approach for the case described?\n"
        "- Use only the evidence provided in the abstracts below. Do NOT hallucinate or create recommendations not present in the sources.\n"
        "- Provide a concise answer, cite references by number.\n"
        "\n### Article Abstracts\n"
        f"{evidence}\n"
        "\nPlease answer in English. Do not invent information beyond the abstracts."
    )
    return prompt

# Opcional: função para sumarizar as referências (links)
# def format_references(articles):
#    return "\n".join([f"{i+1}. {art['link']}" for i, art in enumerate(articles)])

def format_references(articles):
    """
    Gera lista de referências no formato Markdown: [Título do artigo](link)
    """
    refs = []
    for i, art in enumerate(articles, 1):
        title = art["title"]
        link = art["link"]
        refs.append(f"{i}. [{title}]({link})")
    return "\n".join(refs)