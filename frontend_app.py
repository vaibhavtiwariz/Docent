# frontend_app.py

import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Intelli-Curate",
    page_icon="✨",
    layout="centered"
)

# --- App Title ---
st.title("Intelli-Curate ✨")
st.write("Your AI-Powered Curation Assistant for Research Repositories")

# --- API Endpoint ---
API_URL = "http://127.0.0.1:8000/curate-document/"

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Upload a research paper (PDF)",
    type="pdf"
)

# --- Main Logic ---
if uploaded_file is not None:
    with st.spinner("Our AI agent is reading the paper... This may take a moment."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(API_URL, files=files, timeout=300)

            if response.status_code == 200:
                st.success("Successfully extracted metadata!")
                metadata = response.json()
                
                # --- Human-in-the-Loop Interface ---
                st.subheader("Please review and edit the extracted metadata:")
                
                edited_title = st.text_input(
                    "Title", 
                    value=metadata.get("title", "Title not found")
                )
                
                authors_str = ", ".join(metadata.get("authors", []))
                edited_authors_str = st.text_area(
                    "Authors (comma-separated)", 
                    value=authors_str,
                    height=100
                )
                
                if st.button("Save Corrected Metadata", key="save_correction"):
                    try:
                        payload = {
                            "filename": uploaded_file.name,
                            "extracted_title": metadata.get("title", ""),
                            "extracted_authors": metadata.get("authors", []),
                            "corrected_title": edited_title,
                            "corrected_authors": [
                                a.strip() for a in edited_authors_str.split(",") if a.strip()
                            ],
                        }
                        save_resp = requests.post(
                            "http://127.0.0.1:8000/save-correction/",
                            json=payload,
                            timeout=30,
                        )
                        if save_resp.status_code == 200:
                            st.success(
                                "Correction saved! Your review improves future extractions."
                            )
                        else:
                            st.error(
                                f"Could not save correction (status {save_resp.status_code})."
                            )
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not save correction: {e}")

            else:
                error_details = response.json().get("detail", "Unknown error")
                st.error(f"API Error: {error_details} (Status Code: {response.status_code})")

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the backend API. Please ensure it's running. Error: {e}")