"""
NIVARAN — OCR Module
Uses Google Gemini 1.5 Flash API to extract text from document images and PDFs.

Privacy: Files are processed in-memory only. No user documents are persisted.
"""

import os
from dotenv import load_dotenv, find_dotenv

# ───────────────────────────────────────────────────────
# Load .env IMMEDIATELY — before anything else touches env vars
# Uses explicit path + find_dotenv fallback for robustness
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
    print(f"[OCR] Looked for .env at: {_ENV_PATH}")
    print(f"[OCR] .env exists: {os.path.exists(_ENV_PATH)}")

# ───────────────────────────────────────────────────────
# LAZY-INITIALIZED Gemini client
# This is the key fix: do NOT call genai.configure() at module level
# because it runs before app.py's load_dotenv() on some import orders.
# Instead, configure on first actual use.
# ───────────────────────────────────────────────────────
_client_configured = False

# gemini-2.5-flash: separate quota pool from 2.0-flash, good free-tier limits
MODEL_NAME = 'gemini-2.5-flash'


def _ensure_client():
    """Lazily configure the Gemini client on first use."""
    global _client_configured, _api_key

    if _client_configured:
        return True

    # Re-read key in case .env was loaded later by app.py
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
    print(f"[OCR] Gemini client configured successfully.")
    return True


def extract_text_from_file(file_bytes, filename, mime_type=None):
    """
    Extract text from an uploaded document using Gemini 1.5 Flash Vision API.

    Args:
        file_bytes (bytes): Raw bytes of the uploaded file.
        filename (str): Original filename (used for MIME type detection).
        mime_type (str, optional): Explicit MIME type override.

    Returns:
        dict: {
            'text': str — extracted text,
            'confidence': float — estimated OCR quality (0.0 to 1.0),
            'error': str or None — error message if extraction failed
        }
    """
    # Lazy-init the client
    if not _ensure_client():
        return {
            'text': '',
            'confidence': 0.0,
            'error': 'Gemini API key not configured. Set GEMINI_API_KEY in nivaran-backend/.env'
        }

    # Determine MIME type once — single API call per upload
    if mime_type is None:
        mime_type = _detect_mime_type(filename)

    if mime_type is None:
        return {
            'text': '',
            'confidence': 0.0,
            'error': f'Unsupported file type: {filename}'
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
    file_part = {'mime_type': mime_type, 'data': file_bytes}
    prompt = (
        "Extract ALL text from this document image/PDF exactly as written. "
        "Preserve the original formatting, numbers, dates, and special characters. "
        "Do not summarize or interpret — just extract the raw text content. "
        "If the document is in Hindi or a mix of Hindi and English, extract both. "
        "At the end, on a new line, rate the image/document quality from 0 to 100 "
        "in this exact format: QUALITY_SCORE: <number>"
    )

    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[OCR] API call attempt {attempt}/{max_attempts} (model: {MODEL_NAME})")
            response = model.generate_content([prompt, file_part])

            if response and response.text:
                text, confidence = _parse_quality_score(response.text.strip())
                return {'text': text.strip(), 'confidence': confidence, 'error': None}
            else:
                return {'text': '', 'confidence': 0.0, 'error': 'Gemini returned empty response'}

        except Exception as e:
            last_error = str(e)
            is_rate_limit = '429' in last_error or 'RESOURCE_EXHAUSTED' in last_error

            if is_rate_limit and attempt < max_attempts:
                wait = 20 * attempt  # 20s, then 40s
                print(f"[OCR] Rate limit hit — waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                break  # Non-retryable error or max attempts reached

    # Return user-friendly message for rate limit errors
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
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'webp': 'image/webp',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'tiff': 'image/tiff',
        'tif': 'image/tiff',
    }
    return mime_map.get(ext)


def _parse_quality_score(raw_text):
    """
    Parse the quality score from Gemini's response.
    Returns (clean_text, confidence_float).
    """
    lines = raw_text.split('\n')
    confidence = 0.85  # Default confidence if not parseable
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
