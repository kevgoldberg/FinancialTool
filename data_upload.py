import streamlit as st
import pandas as pd

def upload_data():
    """
    Handles file upload and returns a DataFrame if a file is uploaded, else None.
    """
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx"], label_visibility="collapsed")
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            return df, uploaded_file
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None, None
    return None, None
