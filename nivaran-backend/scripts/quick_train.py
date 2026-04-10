"""
NIVARAN — HYPER-FAST DEMO TRAINING SCRIPT
=========================================
Trains a tiny SpaCy NER model in < 10 seconds.
Includes high-frequency printing to prevent terminal freeze.
"""

import os
import spacy
import time
from spacy.training import Example

# ───────────────────────────────────────────────────────
# 1. SETUP PATHS
# ───────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE_DIR, 'models', 'quick_demo_model')

print(f"[1/7] Initializing path: {OUTPUT_DIR}")
os.makedirs(os.path.dirname(OUTPUT_DIR), exist_ok=True)

# ───────────────────────────────────────────────────────
# 2. TRAINING DATA (Exactly 3 examples)
# ───────────────────────────────────────────────────────
print("[2/7] Preparing training data...")

TRAIN_DATA = [
    (
        "BSES Rajdhani Power Limited. Bill Amount: Rs. 2500. Due Date: 15/04/2024.",
        {"entities": [
            (0, 27, "ORG"),        # BSES Rajdhani Power Limited
            (42, 50, "AMOUNT"),     # Rs. 2500
            (62, 72, "DATE")        # 15/04/2024
        ]}
    ),
    (
        "Municipal Corporation of Delhi. Tax Due: Rs. 12000. Deadline: 31/03/2024.",
        {"entities": [
            (0, 30, "ORG"),        # Municipal Corporation of Delhi
            (41, 50, "AMOUNT"),     # Rs. 12000
            (61, 71, "DATE")        # 31/03/2024
        ]}
    ),
    (
        "Rent Agreement. Monthly Rent: Rs. 18000. Security Deposit: Rs. 54000. Notice: 30 days.",
        {"entities": [
            (31, 40, "RENT_AMOUNT"), # Rs. 18000
            (59, 68, "DEPOSIT"),     # Rs. 54000
            (77, 84, "NOTICE")       # 30 days
        ]}
    )
]

# ───────────────────────────────────────────────────────
# 3. INITIALIZE BLANK MODEL
# ───────────────────────────────────────────────────────
print("[3/7] Creating blank English model...")
nlp = spacy.blank("en")

if "ner" not in nlp.pipe_names:
    print("      Adding 'ner' pipeline component...")
    ner = nlp.add_pipe("ner")

# ───────────────────────────────────────────────────────
# 4. ADD LABELS
# ───────────────────────────────────────────────────────
print("[4/7] Registering entity labels...")
for text, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# ───────────────────────────────────────────────────────
# 5. START TRAINING
# ───────────────────────────────────────────────────────
print("[5/7] Starting training loop (10 iterations)...")
optimizer = nlp.begin_training()

for i in range(1, 11):
    start_time = time.time()
    losses = {}
    
    # Process each example individually for maximum visibility
    for j, (text, annotations) in enumerate(TRAIN_DATA):
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], sgd=optimizer, drop=0.2, losses=losses)
        print(f"      Iteration {i}/10 - Sample {j+1}/3 processed...")

    elapsed = time.time() - start_time
    print(f"   >>> COMPLETED ITERATION {i:2d} | Loss: {losses.get('ner', 0.0):.4f} | Time: {elapsed:.2f}s")

# ───────────────────────────────────────────────────────
# 6. SAVE MODEL
# ───────────────────────────────────────────────────────
print(f"[6/7] Saving model to: {OUTPUT_DIR}")
nlp.to_disk(OUTPUT_DIR)

# ───────────────────────────────────────────────────────
# 7. VERIFY
# ───────────────────────────────────────────────────────
print("[7/7] Verification Test:")
test_nlp = spacy.load(OUTPUT_DIR)
doc = test_nlp("BSES Rajdhani Power Limited. Rs. 2500")
print(f"      Test Input: 'BSES Rajdhani Power Limited. Rs. 2500'")
print(f"      Detected Entities: {[(ent.text, ent.label_) for ent in doc.ents]}")

print("\n" + "="*40)
print(" ✅ TRAINING COMPLETE IN RECORD TIME!")
print("="*40)
