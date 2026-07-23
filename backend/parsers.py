"""
Text extraction for uploaded complaint documents.
No OCR — text-based PDFs only, as per spec.
"""
import email
from email import policy
from io import BytesIO

import docx  # python-docx
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = docx.Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs).strip()


def extract_text_from_eml(file_bytes: bytes) -> str:
    msg = email.message_from_bytes(file_bytes, policy=policy.default)
    subject = msg.get("subject", "")
    sender = msg.get("from", "")
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
    else:
        body = msg.get_content()
    return f"From: {sender}\nSubject: {subject}\n\n{body}".strip()


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore").strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    if ext == "docx":
        return extract_text_from_docx(file_bytes)
    if ext == "eml":
        return extract_text_from_eml(file_bytes)
    if ext == "txt":
        return extract_text_from_txt(file_bytes)
    raise ValueError(f"Unsupported file type: .{ext}")
