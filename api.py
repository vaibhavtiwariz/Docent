# api.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Import our existing functions from the core module
from core.parser import extract_text_from_pdf
from core.extractor import extract_metadata_from_text
from core.store import init_db, save_correction
from pydantic import BaseModel
from typing import List

# Ensure the corrections database exists on startup
init_db()

# Initialize the FastAPI app
app = FastAPI(
    title="Intelli-Curate API",
    description="An API for intelligent metadata extraction from research papers.",
    version="1.0.0"
)

# Define a temporary directory to store uploaded files
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/curate-document/", tags=["Curation"])
async def curate_document(file: UploadFile = File(...)):
    """
    Accepts a PDF file, extracts metadata, and returns it as JSON.
    """
    # Check for valid file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)

    try:
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # --- Step 1: Parse Text from PDF ---
        print(f"Parsing text from {file.filename}...")
        raw_text = extract_text_from_pdf(temp_file_path)
        if not raw_text:
            raise HTTPException(status_code=500, detail="Failed to extract text from the PDF.")

        # --- Step 2: Extract Metadata with LLM ---
        print("Extracting metadata with the language model...")
        metadata = extract_metadata_from_text(raw_text)
        if not metadata:
            raise HTTPException(status_code=500, detail="The AI model failed to extract metadata.")
        
        print("Successfully extracted metadata.")
        return JSONResponse(status_code=200, content=metadata)

    except Exception as e:
        # Catch any other unexpected errors
        return JSONResponse(status_code=500, content={"error": f"An unexpected error occurred: {str(e)}"})
    finally:
        # Clean up: remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# This allows running the app directly with `python api.py` for simple testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


class CorrectionIn(BaseModel):
    filename: str
    extracted_title: str = ""
    extracted_authors: List[str] = []
    corrected_title: str = ""
    corrected_authors: List[str] = []


@app.post("/save-correction/", tags=["Curation"])
def save_correction_endpoint(correction: CorrectionIn):
    """
    Stores a human-reviewed correction (AI output vs. corrected values)
    in the local SQLite database. This closes the human-in-the-loop loop:
    corrections accumulate into an evaluation/improvement dataset.
    """
    try:
        row_id = save_correction(
            filename=correction.filename,
            extracted_title=correction.extracted_title,
            extracted_authors=correction.extracted_authors,
            corrected_title=correction.corrected_title,
            corrected_authors=correction.corrected_authors,
        )
        return JSONResponse(status_code=200, content={"status": "saved", "id": row_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save correction: {e}")