import io
from pypdf import PdfReader

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extracts text from PDF file content (bytes).
    """
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text_pages = []
        for i, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_pages.append(f"--- Page {i} ---\n" + page_text.strip())
            except Exception:
                # Skip pages that cause extraction errors
                continue
        return "\n\n".join(text_pages) if text_pages else "Empty or scanned PDF without extractable text."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_doc(file_content: bytes, filename: str) -> str:
    """
    Extracts text from supported document types (.pdf, .md, .txt).
    """
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith((".txt", ".md", ".markdown", ".rst")):
        try:
            return file_content.decode("utf-8", errors="replace")
        except Exception as e:
            return f"Error decoding text document: {e}"
    return f"Unsupported document format: {filename}"
