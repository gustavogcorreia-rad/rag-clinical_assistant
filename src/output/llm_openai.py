# src/output/llm_openai.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _load_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY não definida.\n"
            "Defina no arquivo .env ou como variável de ambiente."
        )
    return key


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = _load_api_key()
        _client = OpenAI(api_key=api_key)  #NOME CORRETO
    return _client


def consultar_gpt4o(
    prompt: str,
    max_tokens: int = 800,
    temperature: float = 0.2,
    model: str = "gpt-4o"
) -> str:
    """
    Consulta o GPT-4o via OpenAI API (SDK moderno).
    """
    client = _get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()