"""File text extraction using MarkItDown with plain-text fallbacks."""

import os
import tempfile
from pathlib import Path
from typing import Optional


class FileExtractor:
    """Extracts text content from uploaded files (PDF, DOCX, TXT, MD)."""

    def __init__(self) -> None:
        self._md = None
        self._md_loaded = False

    def _get_markitdown(self):
        """Lazy-load MarkItDown; return None if unavailable."""
        if self._md_loaded:
            return self._md
        self._md_loaded = True
        try:
            from markitdown import MarkItDown
            self._md = MarkItDown()
        except Exception:
            self._md = None
        return self._md

    def extract(self, uploaded_file) -> str:
        """
        Extract text from a Streamlit UploadedFile object.

        Falls back to UTF-8 decoding if MarkItDown is unavailable or fails.
        """
        suffix = Path(uploaded_file.name).suffix.lower()
        content = uploaded_file.read()

        # Plain text / markdown: no library needed
        if suffix in (".txt", ".md"):
            return content.decode("utf-8", errors="ignore").strip()

        # Try MarkItDown for PDF / DOCX
        md = self._get_markitdown()
        if md is not None:
            return self._extract_with_markitdown(md, content, suffix)

        # Last resort: raw decode (useful for text-ish formats)
        return content.decode("utf-8", errors="ignore").strip()

    def _extract_with_markitdown(self, md, content: bytes, suffix: str) -> str:
        tmp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            result = md.convert(tmp_path)
            text = result.text_content or ""
            return text.strip()
        except Exception as exc:
            return f"[Extraction error: {exc}]"
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
