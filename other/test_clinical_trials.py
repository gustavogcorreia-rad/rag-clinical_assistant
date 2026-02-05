from src.api_integrations.clinical_trials import buscar_clinical_trials

docs = buscar_clinical_trials("intracranial hemorrhage", max_results=3)
for d in docs:
    print(d["title"])
    print(d["link"])