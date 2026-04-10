"""
NIVARAN — OCR Module
Two-stage pipeline for document text extraction:
  1. Direct text extraction via PyPDF2 (fast, free, works offline)
  2. Gemini Vision API fallback for scanned/image-based documents

Privacy: Files are processed in-memory only. No user documents are persisted.
"""

import os
import io
import base64
from dotenv import load_dotenv, find_dotenv

# ───────────────────────────────────────────────────────
# Load .env IMMEDIATELY — before anything else touches env vars
# ───────────────────────────────────────────────────────
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_ENV_PATH = os.path.join(_BACKEND_DIR, '.env')

if os.path.exists(_ENV_PATH):
    load_dotenv(_ENV_PATH, override=True)
else:
    load_dotenv(find_dotenv(), override=True)

# Read key — support BOTH common variable names
_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

# Filter out placeholder values
if _api_key and (_api_key.startswith('your_') or _api_key == 'your_gemini_api_key_here'):
    _api_key = None

# Startup diagnostic
if _api_key:
    _masked = _api_key[:8] + "..." + _api_key[-4:]
    print(f"[OCR] API Key loaded: YES ({_masked}, {len(_api_key)} chars)")
else:
    print("[OCR] API Key loaded: NO — CHECK .env FILE")

# ───────────────────────────────────────────────────────
# LAZY-INITIALIZED Gemini client — never at module level
# ───────────────────────────────────────────────────────
_client_configured = False
MODEL_NAME = 'gemini-2.5-flash'

# Max pages to send to Gemini (prevents timeout on large PDFs)
MAX_PDF_PAGES_FOR_GEMINI = 4


def _ensure_client():
    """Lazily configure the Gemini client on first use."""
    global _client_configured, _api_key

    if _client_configured:
        return True

    if not _api_key:
        load_dotenv(_ENV_PATH, override=True)
        _api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if _api_key and _api_key.startswith('your_'):
            _api_key = None

    if not _api_key:
        return False

    import google.generativeai as genai
    genai.configure(api_key=_api_key)
    _client_configured = True
    print("[OCR] Gemini client configured successfully.")
    return True


def extract_text_from_file(file_bytes, filename, mime_type=None):
    """
    Extract text from an uploaded document.

    Strategy:
      - PDF: Try PyPDF2 direct text extraction first (fast, no API call).
            If text is too short (scanned PDF), fall back to Gemini Vision.
      - Images: Send directly to Gemini Vision.

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

        # ── PDF: Try direct text extraction first ──────────────────────
        if mime_type == 'application/pdf':
            return _extract_from_pdf(file_bytes, filename)

        # ── Image: Send directly to Gemini Vision ──────────────────────
        return _extract_via_gemini(file_bytes, mime_type)

    except Exception as e:
        return {
            'text': '',
            'confidence': 0.0,
            'error': f'Document processing failed: {str(e)}'
        }


def _extract_from_pdf(file_bytes, filename):
    """
    Two-stage PDF extraction:
    1. PyPDF2 direct text read (instant, no API call)
    2. If text < 100 chars (scanned/image PDF), use Gemini on first N pages
    """
    # Stage 1: Try PyPDF2 direct text extraction
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        print(f"[OCR] PDF has {total_pages} page(s) — attempting direct text extraction")

        extracted_pages = []
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ''
                if text.strip():
                    extracted_pages.append(f"--- Page {i+1} ---\n{text.strip()}")
            except Exception as pg_err:
                print(f"[OCR] Page {i+1} text extraction failed: {pg_err}")
                continue

        full_text = '\n\n'.join(extracted_pages)

        # If we got substantial text, it's a text-based PDF — use it directly
        if len(full_text.strip()) >= 150:
            print(f"[OCR] Direct text extraction succeeded ({len(full_text)} chars, {total_pages} pages)")
            return {
                'text': full_text.strip(),
                'confidence': 0.95,
                'error': None
            }

        print(f"[OCR] Direct text too short ({len(full_text)} chars) — likely scanned. Falling back to Gemini Vision.")

    except Exception as e:
        print(f"[OCR] PyPDF2 extraction failed: {e} — falling back to Gemini Vision")

    # Stage 2: Scanned PDF — send raw bytes to Gemini
    # Limit to first MAX_PDF_PAGES_FOR_GEMINI pages to avoid timeout
    try:
        import PyPDF2
        from pypdf import PdfWriter  # Try pypdf if available

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)

        if total_pages > MAX_PDF_PAGES_FOR_GEMINI:
            print(f"[OCR] PDF has {total_pages} pages — truncating to first {MAX_PDF_PAGES_FOR_GEMINI} for Gemini")
            writer = PyPDF2.PdfWriter()
            for i in range(min(MAX_PDF_PAGES_FOR_GEMINI, total_pages)):
                writer.add_page(reader.pages[i])
            buf = io.BytesIO()
            writer.write(buf)
            pdf_bytes_to_send = buf.getvalue()
        else:
            pdf_bytes_to_send = file_bytes

    except Exception:
        # If page limiting fails, just send the whole file
        pdf_bytes_to_send = file_bytes

    return _extract_via_gemini(pdf_bytes_to_send, 'application/pdf')


def _extract_via_gemini(file_bytes, mime_type):
    """Send file bytes to Gemini Vision for text extraction."""
    if not _ensure_client():
        return {
            'text': '',
            'confidence': 0.0,
            'error': 'Gemini API key not configured. Set GEMINI_API_KEY in nivaran-backend/.env'
        }
    return _call_with_retry(file_bytes, mime_type)


def _call_with_retry(file_bytes, mime_type, max_attempts=3):
    """
    Call Gemini API with exponential backoff retry on 429 rate-limit errors.
    Attempts: 1st immediately, 2nd after 20s, 3rd after 40s.
    """
    import time
    import google.generativeai as genai

    model = genai.GenerativeModel(MODEL_NAME)

    # Use inline_data with base64 — most compatible across SDK versions
    file_part = {
        'inline_data': {
            'mime_type': mime_type,
            'data': base64.b64encode(file_bytes).decode('utf-8')
        }
    }

    prompt = (
        "Extract ALL text from this document exactly as written. "
        "Preserve the original formatting, numbers, dates, and special characters. "
        "Do not summarize or interpret — just extract the raw text content. "
        "If the document is in Hindi or a mix of Hindi and English, extract both. "
        "At the end, on a new line, rate the document quality from 0 to 100 "
        "in this exact format: QUALITY_SCORE: <number>"
    )

    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[OCR] Gemini API call attempt {attempt}/{max_attempts} (model: {MODEL_NAME})")
            response = model.generate_content([prompt, file_part])

            if response and response.text:
                text, confidence = _parse_quality_score(response.text.strip())
                print(f"[OCR] Extraction successful ({len(text)} chars, confidence: {confidence:.2f})")
                return {'text': text.strip(), 'confidence': confidence, 'error': None}
            else:
                return {'text': '', 'confidence': 0.0, 'error': 'Gemini returned empty response'}

        except Exception as e:
            last_error = str(e)
            is_rate_limit = '429' in last_error or 'RESOURCE_EXHAUSTED' in last_error

            if is_rate_limit and attempt < max_attempts:
                wait = 20 * attempt  # 20s, then 40s
                print(f"[OCR] Rate limit hit — waiting {wait}s before retry {attempt+1}...")
                time.sleep(wait)
            else:
                print(f"[OCR] API call failed (attempt {attempt}): {last_error[:100]}")
                break

    if last_error and ('429' in last_error or 'RESOURCE_EXHAUSTED' in last_error):
        return {
            'text': '',
            'confidence': 0.0,
            'error': 'RATE_LIMIT: Gemini API quota exceeded. Please wait 60 seconds and try again.'
        }

    return {'text': '', 'confidence': 0.0, 'error': f'OCR extraction failed: {last_error}'}


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


def _parse_quality_score(raw_text):
    """
    Parse the QUALITY_SCORE from the end of Gemini's response.
    Returns (clean_text, confidence_float).
    """
    lines = raw_text.split('\n')
    confidence = 0.85
    text_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith('QUALITY_SCORE:'):
            try:
                score_str = stripped.split(':', 1)[1].strip()
                score_str = ''.join(c for c in score_str if c.isdigit() or c == '.')
                score = float(score_str)
                confidence = min(score / 100.0, 1.0)
            except (ValueError, IndexError):
                confidence = 0.85
        else:
            text_lines.append(line)

    return '\n'.join(text_lines), confidence
