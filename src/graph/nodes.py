# src/graph/nodes.py

class ClinicalNode:
    """
    Representa um fator clínico ou característica relevante para a tomada de decisão.
    """
    def __init__(self, name: str, value):
        self.name = name      # Exemplo: "hypertension"
        self.value = value    # Exemplo: True/False, float, str

    def __repr__(self):
        return f"{self.name}: {self.value}"

# Lista de possíveis fatores clínicos utilizados no sistema
CLINICAL_FACTORS = [
    # Output do modelo
    "hemorrhage_type",
    "hemorrhage_probability",
    
    # 1. Histórico Clínico e Comorbidades
    "hypertension",
    "diabetes",
    "chronic_liver_disease",
    "coagulopathy",
    "prior_stroke",
    
    # 2. Estado clínico atual
    "altered_consciousness",
    "focal_deficit",
    "severe_headache",
    "seizures",
    
    # 3. Uso de medicamentos além dos anticoagulantes
    "antiplatelet_use",
    "substance_abuse",
    
    # 4. Contexto do evento
    "recent_trauma",
    "prior_neurosurgery",
    "vascular_malformation",
    
    # 5. Parâmetros laboratoriais críticos
    "thrombocytopenia",
    "high_inr",
    
    # 6. Dados logísticos importantes para conduta
    "neurosurgery_available",
    "transfer_planned"
]