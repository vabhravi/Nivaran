"""
NIVARAN — Rule Engine Module
Deterministic rule evaluation against SQLite-stored legal rules.

Evaluates extracted entities from rental agreements against the
Model Tenancy Act, 2021 rules stored in the SQLite database.

No ML, no LLMs — pure deterministic logic with explainable outputs.
"""

import os
import sqlite3

# ───────────────────────────────────────────────────────
# Database path
# ───────────────────────────────────────────────────────
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'rules.db')

# Severity weights for risk score calculation
SEVERITY_WEIGHTS = {
    'CRITICAL': 3.0,
    'HIGH': 2.0,
    'MEDIUM': 1.0,
    'LOW': 0.5,
}

# Maximum total weighted score (normalizer)
MAX_RISK_DEDUCTION = 10.0


def get_db_connection():
    """Create a fresh SQLite connection (thread-safe)."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def evaluate_rental_agreement(entities):
    """
    Evaluate extracted entities against all legal rules in the database.

    Args:
        entities (dict): Extracted entities from ner_model.extract_rent_entities()
            Expected keys:
                - rent_amount: float or None
                - deposit_amount: float or None
                - lock_in_period: int or None (months)
                - notice_period: int or None (days)
                - penalty_clause_present: bool
                - no_refund_clause: bool
                - termination_clause_present: bool
                - rent_escalation_uncapped: bool
                - unrestricted_entry: bool

    Returns:
        dict: {
            'risk_score': float (0-10, 10 = safest),
            'flagged_clauses': list[dict],
            'total_flags': int,
            'severity_breakdown': dict
        }
    """
    conn = get_db_connection()
    rules = conn.execute('SELECT * FROM legal_rules').fetchall()
    conn.close()

    flagged_clauses = []
    total_weighted_deduction = 0.0
    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

    for rule in rules:
        violation = _check_rule(rule, entities)
        if violation:
            severity = rule['severity']
            weight = SEVERITY_WEIGHTS.get(severity, 1.0)
            total_weighted_deduction += weight
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            flagged_clauses.append({
                'rule_id': rule['id'],
                'rule_name': rule['rule_name'],
                'entity_type': rule['entity_type'],
                'severity': severity,
                'violation_description': rule['violation_description'],
                'legal_citation': rule['legal_citation'],
                'recommended_action': rule['recommended_action'],
                'detected_value': violation.get('detected_value', 'N/A'),
                'clause_text': violation.get('clause_text', ''),
            })

    # Calculate risk score: 10 - normalized deduction (clamped to 0-10)
    risk_score = max(0.0, min(10.0, 10.0 - (total_weighted_deduction / MAX_RISK_DEDUCTION) * 10.0))
    risk_score = round(risk_score, 1)

    return {
        'risk_score': risk_score,
        'flagged_clauses': flagged_clauses,
        'total_flags': len(flagged_clauses),
        'severity_breakdown': severity_counts,
    }


def _check_rule(rule, entities):
    """
    Check a single rule against the extracted entities.

    Returns a violation dict if the rule is triggered, else None.
    Uses deterministic condition matching — no eval().
    """
    condition = rule['condition']
    entity_type = rule['entity_type']

    # ─── DEPOSIT_AMOUNT: deposit > 2 * rent ──────────
    if condition == 'deposit > 2 * rent':
        rent = entities.get('rent_amount')
        deposit = entities.get('deposit_amount')
        if rent and deposit and deposit > 2 * rent:
            return {
                'detected_value': f'Deposit: ₹{deposit:,.0f}, Rent: ₹{rent:,.0f} (Ratio: {deposit/rent:.1f}x)',
                'clause_text': f'Security deposit of ₹{deposit:,.0f} against monthly rent of ₹{rent:,.0f}'
            }

    # ─── NO_REFUND_CLAUSE: no_refund_clause == True ──
    elif condition == 'no_refund_clause == True':
        if entities.get('no_refund_clause'):
            return {
                'detected_value': 'Non-refundable deposit clause detected',
                'clause_text': entities.get('no_refund_text', 'Deposit declared non-refundable')
            }

    # ─── LOCK_IN_PERIOD: lock_in_period > 11 ─────────
    elif condition == 'lock_in_period > 11':
        lock_in = entities.get('lock_in_period')
        if lock_in and lock_in > 11:
            return {
                'detected_value': f'{lock_in} months',
                'clause_text': f'Lock-in period of {lock_in} months detected'
            }

    # ─── NOTICE_PERIOD: notice_period < 30 ───────────
    elif condition == 'notice_period < 30':
        notice = entities.get('notice_period')
        if notice is not None and notice < 30:
            return {
                'detected_value': f'{notice} days',
                'clause_text': f'Notice period of only {notice} days specified'
            }

    # ─── PENALTY_CLAUSE: penalty_clause_present == True
    elif condition == 'penalty_clause_present == True':
        if entities.get('penalty_clause_present'):
            return {
                'detected_value': 'Early termination penalty found',
                'clause_text': entities.get('penalty_text', 'Penalty clause for early termination')
            }

    # ─── TERMINATION_CLAUSE: termination_clause_missing
    elif condition == 'termination_clause_missing == True':
        if not entities.get('termination_clause_present'):
            return {
                'detected_value': 'No termination clause found',
                'clause_text': 'The agreement does not appear to contain a clear termination or exit clause'
            }

    # ─── RENT_AMOUNT: rent_escalation_uncapped ────────
    elif condition == 'rent_escalation_uncapped == True':
        if entities.get('rent_escalation_uncapped'):
            return {
                'detected_value': 'Uncapped rent increase clause found',
                'clause_text': 'Landlord may increase rent without limit or tenant consent'
            }

    # ─── Unrestricted entry ───────────────────────────
    elif condition == 'unrestricted_entry == True':
        if entities.get('unrestricted_entry'):
            return {
                'detected_value': 'Unrestricted landlord access clause found',
                'clause_text': 'Landlord may enter premises at any time without notice'
            }

    return None


def get_clause_templates():
    """Retrieve all clause templates from the database."""
    conn = get_db_connection()
    templates = conn.execute('SELECT * FROM clause_templates').fetchall()
    conn.close()
    return [dict(t) for t in templates]


def get_all_rules():
    """Retrieve all legal rules from the database."""
    conn = get_db_connection()
    rules = conn.execute('SELECT * FROM legal_rules').fetchall()
    conn.close()
    return [dict(r) for r in rules]
