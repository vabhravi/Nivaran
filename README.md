# 🛡️ NIVARAN — AI-Powered Civic & Legal Companion for Digital Inclusion

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![SpaCy](https://img.shields.io/badge/SpaCy-3.8-09A3D5?logo=spacy)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)

NIVARAN bridges the gap between complex bureaucratic/legal documents and the common citizen using a **Hybrid AI** approach — combining **custom SpaCy NER** + **deterministic Rule-Based Logic (SQLite)** — to not just read, but **AUDIT** documents.

---

## 📋 Table of Contents

- [Modules](#-modules)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the App](#-running-the-app)
- [API Reference](#-api-reference)
- [Training Custom NER Models](#-training-custom-ner-models)
- [Privacy & Ethics](#-privacy--ethics)

---

## 🧩 Modules

### 🏛️ Module 1: Civic-Ease (for Elderly Users)
Upload government notices (electricity bills, tax letters, bank notices). The system extracts actionable intent and converts it to a **simple Hindi audio summary**.

- OCR via Gemini 1.5 Flash → SpaCy NER → Hindi simplification → gTTS audio
- High contrast UI with large buttons (min 48px tap targets)
- Hindi number localization: ₹500 → "Paanch Sau Rupaye"

### 🏠 Module 2: Rent-Right (for Students/Tenants)
Upload a rental agreement PDF/image. The system scans for **predatory or illegal clauses**, flags violations of the **Model Tenancy Act, 2021**, and outputs a **Risk Score (0–10)**.

- OCR → NER → SQLite Rule Engine → Risk Score (Red/Amber/Green)
- 8 pre-loaded rules covering deposit limits, no-refund traps, lock-in periods, etc.
- Legal citations for every flagged clause

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.9+ / Flask 3.1 / Flask-SocketIO |
| Frontend | React 18 / Vite / React Router |
| NLP Engine | SpaCy 3.8 (custom NER + regex fallback) |
| OCR/Vision | Google Gemini 1.5 Flash API |
| Database | SQLite (raw SQL, no ORM) |
| Text-to-Speech | gTTS (Hindi) |
| Real-time | Flask-SocketIO + Socket.IO client |

---

## 📁 Project Structure

```
Nivaran/
├── nivaran-backend/
│   ├── app.py                      # Flask + SocketIO entry point
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── routes/
│   │   ├── civic_ease.py           # /api/civic-ease/upload
│   │   └── rent_right.py           # /api/rent-right/upload
│   ├── nlp/
│   │   ├── ocr.py                  # Gemini 1.5 Flash OCR
│   │   ├── ner_model.py            # SpaCy NER + regex fallback
│   │   └── simplifier.py           # Hindi simplification + gTTS
│   ├── rules/
│   │   ├── rule_engine.py          # SQLite rule evaluator
│   │   └── schema.sql              # Legal rules schema + seed data
│   ├── scripts/
│   │   └── prepare_training_data.py # SpaCy annotation script
│   ├── models/nivaran_ner/         # Trained SpaCy models (after training)
│   ├── database/rules.db           # SQLite database (auto-created)
│   └── temp_audio/                 # Temporary audio files (auto-cleaned)
│
├── nivaran-frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css               # Complete design system
│       ├── pages/
│       │   ├── Home.jsx            # Landing + module selector
│       │   ├── CivicEase.jsx       # Elderly-friendly upload + audio
│       │   └── RentRight.jsx       # Rental agreement scanner
│       ├── components/
│       │   ├── FileUploader.jsx    # Drag-and-drop upload
│       │   ├── ProgressStream.jsx  # Real-time progress bar
│       │   ├── RiskDial.jsx        # Animated risk score dial
│       │   ├── ClauseCard.jsx      # Expandable clause card
│       │   ├── AudioPlayer.jsx     # Hindi audio playback
│       │   └── DisclaimerModal.jsx # Legal disclaimer modal
│       └── utils/
│           └── socket.js           # Socket.IO client config
│
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/app/apikey)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd nivaran-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download SpaCy base model
python -m spacy download en_core_web_sm

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd nivaran-frontend

# Install dependencies
npm install
```

---

## ▶️ Running the App

### Start Backend (Terminal 1)

```bash
cd nivaran-backend
source venv/bin/activate
python app.py
```

The Flask server starts at **http://localhost:5000**.
The SQLite database is auto-initialized from `schema.sql` on first run.

### Start Frontend (Terminal 2)

```bash
cd nivaran-frontend
npm run dev
```

The React dev server starts at **http://localhost:3000**.
API calls are proxied to the backend via Vite config.

### Access the App

Open **http://localhost:3000** in your browser.

---

## 📡 API Reference

### Health Check
```
GET /api/health
→ { status: "healthy", service: "NIVARAN Backend", version: "1.0.0" }
```

### Civic-Ease: Upload Document
```
POST /api/civic-ease/upload
Content-Type: multipart/form-data
Body: document (file), sid (optional Socket.IO ID)

→ {
    audio_url: "/audio/nivaran_abc123.mp3",
    summary_text: "Namaste. BSES ki taraf se yeh suchna hai...",
    extracted_entities: { dates, amounts, organizations, actions },
    ocr_text: "...",
    confidence: 0.92,
    low_confidence_warning: false
  }
```

### Rent-Right: Upload Agreement
```
POST /api/rent-right/upload
Content-Type: multipart/form-data
Body: document (file), sid (optional Socket.IO ID)

→ {
    risk_score: 4.5,
    risk_level: "AMBER",
    flagged_clauses: [{ rule_name, severity, violation_description, legal_citation, ... }],
    total_flags: 3,
    severity_breakdown: { CRITICAL: 1, HIGH: 1, MEDIUM: 1, LOW: 0 },
    extracted_entities: { rent_amount, deposit_amount, ... },
    confidence: 0.88,
    low_confidence_warning: false
  }
```

### WebSocket Events
```
Event: "analysis_progress"
Data: { stage, message, percent, module }
```

---

## 🧠 Training Custom NER Models

The app works out-of-the-box with **regex-based fallback extraction**. For improved accuracy, train custom SpaCy NER models:

```bash
cd nivaran-backend

# 1. Prepare training data
python scripts/prepare_training_data.py

# 2. Generate SpaCy config
python -m spacy init config config.cfg --lang en --pipeline ner --optimize efficiency

# 3. Train civic notice model
python -m spacy train training_data/civic_notice_ner_config.cfg \
    --output models/nivaran_ner/civic_notice_ner \
    --paths.train training_data/civic_notice_ner_train.spacy \
    --paths.dev training_data/civic_notice_ner_train.spacy

# 4. Train rent agreement model
python -m spacy train training_data/rent_agreement_ner_config.cfg \
    --output models/nivaran_ner/rent_agreement_ner \
    --paths.train training_data/rent_agreement_ner_train.spacy \
    --paths.dev training_data/rent_agreement_ner_train.spacy
```

The trained models are automatically loaded by `ner_model.py` when placed in the `models/nivaran_ner/` directory.

---

## 🔒 Privacy & Ethics

| Principle | Implementation |
|-----------|---------------|
| **Stateless Processing** | Documents are processed in-memory only. Never written to disk permanently. |
| **Algorithmic Fairness** | Rule engine evaluates clause text only — no names, gender, or location. |
| **Explainability** | Every flagged risk cites the specific legal section violated. |
| **User Consent** | Mandatory disclaimer modal before any analysis begins. |
| **Confidence Scoring** | Low OCR quality triggers a visible warning to the user. |
| **DPDP Act 2023** | Compliant — no personal data retention. |

---

## 📄 Legal Rules (Pre-loaded)

| # | Rule Name | Severity | Legal Citation |
|---|-----------|----------|---------------|
| 1 | Excessive Security Deposit | HIGH | Section 11(2), Model Tenancy Act, 2021 |
| 2 | No-Refund Clause | CRITICAL | Section 11(4), Model Tenancy Act, 2021 |
| 3 | Excessive Lock-in Period | HIGH | Section 21(1), Model Tenancy Act, 2021 |
| 4 | Insufficient Notice Period | MEDIUM | Section 21(2), Model Tenancy Act, 2021 |
| 5 | Unreasonable Penalty Clause | HIGH | Section 21(4), Model Tenancy Act, 2021 |
| 6 | Missing Termination Clause | HIGH | Section 21, Model Tenancy Act, 2021 |
| 7 | Uncapped Rent Escalation | MEDIUM | Section 9(2), Model Tenancy Act, 2021 |
| 8 | Unrestricted Landlord Entry | MEDIUM | Section 18, Model Tenancy Act, 2021 |

---

## 📝 License

This project is for educational and informational purposes. It does not constitute legal advice.

---

**Built with 🇮🇳 for Digital India**
