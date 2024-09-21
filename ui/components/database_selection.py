import streamlit as st

def select_databases():
    st.subheader("Select Databases")
    databases = {
        "Google Scholar": st.checkbox("Google Scholar", value=True),
        "DBLP": st.checkbox("DBLP")
    }
    return [db for db, selected in databases.items() if selected]