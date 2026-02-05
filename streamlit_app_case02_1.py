import streamlit as st
import pandas as pd
from datetime import datetime
import os
from src.agent import processar

st.set_page_config(page_title="Assistente de Hemorragia Intracraniana", layout="centered")

# Simulação de output do modelo IA (na integração real, será dinâmico)
# LEMBRAR DE ADICIONAR NOME DO PACIENTE - PROVENIENTE DO MODELO DE DETECÇÃO
tipo_hemorragia = "intraparenchymal hemorrhage"
probabilidade = 0.90

st.title("Assistente de Conduta em Hemorragia Intracraniana")
st.markdown(f"**CASO 02 - feminino, 51 anos")
st.markdown(f"**Tipo de hemorragia mais provável detectada:** Intraparenquimatosa")
st.markdown(f"**Probabilidade:** {probabilidade * 100:.1f}%")

st.divider()

# 1. Histórico Clínico e Comorbidades
st.subheader("1. Histórico Clínico e Comorbidades")
has = st.checkbox("Hipertensão arterial sistêmica (HAS)")
diabetes = st.checkbox("Diabetes mellitus")
hepatic_disease = st.checkbox("Doença hepática crônica")
coagulopathy = st.checkbox("Coagulopatias congênitas ou adquiridas (ex.: hemofilia, trombocitopenia)")
prior_stroke = st.checkbox("História prévia de acidente vascular cerebral")

st.divider()

# 2. Estado clínico atual
st.subheader("2. Estado clínico atual")
altered_consciousness = st.checkbox("Alteração do nível de consciência")
focal_deficit = st.checkbox("Déficit neurológico focal")
severe_headache = st.checkbox("Cefaleia intensa ou súbita")
seizures = st.checkbox("Convulsões no contexto atual")

st.divider()

# 3. Uso de medicamentos além dos anticoagulantes
st.subheader("3. Uso de medicamentos além dos anticoagulantes")
antiplatelet = st.checkbox("Uso de antiagregantes plaquetários (ex.: AAS, clopidogrel)")
substance_abuse = st.checkbox("Uso de drogas ilícitas ou abuso de álcool")

st.divider()

# 4. Contexto do evento
st.subheader("4. Contexto do evento")
recent_trauma = st.checkbox("Queda ou trauma cranioencefálico recente")
prior_neurosurgery = st.checkbox("Craniotomia ou neurocirurgia prévia")
vascular_malformation = st.checkbox("Presença de malformações vasculares conhecidas (ex.: MAVs, aneurismas)")

st.divider()

# 5. Parâmetros laboratoriais críticos
st.subheader("5. Parâmetros laboratoriais críticos (se disponíveis)")
thrombocytopenia = st.checkbox("Plaquetopenia (<100.000/mm³)")
high_inr = st.checkbox("INR > 1.5")

st.divider()

# 6. Dados logísticos importantes para conduta
st.subheader("6. Dados logísticos importantes para conduta")
neurosurgery_available = st.checkbox("Disponibilidade de neurocirurgia no hospital")
transfer_planned = st.checkbox("Transferência para centro especializado prevista")

st.divider()

# Função para enviar dados ao agente
def processar_dados(dados_clinicos):
    resposta, referencias = processar(dados_clinicos)
    st.session_state['resposta'] = resposta
    st.session_state['referencias'] = referencias
    st.session_state['dados_clinicos'] = dados_clinicos
    st.success("Sugestão clínica baseada em evidência:")
    st.markdown(resposta)
    st.markdown(referencias)
    with st.expander("Ver dados clínicos enviados (internos)"):
        st.json(dados_clinicos)

# Botão para enviar dados
if st.button("Gerar sugestão de conduta baseada em evidências"):
    dados_clinicos = {
        "hemorrhage_type": tipo_hemorragia,
        "hemorrhage_probability": probabilidade,
        "hypertension": has,
        "diabetes": diabetes,
        "chronic_liver_disease": hepatic_disease,
        "coagulopathy": coagulopathy,
        "prior_stroke": prior_stroke,
        "altered_consciousness": altered_consciousness,
        "focal_deficit": focal_deficit,
        "severe_headache": severe_headache,
        "seizures": seizures,
        "antiplatelet_use": antiplatelet,
        "substance_abuse": substance_abuse,
        "recent_trauma": recent_trauma,
        "prior_neurosurgery": prior_neurosurgery,
        "vascular_malformation": vascular_malformation,
        "thrombocytopenia": thrombocytopenia,
        "high_inr": high_inr,
        "neurosurgery_available": neurosurgery_available,
        "transfer_planned": transfer_planned
    }
    processar_dados(dados_clinicos)

def registrar_feedback(resposta, referencias, dados_clinicos, util=True, log_path="feedback_log.csv"):
    linha = {
        "timestamp": datetime.now().isoformat(),
        "feedback": "positivo" if util else "negativo",
        "resposta": resposta[:300],
        "referencias": referencias,
        "dados_clinicos": str(dados_clinicos)
    }
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        df = pd.concat([df, pd.DataFrame([linha])], ignore_index=True)
    else:
        df = pd.DataFrame([linha])
    df.to_csv(log_path, index=False)

# Exibe feedback somente se resposta foi gerada
if 'resposta' in st.session_state and 'referencias' in st.session_state:
    st.markdown("#### Seu feedback nos ajuda a melhorar o sistema:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Útil para conduta"):
            registrar_feedback(
                st.session_state['resposta'],
                st.session_state['referencias'],
                st.session_state['dados_clinicos'],
                util=True
            )
            st.success("Obrigado pelo feedback positivo!")
    with col2:
        if st.button("👎 Não útil para conduta"):
            registrar_feedback(
                st.session_state['resposta'],
                st.session_state['referencias'],
                st.session_state['dados_clinicos'],
                util=False
            )
            st.info("Obrigado pelo feedback. Seu retorno será usado para aprimorar o sistema.")