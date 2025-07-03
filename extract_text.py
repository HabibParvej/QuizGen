import pdfplumber
import docx
import io

def extract_text(file, file_type):
    """Extract text from uploaded file based on its type"""
    if file_type == "application/pdf":
        return extract_pdf_text(file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_docx_text(file)
    elif file_type == "text/plain":
        return extract_txt_text(file)
    else:
        raise ValueError("Unsupported file format")

def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(io.BytesIO(file.read())) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_docx_text(file):
    doc = docx.Document(io.BytesIO(file.read()))
    return "\n".join([para.text for para in doc.paragraphs])

def extract_txt_text(file):
    return file.read().decode("utf-8")