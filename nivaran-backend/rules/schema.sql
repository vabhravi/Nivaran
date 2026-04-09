-- ═══════════════════════════════════════════════════════
-- NIVARAN — SQLite Rule Engine Schema
-- Based on Model Tenancy Act, 2021 (India)
-- ═══════════════════════════════════════════════════════

-- Drop existing tables for clean re-initialization
DROP TABLE IF EXISTS legal_rules;
DROP TABLE IF EXISTS clause_templates;

-- ───────────────────────────────────────────────────────
-- Table: legal_rules
-- Stores deterministic rules for rental agreement audit.
-- The rule_engine.py evaluates extracted entities against
-- these rules using pure Python logic (no eval()).
-- ───────────────────────────────────────────────────────
CREATE TABLE legal_rules (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name           TEXT NOT NULL,
    entity_type         TEXT NOT NULL,
    condition           TEXT NOT NULL,
    severity            TEXT NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    violation_description TEXT NOT NULL,
    legal_citation      TEXT NOT NULL,
    recommended_action  TEXT NOT NULL
);

-- ───────────────────────────────────────────────────────
-- Table: clause_templates
-- Safe vs. unsafe clause examples for user education.
-- ───────────────────────────────────────────────────────
CREATE TABLE clause_templates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    clause_type     TEXT NOT NULL,
    safe_example    TEXT NOT NULL,
    unsafe_example  TEXT NOT NULL
);

-- ═══════════════════════════════════════════════════════
-- SEED DATA: Legal Rules (Model Tenancy Act, 2021)
-- ═══════════════════════════════════════════════════════

-- Rule 1: Excessive Security Deposit
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Excessive Security Deposit',
    'DEPOSIT_AMOUNT',
    'deposit > 2 * rent',
    'HIGH',
    'Security deposit exceeds two months'' rent, which is the maximum permissible limit under the Model Tenancy Act.',
    'Section 11(2), Model Tenancy Act, 2021 — Security deposit for residential premises shall not exceed two months'' rent.',
    'Negotiate the deposit down to a maximum of two months'' rent. If the landlord refuses, this clause is legally unenforceable.'
);

-- Rule 2: No-Refund Clause on Security Deposit
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'No-Refund Clause Detected',
    'NO_REFUND_CLAUSE',
    'no_refund_clause == True',
    'CRITICAL',
    'The agreement contains a clause stating the security deposit is non-refundable. This is illegal under tenancy law.',
    'Section 11(4), Model Tenancy Act, 2021 — The landlord shall refund the security deposit after adjusting any lawful deductions, within one month of vacancy.',
    'Demand removal of this clause immediately. A non-refundable deposit clause is void and unenforceable. Document this in writing.'
);

-- Rule 3: Excessive Lock-in Period
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Excessive Lock-in Period',
    'LOCK_IN_PERIOD',
    'lock_in_period > 11',
    'HIGH',
    'The lock-in period exceeds 11 months, which may restrict tenant mobility unreasonably and may not align with standard tenancy norms.',
    'Section 21(1), Model Tenancy Act, 2021 — Tenancy agreements should specify a reasonable lock-in period. Agreements exceeding 11 months must be registered.',
    'Negotiate to reduce the lock-in period to 6 months or less. If over 11 months, ensure the agreement is properly registered.'
);

-- Rule 4: Insufficient Notice Period
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Insufficient Notice Period',
    'NOTICE_PERIOD',
    'notice_period < 30',
    'MEDIUM',
    'The notice period for termination is less than 30 days, which may not provide adequate time for the tenant to relocate.',
    'Section 21(2), Model Tenancy Act, 2021 — Either party must give at least one month notice before terminating the tenancy.',
    'Request a minimum of 30 days'' notice period be added to the agreement. This protects both parties.'
);

-- Rule 5: Unreasonable Penalty Clause
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Unreasonable Penalty Clause',
    'PENALTY_CLAUSE',
    'penalty_clause_present == True',
    'HIGH',
    'The agreement contains a penalty clause for early termination that may be disproportionate to actual damages.',
    'Section 21(4), Model Tenancy Act, 2021 — Compensation on early termination should be reasonable and proportionate.',
    'Review the penalty amount. If it exceeds one month''s rent, negotiate it down or seek legal advice before signing.'
);

-- Rule 6: Missing Termination Clause
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Missing Termination Clause',
    'TERMINATION_CLAUSE',
    'termination_clause_missing == True',
    'HIGH',
    'The agreement does not contain a clear termination or exit clause, leaving the tenant without a defined process to end the tenancy.',
    'Section 21, Model Tenancy Act, 2021 — Every tenancy agreement must specify the process and conditions for termination by either party.',
    'Insist on adding a termination clause that specifies notice period, refund process, and conditions for both parties.'
);

-- Rule 7: Rent Escalation Without Cap
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Uncapped Rent Escalation',
    'RENT_AMOUNT',
    'rent_escalation_uncapped == True',
    'MEDIUM',
    'The agreement allows the landlord to increase rent without any cap or ceiling, exposing the tenant to arbitrary hikes.',
    'Section 9(2), Model Tenancy Act, 2021 — Revision of rent shall be as per the terms agreed upon in writing between landlord and tenant.',
    'Negotiate a fixed annual escalation cap (typically 5-10%). Ensure this is written into the agreement.'
);

-- Rule 8: Landlord Unilateral Entry Rights
INSERT INTO legal_rules (rule_name, entity_type, condition, severity, violation_description, legal_citation, recommended_action)
VALUES (
    'Unrestricted Landlord Entry',
    'PENALTY_CLAUSE',
    'unrestricted_entry == True',
    'MEDIUM',
    'The agreement grants the landlord the right to enter the premises at any time without prior notice, violating tenant privacy.',
    'Section 18, Model Tenancy Act, 2021 — The landlord shall give the tenant at least 24 hours advance notice before entering the premises, except in emergencies.',
    'Insist on a clause requiring at least 24 hours'' written notice before any landlord inspection or entry.'
);

-- ═══════════════════════════════════════════════════════
-- SEED DATA: Clause Templates
-- ═══════════════════════════════════════════════════════

INSERT INTO clause_templates (clause_type, safe_example, unsafe_example)
VALUES (
    'Security Deposit',
    'The tenant shall pay a security deposit equal to two months'' rent, refundable within 30 days of vacancy after adjusting lawful deductions.',
    'The tenant shall pay a security deposit of 6 months'' rent. This deposit is non-refundable under any circumstances.'
);

INSERT INTO clause_templates (clause_type, safe_example, unsafe_example)
VALUES (
    'Lock-in Period',
    'Both parties agree to a lock-in period of 6 months, after which either party may terminate with 30 days'' written notice.',
    'The tenant agrees to a mandatory 24-month lock-in period. Early termination will result in forfeiture of the full security deposit.'
);

INSERT INTO clause_templates (clause_type, safe_example, unsafe_example)
VALUES (
    'Notice Period',
    'Either party may terminate this agreement by giving 60 days'' written notice to the other party.',
    'The tenant must vacate within 7 days of receiving a verbal notice from the landlord.'
);

INSERT INTO clause_templates (clause_type, safe_example, unsafe_example)
VALUES (
    'Rent Escalation',
    'Rent shall be increased by a maximum of 5% annually, to be mutually agreed upon 30 days before the renewal date.',
    'The landlord reserves the right to revise rent at any time without prior notice or consent of the tenant.'
);

INSERT INTO clause_templates (clause_type, safe_example, unsafe_example)
VALUES (
    'Landlord Entry',
    'The landlord may enter the premises for inspection after giving 24 hours'' written notice, except in case of emergency.',
    'The landlord shall have unrestricted access to the premises at all times without prior notice.'
);
