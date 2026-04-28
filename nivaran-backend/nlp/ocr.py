"""
NIVARAN — OCR Module
Offline text extraction using PyPDF2 and EasyOCR.
Privacy: Files are processed in-memory only. No API calls, no external services.
"""

import io
import numpy as np
from PIL import Image

# ───────────────────────────────────────────────────────
# Lazy-loaded EasyOCR singleton (avoids ~100MB reload per request)
# ───────────────────────────────────────────────────────
_reader = None


def _get_easyocr_reader():
    """Get or create the EasyOCR reader singleton."""
    global _reader
    if _reader is None:
        import easyocr
        print("[OCR] Initializing EasyOCR reader (first request only)...")
        _reader = easyocr.Reader(['en', 'hi'], gpu=False)
        print("[OCR] EasyOCR reader ready.")
    return _reader


def extract_text_from_file(file_bytes, filename, mime_type=None):
    """
    Extract text from an uploaded document completely offline.

    Handles:
    - Text-based PDFs via PyPDF2
    - Images (PNG, JPG, WebP, etc.) via EasyOCR

    Returns:
        dict: {
            'text': str,
            'confidence': float (0.0–1.0),
            'error': str or None
        }
    """
    try:
        if mime_type is None:
            mime_type = _detect_mime_type(filename)

        if mime_type is None:
            return {
                'text': '',
                'confidence': 0.0,
                'error': f'Unsupported file type: {filename}. Please upload a PDF, PNG, JPG, or WebP.'
            }

        if mime_type == 'application/pdf':
            return _extract_from_pdf(file_bytes)

        return _extract_via_easyocr(file_bytes)

    except Exception as e:
        return {
            'text': '',
            'confidence': 0.0,
            'error': f'Offline OCR failed: {str(e)}'
        }


def _extract_from_pdf(file_bytes):
    """Extract text from a text-based PDF using PyPDF2."""
    import PyPDF2
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        extracted_pages = []
        for page in pdf_reader.pages:
            text = page.extract_text() or ''
            if text.strip():
                extracted_pages.append(text.strip())

        full_text = '\n\n'.join(extracted_pages)

        if len(full_text.strip()) > 100:
            return {
                'text': full_text.strip(),
                'confidence': 0.95,
                'error': None
            }

        # PDF has no extractable text — likely scanned
        return {
            'text': '',
            'confidence': 0.0,
            'error': 'PDF appears to be scanned/image-based. Please upload as an image (JPG/PNG) for offline OCR.'
        }

    except Exception as e:
        return {
            'text': '',
            'confidence': 0.0,
            'error': f'PDF read error: {str(e)}'
        }


def _extract_via_easyocr(file_bytes):
    """Extract text from an image using EasyOCR (offline)."""
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
        img_array = np.array(image)

        reader = _get_easyocr_reader()
        # detail=1 gives us confidence scores; paragraph=False for per-line results
        results = reader.readtext(img_array)

        extracted_text = []
        confidences = []

        for bbox, text, prob in results:
            extracted_text.append(text)
            confidences.append(prob)

        full_text = '\n'.join(extracted_text)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        if not full_text.strip():
            return {
                'text': '',
                'confidence': 0.0,
                'error': 'No text detected in the image. Please upload a clearer document.'
            }

        return {
            'text': full_text.strip(),
            'confidence': float(avg_confidence),
            'error': None
        }

    except Exception as e:
        return {
            'text': '',
            'confidence': 0.0,
            'error': f'EasyOCR engine failed: {str(e)}'
        }


def _detect_mime_type(filename):
    """Detect MIME type from filename extension."""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    mime_map = {
        'pdf':  'application/pdf',
        'png':  'image/png',
        'jpg':  'image/jpeg',
        'jpeg': 'image/jpeg',
        'webp': 'image/webp',
        'gif':  'image/gif',
        'bmp':  'image/bmp',
        'tiff': 'image/tiff',
        'tif':  'image/tiff',
    }
    return mime_map.get(ext)
