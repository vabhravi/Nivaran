"""
NIVARAN — DEMO MODE ROUTE
=========================
POST /api/demo/scan

Local analysis for presentations using the quick_demo_model.
- No Gemini API calls (zero rate limits, works offline)
- Uses PyPDF2 for PDF text extraction or fallback demo text
- Uses trained SpaCy demo model (models/quick_demo_model/)
- Falls back to regex if model fails to catch specific details
- Generates Hindi audio summary via gTTS (local)
"""

import os
import io
import re
import uuid
import threading
import spacy
from flask import Blueprint, request, jsonify
from gtts import gTTS

demo_bp = Blueprint('demo', __name__)

# ───────────────────────────────────────────────────────
# Model & Path setup
# ───────────────────────────────────────────────────────
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATH = os.path.join(_BACKEND_DIR, 'models', 'quick_demo_model')
AUDIO_DIR = os.path.join(_BACKEND_DIR, 'temp_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Lazy-loaded model cache
_nlp_model = None


def _load_model():
    """Load the trained SpaCy demo model."""
    global _nlp_model
    if _nlp_model is None:
        if os.path.exists(MODEL_PATH):
            _nlp_model = spacy.load(MODEL_PATH)
            print(f"[DEMO] Loaded quick_demo_model from {MODEL_PATH}")
        else:
            print(f"[DEMO] Model NOT FOUND at {MODEL_PATH}. Falling back to blank model.")
            _nlp_model = spacy.blank("en")
    return _nlp_model


# ───────────────────────────────────────────────────────
# Text Extraction (Local)
# ───────────────────────────────────────────────────────

def _extract_text_local(file, filename):
    """Extract text from file. Uses PyPDF2 or hardcoded fallback for demo."""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    
    if ext == 'pdf':
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if text.strip():
                return text.strip()
        except Exception as e:
            print(f"[DEMO] PDF extraction failed: {e}")
            
    # Fallback to realistic demo text if extraction fails or for images
    if any(x in filename.lower() for x in ['rent', 'agreement', 'lease']):
        return "Rent Agreement. Monthly Rent: Rs. 18000. Security Deposit: Rs. 54000. Notice: 30 days."
    return "BSES Rajdhani Power Limited. Bill Amount: Rs. 2500. Due Date: 15/04/2024."


# ───────────────────────────────────────────────────────
# NER Processing
# ───────────────────────────────────────────────────────

def _process_ner(text, mode='civic'):
    """Use the SpaCy model + regex to extract entities."""
    nlp = _load_model()
    doc = nlp(text)
    
    entities = {
        'organizations': [], 'amounts': [], 'dates': [], 'actions': [],
        'rent_amount': None, 'deposit_amount': None, 'notice_period': None
    }

    # Model extraction
    for ent in doc.ents:
        lbl = ent.label_
        val = ent.text
        if lbl == 'ORG': entities['organizations'].append(val)
        elif lbl == 'AMOUNT': entities['amounts'].append(val)
        elif lbl == 'DATE': entities['dates'].append(val)
        elif lbl == 'RENT_AMOUNT': 
            digits = re.sub(r'[^\d]', '', val)
            entities['rent_amount'] = float(digits) if digits else None
        elif lbl == 'DEPOSIT':
            digits = re.sub(r'[^\d]', '', val)
            entities['deposit_amount'] = float(digits) if digits else None
        elif lbl == 'NOTICE':
            digits = re.sub(r'[^\d]', '', val)
            entities['notice_period'] = int(digits) if digits else None

    # Regex safety net for amounts/dates
    if not entities['amounts']:
        amt_match = re.search(r'Rs\.?\s*(\d+)', text)
        if amt_match: entities['amounts'].append(f"Rs. {amt_match.group(1)}")
        
    if not entities['dates']:
        date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', text)
        if date_match: entities['dates'].append(date_match.group(0))

    if mode == 'civic' and not entities['actions']:
        entities['actions'] = ['pay', 'contact']

    return entities


# ───────────────────────────────────────────────────────
# Route Handler
# ───────────────────────────────────────────────────────

@demo_bp.route('/scan', methods=['POST'])
def demo_scan():
    """Performs local analysis using the trained model."""
    if 'document' not in request.files:
        return jsonify({'error': 'No document uploaded.'}), 400

    file = request.files['document']
    mode = request.form.get('mode', 'civic').lower()
    
    text = _extract_text_local(file, file.filename)
    entities = _process_ner(text, mode=mode)
    
    # ── Summary & Audio ──
    if mode == 'rent':
        summary = f"Rent Agreement check: Rent is Rs. {entities['rent_amount'] or 18000}, Deposit is Rs. {entities['deposit_amount'] or 54000}. Notice period is {entities['notice_period'] or 30} days."
    else:
        org = entities['organizations'][0] if entities['organizations'] else "Nivaran"
        amt = entities['amounts'][0] if entities['amounts'] else "Rs. 0"
        date = entities['dates'][0] if entities['dates'] else "today"
        summary = f"Namaste. {org} ki taraf se notice hai. Aapko {amt} bharne hain. Antim tareekh {date} hai. Dhanyavaad."

    try:
        audio_filename = f"demo_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        tts = gTTS(text=summary, lang='hi' if mode == 'civic' else 'en', slow=False)
        tts.save(audio_path)
        
        def cleanup():
            if os.path.exists(audio_path): os.remove(audio_path)
        threading.Timer(1800, cleanup).start()
        
        audio_url = f"/audio/{audio_filename}"
    except Exception as e:
        print(f"[DEMO] Audio error: {e}")
        audio_url = None

    # Return standard response structure
    if mode == 'rent':
        return jsonify({
            'mode': 'rent',
            'risk_score': 9,
            'risk_level': 'GREEN',
            'flagged_clauses': [],
            'total_flags': 0,
            'severity_breakdown': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'extracted_entities': entities,
            'ocr_text': text,
            'confidence': 0.95,
            'demo_mode': True
        }), 200
    else:
        return jsonify({
            'mode': 'civic',
            'summary_text': summary,
            'audio_url': audio_url,
            'extracted_entities': entities,
            'ocr_text': text,
            'confidence': 0.95,
            'demo_mode': True
        }), 200
