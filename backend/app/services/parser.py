from pypdf import PdfReader
from io import BytesIO


def extract_text(file_content: bytes, filename: str):

    text = ""

    if filename.lower().endswith(".pdf"):
        pdf = PdfReader(BytesIO(file_content))

        for page in pdf.pages:
            text += page.extract_text() or ""

    else:
        text = file_content.decode("utf-8", errors="ignore")

    return text