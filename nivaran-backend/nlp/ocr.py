"""
NIVARAN — OCR Module
Uses Google Gemini 1.5 Flash API to extract text from document images and PDFs.

Privacy: Files are processed in-memory only. No user documents are persisted.
"""

import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ───────────────────────────────────────────────────────
# Gemini API Configuration
# ───────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("[NIVARAN][WARNING] GEMINI_API_KEY not set. OCR will not function.")

genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 1.5 Flash for fast, cost-effective OCR
MODEL_NAME = 'gemini-1.5-flash'


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
    try:
        # Determine MIME type
        if mime_type is None:
            mime_type = _detect_mime_type(filename)

        if mime_type is None:
            return {
                'text': '',
                'confidence': 0.0,
                'error': f'Unsupported file type: {filename}'
            }

        # Initialize the model
        model = genai.GenerativeModel(MODEL_NAME)

        # Prepare the file content for Gemini
        file_part = {
            'mime_type': mime_type,
            'data': file_bytes
        }

        # OCR prompt — instructs Gemini to extract text faithfully
        prompt = (
            "Extract ALL text from this document image/PDF exactly as written. "
            "Preserve the original formatting, numbers, dates, and special characters. "
            "Do not summarize or interpret — just extract the raw text content. "
            "If the document is in Hindi or a mix of Hindi and English, extract both. "
            "At the end, on a new line, rate the image/document quality from 0 to 100 "
            "in this exact format: QUALITY_SCORE: <number>"
        )

        # Call Gemini API
        response = model.generate_content([prompt, file_part])

        if response and response.text:
            raw_output = response.text.strip()

            # Parse quality score from response
            text, confidence = _parse_quality_score(raw_output)

            return {
                'text': text.strip(),
                'confidence': confidence,
                'error': None
            }
        else:
            return {
                'text': '',
                'confidence': 0.0,
                'error': 'Gemini API returned empty response'
            }

    except Exception as e:
        return {
            'text': '',
            'confidence': 0.0,
            'error': f'OCR extraction failed: {str(e)}'
        }


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
                # Remove any non-numeric characters except dots
                score_str = ''.join(c for c in score_str if c.isdigit() or c == '.')
                score = float(score_str)
                confidence = min(score / 100.0, 1.0)  # Normalize to 0-1
            except (ValueError, IndexError):
                confidence = 0.85  # Fallback
        else:
            text_lines.append(line)

    return '\n'.join(text_lines), confidence
