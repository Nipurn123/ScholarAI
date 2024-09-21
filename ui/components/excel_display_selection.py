import streamlit as st

def display_and_select_faculty(df):
    st.subheader("Select Faculty Members")
    
    faculty_names = df['Faculty Name'].tolist()
    
    # Selectbox for faculty selection with dynamic filtering
    selected_faculty = st.selectbox(
        "Select a faculty member:",
        options=faculty_names,
        format_func=lambda x: x,
        key="faculty_select"
    )
    
    return selected_faculty if selected_faculty else None
