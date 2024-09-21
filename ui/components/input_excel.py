import streamlit as st
import pandas as pd

def upload_faculty_excel():
    st.subheader("Upload Faculty Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("File successfully uploaded and read!")
            return df
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None