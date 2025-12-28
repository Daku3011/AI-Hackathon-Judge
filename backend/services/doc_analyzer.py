import io
from pypdf import PdfReader

def extract_text_from_pdf(file_content):
    """
    Extracts text from PDF file content (bytes).
    """
    try:
        # Create a file-like object from bytes
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
