"""
PDF text extraction using PyMuPDF. Fast, local, no AI needed.
"""

import os
import zipfile
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def _check_fitz():
    if fitz is None:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")


def extract_text(pdf_path: str) -> str:
    """Extract full text from a PDF. Handles ZIP-wrapped PDFs."""
    _check_fitz()

    path = _unwrap_zip(pdf_path)
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text.strip()


def extract_daily_report(pdf_path: str) -> dict:
    """Extract structured content from a Procore daily report PDF."""
    text = extract_text(pdf_path)
    return {
        "path": pdf_path,
        "filename": os.path.basename(pdf_path),
        "full_text": text,
        "length": len(text),
    }


def extract_schedule_table(pdf_path: str) -> str:
    """Extract text from 3-week look-ahead PDF, preserving table structure."""
    _check_fitz()
    path = _unwrap_zip(pdf_path)
    doc = fitz.open(path)
    text = ""
    for page in doc:
        # Use dict mode for better table extraction
        blocks = page.get_text("dict")["blocks"]
        lines = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = " ".join(span["text"] for span in line["spans"]).strip()
                    if line_text:
                        lines.append(line_text)
        text += "\n".join(lines) + "\n\n"
    doc.close()
    return text.strip()


def extract_meeting_minutes(pdf_path: str) -> str:
    """Extract full text from meeting minutes PDF."""
    return extract_text(pdf_path)


def _unwrap_zip(pdf_path: str) -> str:
    """If a PDF is actually a ZIP file, extract the real PDF from within."""
    try:
        if zipfile.is_zipfile(pdf_path):
            with zipfile.ZipFile(pdf_path) as zf:
                pdf_names = [n for n in zf.namelist() if n.lower().endswith('.pdf')]
                if pdf_names:
                    tmp = tempfile.mktemp(suffix='.pdf')
                    with open(tmp, 'wb') as out:
                        out.write(zf.read(pdf_names[0]))
                    return tmp
    except Exception:
        pass
    return pdf_path
