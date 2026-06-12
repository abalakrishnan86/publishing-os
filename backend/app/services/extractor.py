import pdfplumber
import docx

from app.models.dbmodels import FileType


def extract_text(filepath: str, file_type: FileType) -> str:
    if file_type == FileType.TXT:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            return fh.read()

    if file_type == FileType.DOCX:
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if file_type == FileType.PDF:
        pages: list[str] = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)

    raise ValueError(f"Unsupported file type: {file_type}")


def count_words(text: str) -> int:
    return len(text.split())
