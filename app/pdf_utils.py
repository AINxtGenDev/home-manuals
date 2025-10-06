"""PDF processing utilities."""

import hashlib
from pathlib import Path
from typing import Tuple

from pypdf import PdfReader


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal hash string
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_pdf_text(file_path: Path) -> Tuple[int, str]:
    """Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (number_of_pages, extracted_text)
    """
    try:
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)

        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n".join(text_parts)
        return num_pages, full_text

    except Exception as e:
        # Log error but don't fail upload
        print(f"Error extracting PDF text: {e}")
        return 0, ""


def validate_pdf_file(file_path: Path) -> bool:
    """Validate that a file is a valid PDF.

    Args:
        file_path: Path to the file

    Returns:
        True if valid PDF, False otherwise
    """
    try:
        # Check magic bytes
        with open(file_path, "rb") as f:
            header = f.read(5)
            if header != b"%PDF-":
                return False

        # Try to open with pypdf
        PdfReader(file_path)
        return True

    except Exception:
        return False


def safe_filename(filename: str) -> str:
    """Generate a safe filename by keeping only alphanumeric and basic punctuation.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Keep only alphanumeric, dots, hyphens, underscores
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_ ")
    return "".join(c if c in safe_chars else "_" for c in filename)
