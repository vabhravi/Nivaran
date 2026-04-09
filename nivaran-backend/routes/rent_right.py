"""
NIVARAN — Rent-Right Route
POST /api/rent-right/upload

Handles rental agreement uploads for students/tenants.
Flow: Upload → OCR (Gemini) → NER (SpaCy) → Rule Engine (SQLite) → Risk Score
All processing is stateless — no documents are stored.
"""

from flask import Blueprint, request, jsonify
from nlp.ocr import extract_text_from_file
from nlp.ner_model import extract_rent_entities
from rules.rule_engine import evaluate_rental_agreement

rent_right_bp = Blueprint('rent_right', __name__)

# Low confidence threshold
OCR_CONFIDENCE_THRESHOLD = 0.6


@rent_right_bp.route('/upload', methods=['POST'])
def upload_rental_agreement():
    """
    Process a rental agreement document.

    Expects: multipart/form-data with file field 'document'
    Optional query param: sid (Socket.IO session ID for progress updates)

    Returns: JSON {
        risk_score: float (0-10),
        risk_level: str (RED / AMBER / GREEN),
        flagged_clauses: list[dict],
        total_flags: int,
        severity_breakdown: dict,
        extracted_entities: dict,
        ocr_text: str,
        confidence: float,
        low_confidence_warning: bool
    }
    """
    # ─── Validate Upload ──────────────────────────────
    if 'document' not in request.files:
        return jsonify({'error': 'No document file provided. Please upload a rental agreement image or PDF.'}), 400

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
        _emit_progress(sid, 'ocr', 'Scanning your rental agreement...', 10)

        ocr_result = extract_text_from_file(file_bytes, filename)

        if ocr_result['error']:
            return jsonify({
                'error': f'OCR failed: {ocr_result["error"]}',
                'suggestion': 'Please upload a clearer image or PDF of your rental agreement.'
            }), 422

        raw_text = ocr_result['text']
        confidence = ocr_result['confidence']

        if not raw_text.strip():
            return jsonify({
                'error': 'No text could be extracted from the document.',
                'suggestion': 'The document may be blank or the image quality is too low.'
            }), 422

        _emit_progress(sid, 'ocr_done', 'Document text extracted successfully.', 25)

        # ─── Stage 2: NER ─────────────────────────────
        _emit_progress(sid, 'ner', 'Identifying rental clauses and key terms...', 35)

        entities = extract_rent_entities(raw_text)

        # Build a readable summary of what was found
        found_items = []
        if entities['rent_amount']:
            found_items.append(f"Rent: ₹{entities['rent_amount']:,.0f}")
        if entities['deposit_amount']:
            found_items.append(f"Deposit: ₹{entities['deposit_amount']:,.0f}")
        if entities['lock_in_period']:
            found_items.append(f"Lock-in: {entities['lock_in_period']} months")
        if entities['notice_period']:
            found_items.append(f"Notice: {entities['notice_period']} days")

        entities_msg = f"Found: {', '.join(found_items)}" if found_items else "Extracting clause details..."
        _emit_progress(sid, 'ner_done', entities_msg, 50)

        # ─── Stage 3: Rule Engine ─────────────────────
        _emit_progress(sid, 'rules', 'Checking against Model Tenancy Act, 2021...', 60)

        # Simulate per-clause scanning progress
        rule_result = evaluate_rental_agreement(entities)

        # Emit per-clause findings
        for i, clause in enumerate(rule_result['flagged_clauses']):
            pct = 60 + int((i + 1) / max(len(rule_result['flagged_clauses']), 1) * 25)
            severity_emoji = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }.get(clause['severity'], '⚪')
            _emit_progress(
                sid, 'rule_check',
                f"{severity_emoji} {clause['severity']}: {clause['rule_name']} — {clause['violation_description'][:80]}",
                min(pct, 85)
            )

        if not rule_result['flagged_clauses']:
            _emit_progress(sid, 'rule_check', '✅ No major violations found in the agreement.', 85)

        # ─── Stage 4: Risk Score Calculation ──────────
        risk_score = rule_result['risk_score']
        risk_level = _get_risk_level(risk_score)

        _emit_progress(
            sid, 'complete',
            f'Analysis complete. Risk Score: {risk_score}/10 ({risk_level})',
            100
        )

        # ─── Remove raw_entities from response (internal data) ──
        entities_clean = {k: v for k, v in entities.items() if k != 'raw_entities'}

        return jsonify({
            'risk_score': risk_score,
            'risk_level': risk_level,
            'flagged_clauses': rule_result['flagged_clauses'],
            'total_flags': rule_result['total_flags'],
            'severity_breakdown': rule_result['severity_breakdown'],
            'extracted_entities': entities_clean,
            'ocr_text': raw_text,
            'confidence': confidence,
            'low_confidence_warning': confidence < OCR_CONFIDENCE_THRESHOLD,
        }), 200

    except Exception as e:
        _emit_progress(sid, 'error', f'Analysis failed: {str(e)}', 100)
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


def _get_risk_level(score):
    """Map risk score to RED/AMBER/GREEN level."""
    if score <= 4:
        return 'RED'
    elif score <= 7:
        return 'AMBER'
    else:
        return 'GREEN'


def _emit_progress(sid, stage, message, percent):
    """Emit a progress update via Socket.IO if a session ID is provided."""
    if sid:
        try:
            from app import socketio
            socketio.emit('analysis_progress', {
                'stage': stage,
                'message': message,
                'percent': percent,
                'module': 'rent-right'
            }, room=sid)
        except Exception:
            pass  # Don't fail if Socket.IO emit fails
