"""
NIVARAN — NER Model Module
Loads custom SpaCy NER models for entity extraction from civic notices
and rental agreements.

Two model configurations:
1. civic_notice_ner: DATE, AMOUNT, ORG, ACTION_VERB, DEADLINE
2. rent_agreement_ner: RENT_AMOUNT, DEPOSIT_AMOUNT, LOCK_IN_PERIOD,
   NOTICE_PERIOD, PENALTY_CLAUSE, NO_REFUND_CLAUSE, TERMINATION_CLAUSE

Falls back to regex-based extraction when trained models are not available.
"""

import re
import os
import spacy

# ───────────────────────────────────────────────────────
# Model paths
# ───────────────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'nivaran_ner')

# Global model cache
_civic_model = None
_rent_model = None


def _load_base_model():
    """Load the base SpaCy English model."""
    try:
        return spacy.load('en_core_web_sm')
    except Exception as e:
        print(f"[NIVARAN][WARNING] Failed to load en_core_web_sm (Error: {e}). Using blank English model.")
        return spacy.blank('en')


def _is_valid_spacy_model(path):
    """Check if a directory contains a valid SpaCy model (has meta.json)."""
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, 'meta.json'))


def get_civic_model():
    """Load or return cached civic notice NER model."""
    global _civic_model
    if _civic_model is None:
        civic_path = os.path.join(MODEL_DIR, 'civic_notice_ner')
        if _is_valid_spacy_model(civic_path):
            try:
                _civic_model = spacy.load(civic_path)
                print("[NIVARAN] Loaded trained civic_notice_ner model.")
            except Exception as e:
                print(f"[NIVARAN][WARNING] Failed to load civic_notice_ner model: {e}")
                _civic_model = _load_base_model()
                print("[NIVARAN] Falling back to base model with regex for civic NER.")
        else:
            _civic_model = _load_base_model()
            print("[NIVARAN] No trained civic_notice_ner model found — using base model with regex fallback.")
    return _civic_model


def get_rent_model():
    """Load or return cached rent agreement NER model."""
    global _rent_model
    if _rent_model is None:
        rent_path = os.path.join(MODEL_DIR, 'rent_agreement_ner')
        if _is_valid_spacy_model(rent_path):
            try:
                _rent_model = spacy.load(rent_path)
                print("[NIVARAN] Loaded trained rent_agreement_ner model.")
            except Exception as e:
                print(f"[NIVARAN][WARNING] Failed to load rent_agreement_ner model: {e}")
                _rent_model = _load_base_model()
                print("[NIVARAN] Falling back to base model with regex for rent NER.")
        else:
            _rent_model = _load_base_model()
            print("[NIVARAN] No trained rent_agreement_ner model found — using base model with regex fallback.")
    return _rent_model


# ═══════════════════════════════════════════════════════
# CIVIC NOTICE ENTITY EXTRACTION
# ═══════════════════════════════════════════════════════

def extract_civic_entities(text):
    """
    Extract entities from a civic/government notice.

    Returns:
        dict: {
            'dates': list[str],
            'amounts': list[str],
            'organizations': list[str],
            'actions': list[str],
            'deadlines': list[str],
            'raw_entities': list[dict]  # SpaCy entities if model is trained
        }
    """
    nlp = get_civic_model()
    doc = nlp(text)

    entities = {
        'dates': [],
        'amounts': [],
        'organizations': [],
        'actions': [],
        'deadlines': [],
        'raw_entities': []
    }

    # Extract entities from SpaCy NER
    for ent in doc.ents:
        entity_info = {'text': ent.text, 'label': ent.label_, 'start': ent.start_char, 'end': ent.end_char}
        entities['raw_entities'].append(entity_info)

        if ent.label_ in ('DATE', 'DEADLINE'):
            entities['dates'].append(ent.text)
            if ent.label_ == 'DEADLINE':
                entities['deadlines'].append(ent.text)
        elif ent.label_ in ('MONEY', 'AMOUNT'):
            entities['amounts'].append(ent.text)
        elif ent.label_ in ('ORG', 'ORGANIZATION'):
            entities['organizations'].append(ent.text)
        elif ent.label_ in ('ACTION_VERB',):
            entities['actions'].append(ent.text)

    # ─── Regex Fallback ───────────────────────────────
    # Always run regex to catch what SpaCy might miss
    entities = _civic_regex_fallback(text, entities)

    return entities


def _civic_regex_fallback(text, entities):
    """Regex-based entity extraction as fallback/supplement for civic notices."""

    # Amounts: ₹, Rs., INR patterns
    amount_patterns = [
        r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{2})?)',
        r'([\d,]+(?:\.\d{2})?)\s*(?:₹|Rs\.?|INR|rupees?)',
        r'(?:amount|total|due|pay|payment|charge|fee|fine)\s*(?:of|is|:)?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d{2})?)',
    ]
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.replace(',', '').strip()
            if cleaned and cleaned not in entities['amounts']:
                entities['amounts'].append(cleaned)

    # Dates: various formats
    date_patterns = [
        r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
        r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})\b',
        r'\b(?:due\s+(?:date|by|on|before)\s*:?\s*)(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
        r'\b(?:before|by|on|dated?)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if m not in entities['dates']:
                entities['dates'].append(m)

    # Action words
    action_patterns = [
        r'\b(pay|deposit|submit|file|report|renew|register|comply|respond|appear|contact)\b',
    ]
    for pattern in action_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            m_lower = m.lower()
            if m_lower not in [a.lower() for a in entities['actions']]:
                entities['actions'].append(m_lower)

    # Organizations
    org_patterns = [
        r'(?:(?:Municipal|District|State|Central|National)\s+\w+(?:\s+\w+)?)',
        r'(?:(?:BSES|NDMC|MCD|DDA|LIC|SBI|HDFC|ICICI|PNB|BOB|RBI)\b)',
        r'(?:(?:Electricity|Water|Gas|Revenue|Income\s+Tax)\s+(?:Board|Department|Authority|Commission|Corporation|Office))',
    ]
    for pattern in org_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if m not in entities['organizations']:
                entities['organizations'].append(m)

    return entities


# ═══════════════════════════════════════════════════════
# RENTAL AGREEMENT ENTITY EXTRACTION
# ═══════════════════════════════════════════════════════

def extract_rent_entities(text):
    """
    Extract entities from a rental agreement document.

    Returns:
        dict: {
            'rent_amount': float or None,
            'deposit_amount': float or None,
            'lock_in_period': int or None (months),
            'notice_period': int or None (days),
            'penalty_clause_present': bool,
            'penalty_text': str,
            'no_refund_clause': bool,
            'no_refund_text': str,
            'termination_clause_present': bool,
            'termination_text': str,
            'rent_escalation_uncapped': bool,
            'unrestricted_entry': bool,
            'raw_entities': list[dict]
        }
    """
    nlp = get_rent_model()
    doc = nlp(text)

    entities = {
        'rent_amount': None,
        'deposit_amount': None,
        'lock_in_period': None,
        'notice_period': None,
        'penalty_clause_present': False,
        'penalty_text': '',
        'no_refund_clause': False,
        'no_refund_text': '',
        'termination_clause_present': False,
        'termination_text': '',
        'rent_escalation_uncapped': False,
        'unrestricted_entry': False,
        'raw_entities': []
    }

    # Extract from SpaCy NER (if trained model is loaded)
    for ent in doc.ents:
        entity_info = {'text': ent.text, 'label': ent.label_, 'start': ent.start_char, 'end': ent.end_char}
        entities['raw_entities'].append(entity_info)

        if ent.label_ == 'RENT_AMOUNT':
            entities['rent_amount'] = _parse_amount(ent.text)
        elif ent.label_ == 'DEPOSIT_AMOUNT':
            entities['deposit_amount'] = _parse_amount(ent.text)
        elif ent.label_ == 'LOCK_IN_PERIOD':
            entities['lock_in_period'] = _parse_months(ent.text)
        elif ent.label_ == 'NOTICE_PERIOD':
            entities['notice_period'] = _parse_days(ent.text)
        elif ent.label_ == 'PENALTY_CLAUSE':
            entities['penalty_clause_present'] = True
            entities['penalty_text'] = ent.text
        elif ent.label_ == 'NO_REFUND_CLAUSE':
            entities['no_refund_clause'] = True
            entities['no_refund_text'] = ent.text
        elif ent.label_ == 'TERMINATION_CLAUSE':
            entities['termination_clause_present'] = True
            entities['termination_text'] = ent.text

    # ─── Regex Fallback ───────────────────────────────
    entities = _rent_regex_fallback(text, entities)

    return entities


def _rent_regex_fallback(text, entities):
    """Regex-based extraction fallback for rental agreements."""
    text_lower = text.lower()

    # ─── Rent Amount ──────────────────────────────────
    if entities['rent_amount'] is None:
        rent_patterns = [
            r'(?:monthly\s+)?rent\s*(?:of|is|:|-|shall be|amount)?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+)',
            r'(?:₹|Rs\.?|INR)\s*([\d,]+)\s*(?:per\s+month|monthly|p\.?m\.?|/\s*month)',
        ]
        for pattern in rent_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['rent_amount'] = _parse_amount(match.group(1))
                break

    # ─── Deposit / Security Deposit ───────────────────
    if entities['deposit_amount'] is None:
        deposit_patterns = [
            r'(?:security\s+)?deposit\s*(?:of|is|:|-|shall be|amount)?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+)',
            r'(?:₹|Rs\.?|INR)\s*([\d,]+)\s*(?:as\s+(?:security\s+)?deposit)',
            r'(?:advance|caution)\s*(?:money|deposit)?\s*(?:of|is|:)?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+)',
        ]
        for pattern in deposit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['deposit_amount'] = _parse_amount(match.group(1))
                break

    # ─── Lock-in Period ───────────────────────────────
    if entities['lock_in_period'] is None:
        lockin_patterns = [
            r'lock[\s-]*in\s*(?:period)?\s*(?:of|is|:|-|shall be)?\s*(\d+)\s*(?:months?|yrs?|years?)',
            r'(?:minimum\s+)?(?:tenure|period|term)\s*(?:of|is|:)?\s*(\d+)\s*(?:months?|yrs?|years?)',
        ]
        for pattern in lockin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                # Convert years to months if necessary
                if 'year' in match.group(0).lower() or 'yr' in match.group(0).lower():
                    value *= 12
                entities['lock_in_period'] = value
                break

    # ─── Notice Period ────────────────────────────────
    if entities['notice_period'] is None:
        notice_patterns = [
            r'notice\s*(?:period)?\s*(?:of|is|:|-|shall be)?\s*(\d+)\s*(?:days?|months?)',
            r'(\d+)\s*(?:days?|months?)\s*(?:prior\s+)?(?:written\s+)?notice',
        ]
        for pattern in notice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                # Convert months to days
                if 'month' in match.group(0).lower():
                    value *= 30
                entities['notice_period'] = value
                break

    # ─── Penalty Clause ───────────────────────────────
    if not entities['penalty_clause_present']:
        penalty_patterns = [
            r'((?:penalty|forfeiture|forfeit|penal|liquidated damages)[\s\S]{0,200}(?:early|premature|before)[\s\S]{0,100}(?:termination|vacate|leaving|exit))',
            r'((?:early|premature|before)[\s\S]{0,100}(?:termination|vacate|leaving|exit)[\s\S]{0,200}(?:penalty|forfeiture|forfeit|penal|liquidated damages))',
        ]
        for pattern in penalty_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['penalty_clause_present'] = True
                entities['penalty_text'] = match.group(1)[:300]
                break

    # ─── No-Refund Clause (CRITICAL — zero false negatives) ───
    if not entities['no_refund_clause']:
        no_refund_patterns = [
            r'((?:deposit|amount)\s+(?:is|shall be|will be)\s+(?:non[\s-]?refundable|not\s+refundable|not\s+(?:be\s+)?refunded|forfeited))',
            r'(non[\s-]?refundable\s+(?:deposit|security|advance|amount))',
            r'((?:no|not|never)\s+(?:refund|return)\s+(?:of|on)?\s*(?:deposit|security|advance|amount))',
            r'((?:deposit|security|advance)\s+(?:shall|will|would)\s+(?:not|never)\s+(?:be\s+)?(?:refunded|returned))',
            r'(under\s+no\s+circum\w*\s+(?:shall|will)?\s*(?:the\s+)?(?:deposit|security|amount)\s+(?:be\s+)?(?:refunded|returned))',
        ]
        for pattern in no_refund_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['no_refund_clause'] = True
                entities['no_refund_text'] = match.group(1)
                break

    # ─── Termination Clause ───────────────────────────
    if not entities['termination_clause_present']:
        termination_patterns = [
            r'((?:termination|exit|vacating|end of tenancy)[\s\S]{0,300}(?:clause|section|article|provision))',
            r'((?:clause|section|article)\s*\d*\s*[:\-]?\s*(?:termination|exit|vacating|end of tenancy))',
        ]
        for pattern in termination_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['termination_clause_present'] = True
                entities['termination_text'] = match.group(1)[:300]
                break

    # ─── Rent Escalation ──────────────────────────────
    escalation_patterns = [
        r'(?:rent|rental)\s+(?:increase|escalation|revision|hike)[\s\S]{0,200}(?:at\s+(?:the\s+)?(?:sole\s+)?discretion|without\s+(?:limit|cap|ceiling|consent|notice)|any\s+time)',
        r'(?:landlord|lessor)\s+(?:may|shall|can|reserves?\s+the\s+right)\s+(?:to\s+)?(?:increase|raise|revise|hike)\s+(?:the\s+)?rent\s+(?:at\s+any\s+time|without)',
    ]
    for pattern in escalation_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            entities['rent_escalation_uncapped'] = True
            break

    # ─── Unrestricted Entry ───────────────────────────
    entry_patterns = [
        r'(?:landlord|lessor|owner)\s+(?:shall\s+have|has|reserves?)\s+(?:unrestricted|unlimited|full|free)\s+(?:access|entry|right\s+to\s+enter)',
        r'(?:enter|access|inspect)\s+(?:the\s+)?(?:premises|property)\s+(?:at\s+any\s+time|without\s+(?:prior\s+)?notice)',
    ]
    for pattern in entry_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            entities['unrestricted_entry'] = True
            break

    return entities


# ═══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

def _parse_amount(text):
    """Parse a numeric amount from text, removing commas and currency symbols."""
    try:
        cleaned = re.sub(r'[^\d.]', '', text.replace(',', ''))
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


def _parse_months(text):
    """Parse a duration in months from text."""
    try:
        match = re.search(r'(\d+)', text)
        if match:
            value = int(match.group(1))
            if 'year' in text.lower() or 'yr' in text.lower():
                value *= 12
            return value
    except (ValueError, TypeError):
        pass
    return None


def _parse_days(text):
    """Parse a duration in days from text."""
    try:
        match = re.search(r'(\d+)', text)
        if match:
            value = int(match.group(1))
            if 'month' in text.lower():
                value *= 30
            return value
    except (ValueError, TypeError):
        pass
    return None
