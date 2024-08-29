import streamlit as st

def agregar_estilo_css():
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)