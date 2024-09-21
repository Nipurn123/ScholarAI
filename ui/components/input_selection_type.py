import streamlit as st

def select_input_type():
    input_type = st.radio("Select input type:", ("Excel", "BibTeX"))
    return input_type