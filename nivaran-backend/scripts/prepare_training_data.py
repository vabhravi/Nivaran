"""
NIVARAN — SpaCy Training Data Annotation Script
Prepares annotated training data for custom NER models.

Two model configurations:
1. civic_notice_ner: DATE, AMOUNT, ORG, ACTION_VERB, DEADLINE
2. rent_agreement_ner: RENT_AMOUNT, DEPOSIT_AMOUNT, LOCK_IN_PERIOD,
   NOTICE_PERIOD, PENALTY_CLAUSE, NO_REFUND_CLAUSE, TERMINATION_CLAUSE

Usage:
    python scripts/prepare_training_data.py

This script:
  1. Defines sample annotated training data in SpaCy format.
  2. Converts annotations to SpaCy DocBin (.spacy) binary format.
  3. Generates SpaCy config files for training.
  4. Outputs instructions for running spacy train.

In production, you would replace the sample data below with your
50 annotated rental agreements and 20 government notices.
"""

import os
import json
import spacy
from spacy.tokens import DocBin
from spacy.training import Example

# ═══════════════════════════════════════════════════════
# OUTPUT DIRECTORIES
# ═══════════════════════════════════════════════════════
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'training_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════
# SAMPLE CIVIC NOTICE TRAINING DATA
# Format: (text, {"entities": [(start, end, label), ...]})
# ═══════════════════════════════════════════════════════

CIVIC_NOTICE_TRAIN_DATA = [
    (
        "This is to inform you that your electricity bill of Rs. 2500 is due by 15/03/2024. "
        "Please pay the amount to BSES Rajdhani Power Limited before the due date to avoid disconnection.",
        {"entities": [
            (57, 64, "AMOUNT"),
            (74, 84, "DEADLINE"),
            (112, 142, "ORG"),
            (89, 92, "ACTION_VERB"),
            (74, 84, "DATE"),
        ]}
    ),
    (
        "Municipal Corporation of Delhi. Property Tax Notice. "
        "You are hereby informed that property tax of INR 15000 for the financial year 2023-24 "
        "is pending. Last date for payment without penalty: 31st March 2024. "
        "Contact MCD Ward Office for queries.",
        {"entities": [
            (0, 31, "ORG"),
            (100, 105, "AMOUNT"),
            (155, 170, "DEADLINE"),
            (155, 170, "DATE"),
            (172, 179, "ACTION_VERB"),
            (180, 200, "ORG"),
        ]}
    ),
    (
        "HDFC Bank Notice: Your home loan EMI of Rs 18500 for the month of February 2024 "
        "is overdue. Kindly deposit the outstanding amount by 10/02/2024 to avoid late payment charges.",
        {"entities": [
            (0, 9, "ORG"),
            (40, 45, "AMOUNT"),
            (67, 80, "DATE"),
            (107, 117, "DEADLINE"),
            (96, 103, "ACTION_VERB"),
        ]}
    ),
    (
        "Water Supply Board, Government of Maharashtra. Notice for pending water bill. "
        "Amount due: Rs 450. Payment deadline: 20th January 2024. "
        "Pay online at mahawater.gov.in or visit nearest Jan Seva Kendra.",
        {"entities": [
            (0, 46, "ORG"),
            (89, 92, "AMOUNT"),
            (115, 135, "DEADLINE"),
            (115, 135, "DATE"),
            (137, 140, "ACTION_VERB"),
        ]}
    ),
    (
        "Income Tax Department, Government of India. "
        "You are required to file your Income Tax Return for AY 2023-24 by 31st July 2024. "
        "Failure to comply will attract penalty under Section 234F of the Income Tax Act.",
        {"entities": [
            (0, 43, "ORG"),
            (64, 68, "ACTION_VERB"),
            (107, 121, "DEADLINE"),
            (107, 121, "DATE"),
        ]}
    ),
    (
        "LIC of India Policy Premium Notice. Your premium of Rs. 12000 for policy number "
        "LIC-2024-5678 is due on 15/04/2024. Submit payment at nearest LIC branch or online portal.",
        {"entities": [
            (0, 12, "ORG"),
            (52, 57, "AMOUNT"),
            (99, 109, "DEADLINE"),
            (99, 109, "DATE"),
            (111, 117, "ACTION_VERB"),
        ]}
    ),
    (
        "Gas Authority of India Limited. Your cooking gas cylinder subsidy of Rs 250 has been "
        "credited to your bank account on 05/01/2024. No action required.",
        {"entities": [
            (0, 30, "ORG"),
            (71, 74, "AMOUNT"),
            (115, 125, "DATE"),
        ]}
    ),
    (
        "State Bank of India. Credit Card Statement. Your outstanding balance is Rs 8750. "
        "Minimum amount due: Rs 875. Payment due date: 25/02/2024. "
        "Please pay to avoid interest charges.",
        {"entities": [
            (0, 19, "ORG"),
            (72, 76, "AMOUNT"),
            (101, 104, "AMOUNT"),
            (127, 137, "DEADLINE"),
            (127, 137, "DATE"),
            (139, 142, "ACTION_VERB"),
        ]}
    ),
]


# ═══════════════════════════════════════════════════════
# SAMPLE RENTAL AGREEMENT TRAINING DATA
# ═══════════════════════════════════════════════════════

RENT_AGREEMENT_TRAIN_DATA = [
    (
        "The monthly rent for the premises shall be Rs 15000 (Rupees Fifteen Thousand only) "
        "payable on or before the 5th of each month. The tenant shall pay a security deposit "
        "of Rs 45000 (Rupees Forty Five Thousand only) at the time of signing this agreement.",
        {"entities": [
            (45, 50, "RENT_AMOUNT"),
            (163, 168, "DEPOSIT_AMOUNT"),
        ]}
    ),
    (
        "Lock-in Period: The tenant agrees to a minimum lock-in period of 12 months from the "
        "date of commencement. During this period, the tenant shall not vacate the premises. "
        "Early termination during lock-in will result in forfeiture of the security deposit.",
        {"entities": [
            (63, 72, "LOCK_IN_PERIOD"),
            (147, 259, "PENALTY_CLAUSE"),
        ]}
    ),
    (
        "Termination: Either party may terminate this agreement by giving 15 days written notice "
        "to the other party. Upon termination, the tenant shall vacate the premises and the "
        "landlord shall refund the security deposit within 30 days of vacancy.",
        {"entities": [
            (64, 71, "NOTICE_PERIOD"),
            (0, 241, "TERMINATION_CLAUSE"),
        ]}
    ),
    (
        "The security deposit of Rs 100000 paid by the tenant is non-refundable under any "
        "circumstances. The landlord shall retain the full deposit amount regardless of the "
        "condition of the premises at the time of vacancy.",
        {"entities": [
            (27, 33, "DEPOSIT_AMOUNT"),
            (0, 88, "NO_REFUND_CLAUSE"),
        ]}
    ),
    (
        "Monthly rent: INR 20000. Security deposit: INR 60000 (three months rent). "
        "Lock-in period: 6 months. Notice period for termination: 30 days by either party.",
        {"entities": [
            (18, 23, "RENT_AMOUNT"),
            (47, 52, "DEPOSIT_AMOUNT"),
            (80, 88, "LOCK_IN_PERIOD"),
            (114, 121, "NOTICE_PERIOD"),
        ]}
    ),
    (
        "In case of early termination by the tenant before completion of the lock-in period "
        "of 11 months, the tenant shall be liable to pay a penalty equivalent to two months' "
        "rent as liquidated damages to the landlord.",
        {"entities": [
            (84, 93, "LOCK_IN_PERIOD"),
            (0, 215, "PENALTY_CLAUSE"),
        ]}
    ),
    (
        "The tenant hereby agrees that the advance amount of Rs 50000 deposited with the "
        "landlord shall not be refunded to the tenant under any circumstances whatsoever. "
        "This amount shall be treated as non-refundable advance.",
        {"entities": [
            (49, 54, "DEPOSIT_AMOUNT"),
            (0, 200, "NO_REFUND_CLAUSE"),
        ]}
    ),
    (
        "The rent for the said premises is fixed at Rs 25000 per month. The lessee shall "
        "deposit Rs 50000 as security deposit. The agreement shall be for a period of "
        "11 months with a notice period of 60 days for termination.",
        {"entities": [
            (44, 49, "RENT_AMOUNT"),
            (87, 92, "DEPOSIT_AMOUNT"),
            (139, 148, "LOCK_IN_PERIOD"),
            (169, 176, "NOTICE_PERIOD"),
        ]}
    ),
    (
        "Clause 8 - Termination: This agreement may be terminated by either party giving "
        "not less than one month prior written notice. Upon termination by the tenant, the "
        "landlord shall refund the security deposit after deducting any damages within 15 days.",
        {"entities": [
            (0, 265, "TERMINATION_CLAUSE"),
            (88, 97, "NOTICE_PERIOD"),
        ]}
    ),
    (
        "The landlord reserves the right to increase the rent at any time without prior notice "
        "or consent of the tenant. The tenant shall comply with any rent revision immediately.",
        {"entities": [
            (40, 44, "RENT_AMOUNT"),
        ]}
    ),
]


# ═══════════════════════════════════════════════════════
# CONVERSION TO SPACY DOCBIN FORMAT
# ═══════════════════════════════════════════════════════

def create_training_data(train_data, output_name, custom_labels):
    """
    Convert annotated training data to SpaCy DocBin format.

    Args:
        train_data: List of (text, annotations) tuples.
        output_name: Name for the output .spacy file.
        custom_labels: List of custom entity labels.
    """
    nlp = spacy.blank('en')

    # Add custom entity labels
    ner = nlp.add_pipe('ner')
    for label in custom_labels:
        ner.add_label(label)

    doc_bin = DocBin()
    skipped = 0

    for text, annotations in train_data:
        try:
            doc = nlp.make_doc(text)
            ents = []
            seen_tokens = set()

            for start, end, label in annotations['entities']:
                span = doc.char_span(start, end, label=label, alignment_mode='contract')
                if span is not None:
                    # Check for overlapping spans
                    token_range = set(range(span.start, span.end))
                    if not token_range & seen_tokens:
                        ents.append(span)
                        seen_tokens |= token_range

            doc.ents = ents
            doc_bin.add(doc)
        except Exception as e:
            print(f"  Skipped entry: {e}")
            skipped += 1

    output_path = os.path.join(OUTPUT_DIR, f'{output_name}.spacy')
    doc_bin.to_disk(output_path)
    print(f"  ✅ Created {output_path} ({len(train_data) - skipped} docs, {skipped} skipped)")

    return output_path


def generate_spacy_config(model_name, labels, output_dir):
    """
    Generate a base SpaCy training config file.

    In practice, you would use: python -m spacy init config config.cfg --lang en --pipeline ner
    This function creates a minimal config for reference.
    """
    config_content = f"""# NIVARAN SpaCy Training Config — {model_name}
# Generated by prepare_training_data.py
#
# To generate a full config, run:
#   python -m spacy init config {model_name}_config.cfg --lang en --pipeline ner --optimize efficiency
#
# Then train with:
#   python -m spacy train {model_name}_config.cfg \\
#       --output ../models/nivaran_ner/{model_name} \\
#       --paths.train ./training_data/{model_name}_train.spacy \\
#       --paths.dev ./training_data/{model_name}_dev.spacy

[system]
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["tok2vec", "ner"]
batch_size = 1000
disabled = []

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 96
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = true

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"
seed = 0
gpu_allocator = null
accumulate_gradient = 1
patience = 1600
max_epochs = 100
max_steps = 20000
eval_frequency = 200
score_weights = {{"ents_f": 1.0, "ents_p": 0.0, "ents_r": 0.0}}

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = false
eps = 0.00000001

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2
get_length = null
size = 500

[corpora]

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${{paths.dev}}
max_length = 0
gold_preproc = false
limit = 0
augmenter = null

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${{paths.train}}
max_length = 0
gold_preproc = false
limit = 0
augmenter = null

[paths]
train = null
dev = null
vectors = "en_core_web_sm"
init_tok2vec = null
"""

    config_path = os.path.join(output_dir, f'{model_name}_config.cfg')
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print(f"  ✅ Config saved to {config_path}")

    return config_path


# ═══════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("NIVARAN — SpaCy Training Data Preparation")
    print("=" * 60)

    # ─── Civic Notice NER ─────────────────────────────
    print("\n📄 Preparing Civic Notice NER training data...")
    civic_labels = ['DATE', 'AMOUNT', 'ORG', 'ACTION_VERB', 'DEADLINE']
    civic_path = create_training_data(
        CIVIC_NOTICE_TRAIN_DATA,
        'civic_notice_ner_train',
        civic_labels
    )
    generate_spacy_config('civic_notice_ner', civic_labels, OUTPUT_DIR)

    # ─── Rent Agreement NER ───────────────────────────
    print("\n🏠 Preparing Rent Agreement NER training data...")
    rent_labels = [
        'RENT_AMOUNT', 'DEPOSIT_AMOUNT', 'LOCK_IN_PERIOD',
        'NOTICE_PERIOD', 'PENALTY_CLAUSE', 'NO_REFUND_CLAUSE',
        'TERMINATION_CLAUSE'
    ]
    rent_path = create_training_data(
        RENT_AGREEMENT_TRAIN_DATA,
        'rent_agreement_ner_train',
        rent_labels
    )
    generate_spacy_config('rent_agreement_ner', rent_labels, OUTPUT_DIR)

    # ─── Instructions ─────────────────────────────────
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Install SpaCy and the base model:
   pip install spacy
   python -m spacy download en_core_web_sm

2. Add more training data to the TRAIN_DATA lists above.
   Target: 50 rental agreements + 20 government notices.

3. Split data into train/dev sets (80/20 split).

4. Generate a full SpaCy config:
   python -m spacy init config config.cfg --lang en --pipeline ner --optimize efficiency

5. Train the civic notice model:
   python -m spacy train training_data/civic_notice_ner_config.cfg \\
       --output models/nivaran_ner/civic_notice_ner \\
       --paths.train training_data/civic_notice_ner_train.spacy \\
       --paths.dev training_data/civic_notice_ner_train.spacy

6. Train the rent agreement model:
   python -m spacy train training_data/rent_agreement_ner_config.cfg \\
       --output models/nivaran_ner/rent_agreement_ner \\
       --paths.train training_data/rent_agreement_ner_train.spacy \\
       --paths.dev training_data/rent_agreement_ner_train.spacy

7. The trained models will be saved in models/nivaran_ner/ and
   automatically loaded by ner_model.py when the app starts.

NOTE: Until models are trained, the app uses regex-based fallback
extraction which is functional but less accurate than trained NER.
""")
