from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.nlp.pipeline import generate_quiz_from_pdf


app = FastAPI(
    title="Offline NLP-Based PDF Quiz Generator",
    description="Generate quiz questions from uploaded PDFs using only local NLP libraries.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "offline-pdf-quiz-generator"}


@app.post("/api/generate-quiz")
async def generate_quiz(
    file: UploadFile = File(...),
    questions_per_type: int = Form(4),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    try:
        pdf_bytes = await file.read()
        result = generate_quiz_from_pdf(pdf_bytes, questions_per_type=max(1, min(questions_per_type, 10)))
        payload = asdict(result)
        payload["quiz"] = [asdict(question) for question in result.quiz]
        payload["keywords"] = [asdict(keyword) for keyword in result.keywords]
        payload["entities"] = [asdict(entity) for entity in result.entities]
        return payload
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - surfaced in API response
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {exc}") from exc
