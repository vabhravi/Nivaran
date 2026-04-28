"""
NIVARAN — Civic-Ease Route
POST /api/civic-ease/upload

Handles government notice uploads for elderly users.
Flow: Upload → OCR (EasyOCR) → NER (SpaCy regex fallback) → Hindi Summary → Audio (pyttsx3)
All processing is offline and stateless — no documents are stored, no APIs called.
"""

import os
import threading
from flask import Blueprint, request, jsonify
from flask_socketio import emit

from nlp.ocr import extract_text_from_file
from nlp.ner_model import extract_civic_entities
from nlp.simplifier import build_hindi_summary, generate_audio, cleanup_audio_file

civic_ease_bp = Blueprint('civic_ease', __name__)

# Low confidence threshold
OCR_CONFIDENCE_THRESHOLD = 0.6


@civic_ease_bp.route('/upload', methods=['POST'])
def upload_civic_document():
    """
    Process a government notice/civic document.

    Expects: multipart/form-data with file field 'document'
    Optional query param: sid (Socket.IO session ID for progress updates)

    Returns: JSON {
        audio_url: str,
        summary_text: str,
        extracted_entities: dict,
        ocr_text: str,
        confidence: float,
        low_confidence_warning: bool
    }
    """
    # ─── Validate Upload ──────────────────────────────
    if 'document' not in request.files:
        return jsonify({'error': 'No document file provided. Please upload an image or PDF.'}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'Empty filename. Please select a valid file.'}), 400

    # Get Socket.IO session ID for progress updates
    sid = request.form.get('sid', None)

    try:
        # Read file bytes (in-memory only — no disk write)
        file_bytes = file.read()
        filename = file.filename

        # ─── Stage 1: OCR ─────────────────────────────
        _emit_progress(sid, 'ocr', 'Dastavez se text nikal rahe hain... (Extracting text from document...)', 15)

        ocr_result = extract_text_from_file(file_bytes, filename)

        if ocr_result['error']:
            _emit_progress(sid, 'error', f'OCR failed: {ocr_result["error"]}', 100)
            return jsonify({
                'error': f'OCR failed: {ocr_result["error"]}',
                'suggestion': 'Please upload a clearer image or PDF.'
            }), 422

        raw_text = ocr_result['text']
        confidence = ocr_result['confidence']

        if not raw_text.strip():
            return jsonify({
                'error': 'No text could be extracted from the document.',
                'suggestion': 'The document may be blank or the image quality is too low.'
            }), 422

        _emit_progress(sid, 'ocr_done', 'Text safaltapoorvak nikala gaya. (Text extracted successfully.)', 35)

        # ─── Stage 2: NER ─────────────────────────────
        _emit_progress(sid, 'ner', 'Mukhya jaankaari pehchaan mein hai... (Identifying key details...)', 50)

        entities = extract_civic_entities(raw_text)

        _emit_progress(sid, 'ner_done', 'Jaankaari mil gayi — taareekh, rashi, aur kaaryvahi. (Details found — dates, amounts, and actions.)', 65)

        # ─── Stage 3: Hindi Summary ───────────────────
        _emit_progress(sid, 'simplify', 'Hindi mein saral bhaasha bana rahe hain... (Creating simple Hindi summary...)', 75)

        hindi_summary = build_hindi_summary(entities)

        _emit_progress(sid, 'simplify_done', 'Hindi saransh taiyar. (Hindi summary ready.)', 85)

        # ─── Stage 4: Audio Generation ────────────────
        _emit_progress(sid, 'audio', 'Audio bana rahe hain... (Generating audio...)', 90)

        audio_result = generate_audio(hindi_summary)

        if audio_result['error']:
            # Still return text summary even if audio fails
            _emit_progress(sid, 'error', f'Audio nahi ban saka: {audio_result["error"]}', 100)
            return jsonify({
                'audio_url': None,
                'summary_text': hindi_summary,
                'extracted_entities': entities,
                'ocr_text': raw_text,
                'confidence': confidence,
                'low_confidence_warning': confidence < OCR_CONFIDENCE_THRESHOLD,
                'audio_error': audio_result['error']
            }), 200

        audio_url = f'/audio/{audio_result["audio_filename"]}'

        _emit_progress(sid, 'complete', 'Taiyar hai! Audio suniye. (Ready! Listen to the audio.)', 100)

        # ─── Schedule cleanup after 5 minutes ─────────
        _schedule_cleanup(audio_result['audio_path'], delay_seconds=300)

        return jsonify({
            'audio_url': audio_url,
            'summary_text': hindi_summary,
            'extracted_entities': {
                'dates': entities['dates'],
                'amounts': entities['amounts'],
                'organizations': entities['organizations'],
                'actions': entities['actions'],
            },
            'ocr_text': raw_text,
            'confidence': confidence,
            'low_confidence_warning': confidence < OCR_CONFIDENCE_THRESHOLD,
        }), 200

    except Exception as e:
        _emit_progress(sid, 'error', f'Processing failed: {str(e)}', 100)
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


def _emit_progress(sid, stage, message, percent):
    """Emit a progress update via Socket.IO if a session ID is provided."""
    if sid:
        try:
            from app import socketio
            socketio.emit('analysis_progress', {
                'stage': stage,
                'message': message,
                'percent': percent,
                'module': 'civic-ease'
            }, room=sid)
        except Exception:
            pass  # Don't fail if Socket.IO emit fails


def _schedule_cleanup(audio_path, delay_seconds=300):
    """Schedule audio file deletion after a delay (stateless processing)."""
    def _cleanup():
        import time
        time.sleep(delay_seconds)
        cleanup_audio_file(audio_path)

    t = threading.Thread(target=_cleanup, daemon=True)
    t.start()
