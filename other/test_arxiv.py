from api_integrations.arxiv import buscar_arxiv

docs = buscar_arxiv("brain hemorrhage", max_results=3)
for d in docs:
    print(d["title"])
    print(d["link"])