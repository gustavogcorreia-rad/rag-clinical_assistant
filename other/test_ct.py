from src.api_integrations.cochrane import buscar_cochrane
from src.api_integrations.who_guidelines import buscar_who


docs = buscar_cochrane("intracranial hemorrhage", max_results=3)
for d in docs:
    print(d["title"])
    print(d["link"])

docs = buscar_who("intracranial hemorrhage", max_results=3)
for d in docs:
    print(d["title"])
    print(d["link"])