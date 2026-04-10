# 📚 Offline NLP-Based PDF Quiz Generator

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-100968?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

An entirely local, privacy-first web application that converts uploaded PDF documents into fully interactive quizzes using advanced Natural Language Processing (NLP)—**without relying on any external APIs like OpenAI.**

## ✨ Features

- **Privacy-First Processing:** Everything stays on your local machine. No external API calls are made across the network.
- **Smart Text Extraction:** Extracts clean, manageable text directly from raw PDFs.
- **Advanced NLP Techniques:** Identifies keywords, entities, and ranks sentence importance.
- **Dynamic Quiz Generation:** Automatically generates a variety of question types based on the document's content:
  - Multiple Choice Questions (MCQs)
  - Fill-in-the-blanks
  - WH Questions (Who, What, Where, etc.)
  - True/False Questions
- **Smart Distractors:** Uses WordNet to dynamically generate plausible wrong answers for MCQs.
- **Interactive UI:** Provides a polished, responsive, browser-based quiz taking and grading experience.

---

## 🛠 Tech Stack

### Frontend
- **React.js** (Component-based UI)
- **Vite** (Next-generation lightning-fast build tool)
- **Tailwind CSS** (Utility-first styling for a beautiful interface)

### Backend
- **FastAPI** (High-performance Python web framework)
- **PyMuPDF** (Speedy PDF parsing)
- **NLTK / spaCy** (Entity detection, tokenization, stopword removal)
- **Scikit-learn** (TF-IDF implementation for sentence ranking)
- **WordNet** (Vocabulary and synonym relations for distractors)

---

## 🚀 Getting Started

Follow the steps below to set up the project on your local machine.

### Prerequisites

- Node.js (v16.x or newer recommended)
- Python 3.9+ 

### 1. Backend Setup

Open a terminal and set up the Python environment:

```bash
# Navigate to the project root
cd /path/to/pdf-to-quiz-nlp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install all backend dependencies
pip install -r backend/requirements.txt

# Download required NLP models (spaCy & NLTK datasets)
python backend/scripts/setup_nlp_assets.py

# Start the FastAPI server
uvicorn backend.main:app --reload --port 8000
```
> **Note:** If the `en_core_web_sm` model fails to load, the backend will gracefully fall back to alternative processing, though for best entity-detection quality, ensuring spaCy is properly installed is highly recommended.

### 2. Frontend Setup

Open a separate terminal and initialize the user interface:

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

### 3. Usage

1. **Access the App:** Open your browser and navigate to `http://localhost:5173`.
2. **Upload PDF:** Drag and drop or select your educational PDF document.
3. **Generate:** The backend will crunch the document utilizing its NLP engines and generate a tailored quiz.
4. **Test Yourself:** Take the quiz directly in your browser and receive your auto-graded score at the end!

## ⚙️ Configuration

By default, the Vite frontend proxies requests or points to `http://localhost:8000`. If you wish to configure a different backend API port, you can explicitly map it:
```bash
export VITE_API_BASE_URL=http://localhost:8000
```

## 📜 License

Created for completely offline, automated educational assessment! Feel free to modify and adapt to your needs.
