import fitz 

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a given PDF file.

    Args:
        pdf_path (str): The file path to the PDF.

    Returns:
        str: The concatenated text from all pages of the PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""