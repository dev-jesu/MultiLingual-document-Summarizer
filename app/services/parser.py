import io
import fitz  # PyMuPDF
import docx
from docx.opc.exceptions import OpcError
import zipfile


def parse_pdf(file_bytes: bytes) -> tuple[str, int]:
    """
    Parses PDF file bytes using PyMuPDF (fitz).
    
    Preserves page order and paragraph spacing, gracefully handles page-level parsing
    errors, detects password protection, and efficiently processes large documents.
    
    Args:
        file_bytes (bytes): Raw bytes of the PDF file.
        
    Returns:
        tuple[str, int]: A tuple containing (extracted_text, total_page_count).
        
    Raises:
        ValueError: If file is empty, corrupted, or password-protected.
    """
    if not file_bytes:
        raise ValueError("File content is empty.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Corrupted or invalid PDF file: {str(e)}")

    try:
        if doc.is_encrypted or doc.needs_pass:
            raise ValueError("PDF is password-protected and cannot be parsed.")

        total_pages = doc.page_count
        if total_pages == 0:
            raise ValueError("PDF file contains no pages.")

        page_texts: list[str] = []
        for i in range(total_pages):
            try:
                page = doc.load_page(i)
                text = page.get_text("text")
                if text:
                    page_texts.append(text.strip())
            except Exception:
                # Gracefully skip unreadable or corrupted single page
                continue

        full_text = "\n\n".join(page_texts)
        return full_text, total_pages, page_texts
    finally:
        doc.close()


def parse_docx(file_bytes: bytes) -> tuple[str, None, list[str]]:
    """
    Parses DOCX file bytes using python-docx.
    
    Preserves paragraph order while ignoring headers, footers, images, and tables.
    
    Args:
        file_bytes (bytes): Raw bytes of the DOCX file.
        
    Returns:
        tuple[str, None, list[str]]: A tuple containing (extracted_text, None, paragraphs).
        
    Raises:
        ValueError: If file is empty, corrupted, or not a valid DOCX document.
    """
    if not file_bytes:
        raise ValueError("File content is empty.")

    try:
        doc_stream = io.BytesIO(file_bytes)
        document = docx.Document(doc_stream)
    except (OpcError, zipfile.BadZipFile, KeyError, Exception) as e:
        raise ValueError(f"Corrupted or invalid DOCX file: {str(e)}")

    paragraphs: list[str] = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)
    return full_text, None, paragraphs
