# Nivaran
AI-Powered Civic & Legal Companion for Digital Inclusion

Nivaran is an intelligent document analysis platform designed to help citizens understand complex civic and legal documents such as rental agreements, electricity bills, and government notices.

The system uses a custom Natural Language Processing pipeline built with **SpaCy** and a **rule-based legal reasoning engine** to extract key contractual information and identify potential risks in documents.

The goal of Nivaran is to reduce the legal literacy gap by transforming dense legal language into clear, actionable insights.

---

# Core Features

### Rent-Right (Rental Agreement Analysis)

This module analyzes rental agreements and detects problematic clauses.

It automatically extracts:

- Rent Amount
- Security Deposit
- Lock-in Period
- Penalty Clauses
- Payment Deadlines
- Termination Clauses

The system evaluates extracted entities using a legal rule engine and produces a **risk score** for the agreement.

---

### Civic-Ease (Civic Document Simplification)

This module processes government notices and civic documents and converts them into simplified explanations.

Example output:

Original Document Text  
"Failure to remit the outstanding electricity dues within seven days will result in disconnection."

Simplified Output  
"You need to pay your electricity bill within 7 days to avoid disconnection."

The system can optionally generate **audio explanations** for improved accessibility.

---

# System Architecture

```

User Uploads Document
|
v
Document Processing Layer
(PDF / Image Parsing)
|
v
Text Normalization
|
v
Custom NLP Pipeline (SpaCy)
|
v
Entity Extraction
|
v
Legal Rule Engine
|
v
Risk Detection
|
v
Simplification Engine
|
v
Output Layer

* Risk Score
* Clause Flags
* Simplified Explanation
* Optional Audio

```

---

# NLP Model

Nivaran uses a **custom-trained SpaCy Named Entity Recognition (NER) model** specifically designed for legal contract understanding.

The model is trained to detect structured legal entities within unstructured contract text.

### Extracted Entities

```

RENT_AMOUNT
DEPOSIT_AMOUNT
LOCKIN_PERIOD
PENALTY_CLAUSE
DUE_DATE
TERMINATION_CONDITION
PAYMENT_FREQUENCY

```

The model processes long legal documents and extracts critical information needed for downstream analysis.

---

# Hybrid Intelligence Approach

Nivaran does not rely on large language model APIs.

Instead, it combines:

1. **Statistical NLP (SpaCy NER)**
2. **Deterministic rule-based legal logic**
3. **Structured document interpretation**

This hybrid architecture improves reliability and transparency when working with legal documents.

---

# Rule Engine

After entity extraction, the system evaluates contracts using predefined legal heuristics.

Example rules:

```

IF deposit > 2 × monthly_rent
FLAG excessive_security_deposit

IF lockin_period > 12 months
FLAG restrictive_lockin_clause

IF penalty_clause contains "non-refundable"
FLAG financial_risk

```

The rule engine assigns a **risk score** and generates explanations for flagged clauses.

---

# Technology Stack

Backend

- Python
- Flask
- Flask-SocketIO
- SpaCy NLP

Frontend

- React.js
- WebSocket client

Database

- SQLite (rule storage)

Document Processing

- PDF parsing
- OCR for scanned documents

Audio Generation

- Text-to-Speech engine

---

# Project Structure

```

nivaran/

backend/
app.py
routes/
services/
nlp/
spacy_pipeline.py
entity_extractor.py
train_model.py

```
rule_engine/
    rules.db
    rule_engine.py
```

frontend/
src/
components/
pages/

models/
legal_ner_model/

dataset/
contracts/
civic_documents/

```

---

# Processing Pipeline

Step 1  
User uploads a document.

Step 2  
The document is converted into raw text.

Step 3  
The SpaCy NLP model extracts legal entities.

Step 4  
The rule engine evaluates extracted entities.

Step 5  
The system generates a risk score and highlights problematic clauses.

Step 6  
The simplification engine converts complex legal language into simple explanations.

Step 7  
Optional audio explanation is generated for accessibility.

---

# Evaluation Metrics

Model performance is evaluated using:

Entity Extraction Accuracy  
Target: >90%

Rule Engine Reliability  
Zero false negatives for critical risk clauses.

Latency  
Document analysis completed within 5 seconds.

---

# Privacy Design

Nivaran follows strict privacy principles.

- Documents are processed only during analysis
- No documents are stored permanently
- Extracted data is discarded after processing
- No external AI APIs are used

---

# Future Improvements

- Multilingual legal analysis
- Mobile application
- Clause classification models
- Support for additional legal document types
- Advanced risk scoring

---

# Contributors

Nivaran Development Team