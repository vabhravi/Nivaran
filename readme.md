# NIVARAN
### AI-Powered Civic & Legal Companion for Digital Inclusion

Nivaran is a document intelligence platform that helps citizens understand civic and legal documents such as rental agreements, electricity bills, or government notices.

Instead of using large AI APIs, Nivaran uses a **custom-trained SpaCy NLP model combined with deterministic rule-based logic** to extract meaningful entities and detect legal risks.

The platform has two main modules:

1. **Civic-Ease**
   - Simplifies civic documents
   - Converts them into short explanations
   - Produces audio explanations for elderly users

2. **Rent-Right**
   - Analyzes rental agreements
   - Extracts legal clauses
   - Flags unfair or illegal terms

---

# Core Philosophy

Nivaran follows a **Hybrid AI Architecture**

Instead of relying on LLM APIs:

- Custom NLP model (SpaCy NER)
- Deterministic legal rule engine
- Structured entity extraction
- Explainable risk scoring

This makes the system:

- Transparent
- Privacy-friendly
- Lightweight
- Explainable

---

# System Architecture

```

User Uploads Document
|
v
Document Processing Layer
|
v
Text Extraction (PDF / Image Parser)
|
v
SpaCy NLP Pipeline
(Custom NER Model)
|
v
Entity Extraction
(Rent, Deposit, Deadline, Lock-in)
|
v
Rule Engine (Python + SQLite)
|
v
Risk Detection & Legal Evaluation
|
v
Output Generator
|           |
v           v
Risk Score   Simplified Summary
|
v
Audio Explanation

```

---

# Technology Stack

### Backend
- Python
- Flask
- Flask-SocketIO
- SpaCy (custom NLP training)

### Database
- SQLite

### Frontend
- React.js

### NLP
- Custom SpaCy NER model

### Other Tools
- Prodigy / Label Studio (annotation)
- PyPDF / Tesseract (document text extraction)
- gTTS / Coqui TTS (offline audio)

---

# Repository Structure

```

nivaran/

backend/
app.py
routes/
services/
nlp/
train_ner.py
spacy_pipeline.py
rule_engine/
rule_engine.py
rules.db
utils/

frontend/
src/
components/
pages/

dataset/
rental_contracts/
civic_notices/

annotations/

models/
spacy_model/

docs/
architecture.md

```

---

# Development Roadmap

The project will be implemented in **phases**, each producing a working deliverable.

---

# Phase 1 — Data Collection & Annotation

### Goal
Create a dataset to train the custom SpaCy NER model.

### Tasks

1 Collect rental agreements  
2 Collect civic notices  
3 Clean the text  
4 Annotate legal entities

### Entities to Label

```

RENT_AMOUNT
DEPOSIT_AMOUNT
DUE_DATE
LOCKIN_PERIOD
PENALTY_CLAUSE
UTILITY_AMOUNT
NOTICE_DATE

```

### Prompt for Implementation

```

Build a dataset preparation pipeline for legal document analysis.

Requirements:

* Input: Rental agreements and civic notices (PDF or text)
* Clean and normalize text
* Create annotation format compatible with SpaCy
* Label entities such as rent, deposit, penalty clause, lock-in period, due date

Output:
Annotated dataset ready for SpaCy training.

```

Deliverable

```

dataset/
annotations/
training_data.spacy

```

---

# Phase 2 — Train Custom SpaCy NER Model

### Goal
Train a domain-specific NLP model.

### Tasks

- Create training pipeline
- Train SpaCy NER model
- Evaluate accuracy
- Save trained model

### Prompt for Implementation

```

Train a custom Named Entity Recognition model using SpaCy.

Requirements:

* Input: annotated dataset of legal documents
* Train entities:
  RENT_AMOUNT
  DEPOSIT_AMOUNT
  LOCKIN_PERIOD
  PENALTY_CLAUSE
  DUE_DATE
* Use SpaCy training pipeline
* Split dataset into train/test
* Evaluate using precision, recall, F1
* Save model for production inference

```

Deliverable

```

models/legal_ner_model/

```

Expected performance

```

Entity extraction accuracy > 90%

```

---

# Phase 3 — Document Processing Pipeline

### Goal
Convert uploaded documents into analyzable text.

### Tasks

- File upload API
- PDF parser
- Image OCR
- Text normalization

### Prompt

```

Build a document processing pipeline.

Requirements:

* Accept PDF or image uploads
* Extract raw text
* Clean formatting
* Pass the text to the SpaCy NLP model

Output:
Clean text ready for entity extraction

```

Deliverable

```

/upload API
text extraction module

```

---

# Phase 4 — Entity Extraction Layer

### Goal
Extract legal entities using SpaCy model.

### Tasks

- Load trained SpaCy model
- Extract entities
- Structure them into JSON

### Prompt

```

Implement an NLP inference service using the trained SpaCy model.

Requirements:

* Input: document text
* Run SpaCy pipeline
* Extract entities
* Return structured JSON output

Example Output

{
rent: 15000,
deposit: 30000,
lockin_period: "6 months",
penalty_clause: "1 month rent",
due_date: "5th of every month"
}

```

Deliverable

```

entity_extractor.py

```

---

# Phase 5 — Legal Rule Engine

### Goal
Evaluate contracts using legal rules.

### Example Rules

```

IF deposit > 2 * rent
FLAG excessive deposit

IF lockin_period > 12 months
FLAG restrictive clause

IF penalty_clause contains "non refundable"
FLAG risk

```

### Prompt

```

Build a deterministic rule engine that evaluates extracted entities.

Requirements:

* Input: entity JSON
* Rules stored in SQLite
* Evaluate legal compliance
* Return risk flags

Output example

{
risk_score: 70,
flags: [
"Excessive deposit",
"Lock-in period too long"
]
}

```

Deliverable

```

rule_engine.py
rules.db

```

---

# Phase 6 — Simplification Engine

### Goal
Convert legal text into simple language.

Example

```

Original:
Tenant must deposit Rs 50,000 security refundable subject to conditions.

Simplified:
You must pay a ₹50,000 deposit before moving in.

```

### Prompt

```

Build a legal text simplification engine.

Requirements:

* Use rule-based templates
* Generate short explanations
* Avoid complex legal vocabulary

```

Deliverable

```

summary_generator.py

```

---

# Phase 7 — Audio Explanation (Civic-Ease)

### Goal
Generate spoken summaries.

Example Output

```

"You need to pay ₹500 before Tuesday to avoid a penalty."

```

### Prompt

```

Convert simplified explanations into speech.

Requirements:

* Support Hindi and English
* Output audio file
* Optimize for elderly users

```

Deliverable

```

tts_service.py

```

---

# Phase 8 — Real-Time Analysis

### Goal
Stream document analysis updates.

### Technology

Flask-SocketIO

### Prompt

```

Implement real-time processing updates using WebSockets.

Requirements:

* Stream analysis progress
* Notify when clauses are detected
* Display risk alerts

```

Deliverable

```

socket server
live progress UI

```

---

# Phase 9 — Frontend Dashboard

### Features

Upload document  
View extracted entities  
View risk score  
Listen to explanation  

### Prompt

```

Build a React dashboard for Nivaran.

Features:

* Upload document
* Show live analysis progress
* Display extracted legal entities
* Show risk flags
* Play audio explanation

```

Deliverable

```

React web interface

```

---

# Evaluation Metrics

### NLP Accuracy
```

> 90% entity extraction accuracy

```

### Rule Engine Reliability
```

Zero false negatives for critical clauses

```

### Latency
```

< 5 seconds per document

```

---

# Ethical Design

Nivaran follows strict privacy principles:

- Documents processed **in memory only**
- No document storage
- No personal data retention
- Transparent rule-based decisions

---

# Future Improvements

- Multilingual document understanding
- Mobile app
- Legal clause classification
- Automatic clause segmentation
- Model Tenancy Act compliance checker

---

# Contributors

Backend + NLP
Rohit

Frontend + UX
Bhavya

Project
Nivaran Team
```

---

✅ This README gives you:

* **Phase-wise deliverables**
* **Implementation prompts**
* **Architecture**
* **Training pipeline**
* **NLP design**

---

💡 If you want, I can also show you:

1️⃣ **Complete system architecture diagram (professional level for reports)**
2️⃣ **SpaCy NER training pipeline for legal documents**
3️⃣ **How to build a dataset for this project**
4️⃣ **Rule engine design used in real legal tech startups**

That would make this project **very strong for ML/NLP portfolios and research.**
