from __future__ import annotations

from dataclasses import dataclass

from .keyword_extraction import KeywordItem, extract_keywords
from .ner import EntityItem, extract_entities
from .preprocessing import PreprocessedDocument, extract_pdf_text, preprocess_document
from .question_generation import generate_quiz_questions, rank_sentences
from .llm_generation import call_ollama


@dataclass
class DocumentStats:
    page_count: int
    sentence_count: int
    word_count: int
    character_count: int


@dataclass
class QuizGenerationResult:
    document: DocumentStats
    keywords: list[KeywordItem]
    entities: list[EntityItem]
    quiz: list
    pipeline: dict


def _document_stats(document: PreprocessedDocument) -> DocumentStats:
    return DocumentStats(
        page_count=document.page_count,
        sentence_count=len(document.sentences),
        word_count=len(document.tokens),
        character_count=len(document.raw_text),
    )


def generate_quiz_from_pdf(pdf_bytes: bytes, questions_per_type: int = 4) -> QuizGenerationResult:
    text, page_count = extract_pdf_text(pdf_bytes)
    if not text.strip():
        raise ValueError("No extractable text was found in the uploaded PDF.")

    document = preprocess_document(text, page_count=page_count)
    keywords = extract_keywords(document, top_n=max(15, questions_per_type * 4))
    entities, model_loaded = extract_entities(document.raw_text)
    
    # Attempt offline LLM generation
    quiz = call_ollama(document.raw_text, "llama3")
    llm_used = True
    
    # Fallback to pure logic if LLM offline
    if not quiz:
        llm_used = False
        ranked_sentences = rank_sentences(document, keywords, entities)
        counts = {
            "mcq": questions_per_type,
            "fill_blank": questions_per_type,
            "wh": questions_per_type,
            "true_false": questions_per_type,
        }
        quiz = generate_quiz_questions(ranked_sentences, keywords, entities, counts)

    return QuizGenerationResult(
        document=_document_stats(document),
        keywords=keywords[: max(10, questions_per_type * 2)],
        entities=entities,
        quiz=quiz,
        pipeline={
            "spaCy_model_loaded": model_loaded,
            "extractor": "Local LLM Strategy" if llm_used else "PyMuPDF + NLTK + spaCy + TF-IDF",
            "local_only": True,
            "llm_connected": llm_used,
        },
    )
