import os

def extract_resume_text(path):
    extension = os.path.splitext(path)[1].lower()
    text = ""
    if extension == ".txt":
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            text = file.read()
    elif extension == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install pypdf with: pip install pypdf") from exc
        reader = PdfReader(path)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:
                raise ValueError("This PDF is password-protected. Please upload an unprotected file.") from exc
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif extension == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("Install python-docx with: pip install python-docx") from exc
        document = Document(path)
        parts = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                row_cells = []
                last_text = None
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text and cell_text != last_text:
                        row_cells.append(cell_text)
                        last_text = cell_text
                if row_cells:
                    parts.append(" | ".join(row_cells))
        text = "\n".join(parts)
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX or TXT.")

    # Sanitize null bytes and normalize whitespace
    text = text.replace("\x00", "")
    return text.strip()
