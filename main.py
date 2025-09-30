# main.py

from core.parser import extract_text_from_pdf
from core.extractor import extract_metadata_from_text # <-- Import our new function
import pprint # Use pprint for cleaner dictionary printing

# Make sure to place a PDF in the 'documents' folder
PDF_FILE_PATH = "documents/R1.pdf" 

def run():
    print("--- 1. Starting PDF Text Extraction ---")
    extracted_text = extract_text_from_pdf(PDF_FILE_PATH)

    if not extracted_text:
        print("Failed to extract text. Exiting.")
        return

    print(f"Successfully extracted {len(extracted_text)} characters.")
    print("\n--- 2. Starting Metadata Extraction with LLM ---")
    
    metadata = extract_metadata_from_text(extracted_text)

    if metadata:
        print("\n--- ✅ Successfully Extracted Metadata ---")
        pprint.pprint(metadata)
        print("-------------------------------------------\n")
    else:
        print("\n--- ❌ Failed to extract metadata ---")

if __name__ == "__main__":
    run()