import streamlit as st

st.set_page_config(
    page_title="Assistente Clínico – Hemorragia Intracraniana",
    layout="centered"
)


st.title("Assistente Digital para Manejo de Hemorragia Intracraniana")

st.markdown(
    """
    Este protótipo avalia a utilidade clínica de um **assistente baseado em IA**
    para apoio ao **manejo inicial de hemorragias intracranianas**, a partir de
    evidências científicas recentes.

    Cada caso abaixo é independente e pode ser avaliado separadamente.
    """
)

st.divider()

st.header("Casos clínicos")

def caso_card(titulo, link_app, link_pdf, link_form):
    st.subheader(titulo)
    st.markdown(f"🧠 **Assistente digital:** [{link_app}]({link_app})")
    st.markdown(f"📄 **Informação clínica:** [{link_pdf}]({link_pdf})")
    st.markdown(f"📝 **Formulário de avaliação:** [{link_form}]({link_form})")
    st.divider()

caso_card(
    "CASO 01 – Hemorragia Subaracnoide",
    "Case_01",
    "https://link-pdf-caso01",
    "https://forms.gle/form-caso01"
)

caso_card(
    "CASO 02 – Hematoma Subdural",
    "Case_02",
    "https://link-pdf-caso02",
    "https://forms.gle/form-caso02"
)