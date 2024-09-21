import streamlit as st
import bibtexparser

def upload_bibtex():
    st.subheader("Upload BibTeX File")
    uploaded_file = st.file_uploader("Choose a BibTeX file", type="bib")
    if uploaded_file is not None:
        try:
            bibtex_str = uploaded_file.getvalue().decode("utf-8")
            bib_database = bibtexparser.loads(bibtex_str)
            st.success("File successfully uploaded and read!")
            return bib_database.entries
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None