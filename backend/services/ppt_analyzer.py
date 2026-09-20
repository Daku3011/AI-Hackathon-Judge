from pptx import Presentation
import io

def extract_text_from_ppt(file_content: bytes) -> str:
    """
    Extracts text from a PPT/PPTX file content.
    Returns a string containing structured text from all slides and tables without duplication.
    """
    try:
        ppt_file = io.BytesIO(file_content)
        prs = Presentation(ppt_file)
        
        slide_texts = []
        for i, slide in enumerate(prs.slides, 1):
            slide_content = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text = paragraph.text.strip()
                        if text:
                            slide_content.append(text)
                elif shape.has_table:
                    for row in shape.table.rows:
                        row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_text:
                            slide_content.append(" | ".join(row_text))
                elif hasattr(shape, "text") and shape.text.strip():
                    slide_content.append(shape.text.strip())

            if slide_content:
                slide_texts.append(f"--- Slide {i} ---\n" + "\n".join(slide_content))
                
        return "\n\n".join(slide_texts)
    except Exception as e:
        print(f"Error extracting text from PPT: {e}")
        return ""
