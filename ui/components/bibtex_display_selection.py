import streamlit as st

def display_and_select_papers(bibtex_entries):
    st.subheader("Select Papers")

    # Search functionality
    search_term = st.text_input("Search for a paper:")
    if search_term:
        filtered_entries = [entry for entry in bibtex_entries if search_term.lower() in entry.get('title', '').lower()]
    else:
        filtered_entries = bibtex_entries

    # Display and select
    selected_papers = []
    for entry in filtered_entries:
        title = entry.get('title', 'Untitled')
        authors = entry.get('author', 'Unknown')
        if st.checkbox(f"{title} - {authors}", key=title):
            selected_papers.append(entry)

    return selected_papers