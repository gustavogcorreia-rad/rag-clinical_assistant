# home.py

import streamlit as st

st.set_page_config(
    page_title="Assistente Digital – Hemorragia Intracraniana",
    layout="centered"
)

# ---------------------------
# TÍTULO
# ---------------------------
st.title("Assistente Digital para Manejo de Hemorragia Intracraniana")

# ---------------------------
# TEXTO INTRODUTÓRIO
# ---------------------------
st.markdown(
    """
Este protótipo avalia a **utilidade clínica de um assistente baseado em Inteligência Artificial**
para apoio ao **manejo inicial de hemorragias intracranianas**, a partir de **evidências científicas recentes**.

Os casos disponibilizados para avaliação são **baseados em pacientes reais**, adaptados exclusivamente
para esta simulação educacional e científica.

---

### Fluxo previsto da ferramenta

O fluxo completo do sistema inclui:

- Varredura das tomografias computadorizadas de crânio por um **modelo de IA desenvolvido pelo autor**,  
  capaz de **detectar e classificar hemorragias intracranianas**;
- Direcionamento automático dos casos com **alta probabilidade de hemorragia** para este  
  **Assistente Digital de apoio à decisão clínica**;
- Geração de recomendações iniciais baseadas em **literatura científica selecionada (RAG + LLM)**.

Após a sua avaliação, peço a gentileza de preencher o **formulário de avaliação** disponibilizado ao final.

Cada caso abaixo é **independente** e pode ser avaliado separadamente.
"""
)

st.divider()

# ---------------------------
# LINKS GERAIS
# ---------------------------
st.subheader("Materiais para avaliação")

st.markdown(
    """
- 📄 **Informações clínicas completas e exemplos de imagem (PDF):**  
  👉 [Clique aqui para acessar o documento](https://drive.google.com/file/d/1xyC8AhtCyDOBHF1b_VGrngbC2a9klHhn/view?usp=sharing)

- 📝 **Formulário de avaliação da ferramenta:**  
  👉 [Clique aqui para preencher o formulário](https://docs.google.com/forms/d/e/1FAIpQLSfowzwinA5Axy1mcM1J-LB0u1hw4MaCLbn61YwlNa-XNzp1AA/viewform?usp=publish-editor)
"""
)

st.divider()

# ---------------------------
# CASOS
# ---------------------------
st.subheader("Casos clínicos para avaliação")

st.markdown(
    """
Avalie os casos abaixo utilizando o Assistente Digital correspondente.
"""
)

# Função utilitária para evitar repetição
def bloco_caso(numero, url_app):
    st.markdown(f"""
### Caso {numero:02d}

- 🤖 **Assistente Digital:**  
  👉 [Acessar o Assistente – Caso {numero:02d}]({url_app})
""")

# URLs dos apps (ajuste depois que o Streamlit gerar os links)
bloco_caso(1, "LINK_STREAMLIT_CASE01")
bloco_caso(2, "LINK_STREAMLIT_CASE02")
bloco_caso(3, "LINK_STREAMLIT_CASE03")
bloco_caso(4, "LINK_STREAMLIT_CASE04")
bloco_caso(5, "LINK_STREAMLIT_CASE05")

st.divider()

# ---------------------------
# FORMULÁRIO (REPETIDO AO FINAL)
# ---------------------------
st.subheader("Formulário de avaliação")

st.markdown(
    """
Após a sua avaliação dos **cinco casos**, por favor preencha o formulário abaixo:

👉 [Clique aqui para preencher o formulário de avaliação](https://docs.google.com/forms/d/e/1FAIpQLSfowzwinA5Axy1mcM1J-LB0u1hw4MaCLbn61YwlNa-XNzp1AA/viewform?usp=publish-editor)
"""
)

st.divider()

# ---------------------------
# RODAPÉ
# ---------------------------
st.markdown(
    """
<p style="font-size: 0.9em; color: gray;">
© Gustavo Gumz Correia, MD.<br>
Pesquisa de Doutoramento em Engenharia Biomédica<br>
Universidade do Minho, Braga, Portugal.
</p>
""",
    unsafe_allow_html=True
)