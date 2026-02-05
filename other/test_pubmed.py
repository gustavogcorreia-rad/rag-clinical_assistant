# src/test_pubmed_busca.py

from src.api_integrations.pubmed import buscar_pubmed

def print_artigo(art, i):
    print(f"\n{i+1}. {art['title']}")
    print(f"   Ano: {art['year']}")
    print(f"   Autores: {', '.join(art['authors'])}")
    print(f"   Journal: {art['journal']}")
    print(f"   Link: {art['link']}")
    print(f"   Abstract (primeiras 250 letras): {art['abstract'][:250]}...")

if __name__ == "__main__":
    query = "epidural hemorrhage management"
    print(f"Buscando PubMed para: {query}\n")
    artigos = buscar_pubmed(query, max_results=10)
    print(f"Foram encontrados {len(artigos)} artigos:")
    for i, art in enumerate(artigos):
        print_artigo(art, i)