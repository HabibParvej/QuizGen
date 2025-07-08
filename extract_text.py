
import PyPDF2
from docx import Document

def extract_text(file, file_type):
    """
    Extracts text from uploaded files based on file type (PDF, DOCX, TXT).
    
    Args:
        file: Uploaded file object
        file_type: Type of the file ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain')
    
    Returns:
        str: Extracted text
    """
    text = ""
    
    try:
        if file_type == "application/pdf":
            # Handle PDF files
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Handle DOCX files
            doc = Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        
        elif file_type == "text/plain":
            # Handle TXT files
            text = file.read().decode("utf-8")
        
        else:
            raise ValueError("Unsupported file type")
        
        # Clean up text
        text = text.strip()
        if not text:
            raise ValueError("No text could be extracted from the file")
        
        return text
    
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")
