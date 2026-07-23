# 💊 AI-Powered Pharmaceutical Complaint Management System

An intelligent complaint intake and Quality Management System (QMS) built for pharmaceutical manufacturing industries. The system automatically processes customer complaints from emails, PDFs, DOCX, TXT files, or free-text inputs, extracts structured information using AI, performs pharmaceutical risk assessment, and assists Quality Assurance (QA) teams in complaint investigation.

---

# 🚀 Project Overview

Pharmaceutical companies receive complaints in multiple unstructured formats such as emails, documents, and customer reports. Manually extracting complaint details, verifying completeness, assessing risk, and maintaining complaint records is time-consuming and error-prone.

This project automates the entire complaint intake workflow using a multi-agent AI pipeline powered by **LangGraph** and **Groq LLMs**, enabling QA teams to process complaints faster while maintaining consistency and regulatory compliance.

---

# ✨ Key Features

- 📄 Upload complaints in PDF, DOCX, TXT, or EML format
- 💬 Accept free-text complaint descriptions
- 🤖 AI-powered complaint information extraction
- ✅ Automatic complaint completeness verification
- ❓ Intelligent follow-up questions for missing information
- ⚠️ Pharmaceutical QMS-based severity and risk assessment
- 📝 AI-generated investigation summary
- ✏️ Editable complaint form before submission
- 💾 Complaint storage using SQL database
- 🔍 Duplicate complaint detection
- 📊 REST APIs with Swagger documentation

---

# 🏗️ System Architecture

```
                        User
                          │
          ┌───────────────┴───────────────┐
          │                               │
     Upload Complaint              Enter Complaint
          │                               │
          └───────────────┬───────────────┘
                          │
                  React Frontend (Redux)
                          │
                    FastAPI REST APIs
                          │
                 Document Parser Layer
                          │
                   LangGraph AI Workflow
                          │
     ┌──────────────┬──────────────┬──────────────┐
     │              │              │              │
 Extraction   Completeness    QMS Reasoning   Summary
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                          │
                   SQLAlchemy ORM
                          │
                   PostgreSQL / SQLite
```

---

# 🤖 AI Workflow

The complaint processing pipeline consists of multiple AI agents orchestrated using **LangGraph**.

### 1️⃣ Extraction Agent

Extracts structured complaint information from unstructured text.

Extracted fields include:

- Customer Name
- Product Name
- Batch Number
- Manufacturing Date
- Expiry Date
- Complaint Description
- Complaint Type
- Quantity Affected

---

### 2️⃣ Completeness Agent

Verifies whether all mandatory complaint fields are available.

If information is missing, the assistant automatically asks follow-up questions instead of making assumptions.

---

### 3️⃣ QMS Reasoning Agent

Applies pharmaceutical Quality Management System (QMS) principles to determine:

- Severity
- Priority
- Risk Assessment
- Suggested Corrective Action

---

### 4️⃣ Summary Agent

Generates a concise complaint summary suitable for QA investigation records.

---

# 🔄 End-to-End Workflow

```
Customer Complaint
        │
        ▼
 Upload / Chat Input
        │
        ▼
 Text Extraction
        │
        ▼
 AI Information Extraction
        │
        ▼
 Completeness Validation
        │
 Missing Information?
        │
    Yes ─────► Ask User
        │
       No
        │
        ▼
 QMS Risk Assessment
        │
        ▼
 AI Summary Generation
        │
        ▼
 QA Review
        │
        ▼
 Save Complaint
        │
        ▼
 Database
```

---

# 🛠️ Technology Stack

## Frontend

- React.js
- Redux Toolkit
- CSS
- Axios

## Backend

- FastAPI
- Python
- SQLAlchemy
- Pydantic

## Artificial Intelligence

- LangGraph
- Groq LLM
- Prompt Engineering

## Database

- PostgreSQL
- SQLite

## File Processing

- PDF Parser
- DOCX Parser
- Email Parser
- TXT Reader

---

# 📂 Project Structure

```
frontend/
│
├── components/
├── store/
├── api.js
├── App.jsx
└── main.jsx

backend/
│
├── main.py
├── schemas.py
├── parsers.py
│
├── agents/
│   ├── graph.py
│   ├── nodes.py
│   ├── llm.py
│   ├── state.py
│   └── duplicate_check.py
│
├── prompts/
│
└── database/
    ├── db.py
    └── models.py
```

---

# 🗄️ Database Design

The application uses SQLAlchemy ORM with a normalized relational database.

Main entities include:

- Customer
- Product
- Complaint
- Conversation
- Attachment

Relationships ensure efficient storage while avoiding redundant data.

---

# 🔒 Data Validation

The system validates complaint information before saving.

Examples include:

- Expiry Date must be after Manufacturing Date
- Complaint Date cannot be in the future
- Quantity must be positive
- Mandatory complaint fields cannot be empty

Validation is implemented using **Pydantic**.

---

# 🎯 Why LangGraph?

Instead of relying on a single LLM prompt, the application uses a multi-agent workflow.

Benefits include:

- Modular AI pipeline
- Better extraction accuracy
- Interactive clarification
- Improved maintainability
- Easier debugging
- Scalable architecture

---

# 📡 REST API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/upload` | Upload complaint document |
| POST | `/chat` | Chat with AI assistant |
| POST | `/complaints` | Save complaint |
| GET | `/complaints` | Retrieve all complaints |
| GET | `/complaints/{id}` | Retrieve complaint by ID |
| PUT | `/complaints/{id}` | Update complaint |

Swagger Documentation:

```
http://localhost:8000/docs
```

---

# 🚀 Getting Started

## Backend

```bash
pip install -r backend/requirements.txt

uvicorn backend.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 📸 Application Flow

1. Upload complaint document or enter complaint text.
2. AI extracts structured complaint information.
3. Missing information is requested automatically.
4. AI performs pharmaceutical QMS reasoning.
5. QA reviews and edits extracted information.
6. Complaint is saved into the database.

---

# 🎯 Future Enhancements

- User Authentication & Role-Based Access Control
- Dashboard Analytics
- Complaint Trend Visualization
- Email Integration
- OCR Support for Scanned Documents
- Cloud Deployment
- Audit Trail & Activity Logs
- Notification System

---

# 👨‍💻 Author

**Gokulalaakshmi M**

Computer Science Engineer | Full Stack Developer | AI & Machine Learning Enthusiast

---

# ⭐ If you found this project interesting, consider giving it a star!
