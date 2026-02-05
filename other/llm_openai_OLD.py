# src/output/llm_openai.py

import os
from openai import OpenAI
import traceback


# -------------------------------------------------------------
# LEITURA DA API KEY — SEGURO E UNIVERSAL
# -------------------------------------------------------------
def _load_api_key():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY não definida.\n"
            "Defina com: export OPENAI_API_KEY='sua_chave_aqui'"
        )
    return key


# -------------------------------------------------------------
# FUNÇÃO PRINCIPAL PARA CONSULTAR O GPT-4o
# -------------------------------------------------------------
def consultar_gpt4o(
    prompt: str,
    max_tokens: int = 800,
    temperature: float = 0.2,
    model: str = "gpt-4o"
) -> str:
    """
    Consulta o OpenAI GPT-4o com segurança e tratamento de erros.
    Retorna a resposta em string.
    """

    api_key = _load_api_key()
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=30  # evita travar o Streamlit
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("\nERRO AO CONSULTAR GPT-4o:")
        print(traceback.format_exc())

        return (
            "⚠️ *There was an error when consulting the LLM (GPT-4o). "
            "The system could not generate an evidence-based recommendation.*\n\n"
            f"Error: {str(e)}"
        )