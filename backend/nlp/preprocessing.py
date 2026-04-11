from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable

import fitz
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize as nltk_sent_tokenize
from nltk.tokenize import word_tokenize as nltk_word_tokenize
from nltk.tokenize import wordpunct_tokenize


_FALLBACK_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}


@dataclass
class SentenceFeatures:
    index: int
    text: str
    tokens: list[str] = field(default_factory=list)
    lemmas: list[str] = field(default_factory=list)
    cleaned_text: str = ""


@dataclass
class PreprocessedDocument:
    raw_text: str
    sentences: list[SentenceFeatures]
    tokens: list[str]
    lemmas: list[str]
    filtered_tokens: list[str]
    page_count: int


@lru_cache(maxsize=1)
def _lemmatizer() -> WordNetLemmatizer:
    return WordNetLemmatizer()


@lru_cache(maxsize=1)
def _stopword_set() -> set[str]:
    try:
        return set(stopwords.words("english"))
    except LookupError:
        return set(_FALLBACK_STOPWORDS)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    # Format bullets
    text = re.sub(r"\s*([•·▪])\s*", r"\n• ", text)
    # Ensure there's a space after bullet points
    text = re.sub(r"(?<=\n[•·▪])(?=[^\s])", " ", text)
    # Remove excessive newlines but preserve formatting
    text = re.sub(r" \n", "\n", text)
    text = re.sub(r"\n ", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_bytes: bytes) -> tuple[str, int]:
    if not pdf_bytes:
        return "", 0

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            text = "\n".join(page.get_text("text") for page in document)
            return normalize_whitespace(text), document.page_count
    except Exception as exc:  # pragma: no cover
        raise ValueError("Unable to extract text from the supplied PDF.") from exc


def safe_sentence_tokenize(text: str) -> list[str]:
    if not text:
        return []

    try:
        sentences = nltk_sent_tokenize(text)
    except LookupError:
        sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence and sentence.strip()]


def safe_word_tokenize(text: str) -> list[str]:
    if not text:
        return []

    try:
        tokens = nltk_word_tokenize(text)
    except LookupError:
        tokens = wordpunct_tokenize(text)
    return [token.strip() for token in tokens if token and token.strip()]


def _lemma(token: str) -> str:
    return _lemmatizer().lemmatize(token.lower())


def preprocess_document(text: str, page_count: int = 0) -> PreprocessedDocument:
    normalized_text = normalize_whitespace(text)
    sentence_texts = safe_sentence_tokenize(normalized_text)
    stopword_lookup = _stopword_set()

    sentences: list[SentenceFeatures] = []
    all_tokens: list[str] = []
    all_lemmas: list[str] = []
    filtered_tokens: list[str] = []

    for index, sentence in enumerate(sentence_texts):
        tokens = safe_word_tokenize(sentence)
        lemmas = [_lemma(token) for token in tokens]
        cleaned = [
            lemma
            for lemma in lemmas
            if lemma.isalpha() and lemma not in stopword_lookup and len(lemma) > 2
        ]

        all_tokens.extend(tokens)
        all_lemmas.extend(lemmas)
        filtered_tokens.extend(cleaned)
        sentences.append(
            SentenceFeatures(
                index=index,
                text=sentence,
                tokens=tokens,
                lemmas=lemmas,
                cleaned_text=" ".join(cleaned),
            )
        )

    return PreprocessedDocument(
        raw_text=normalized_text,
        sentences=sentences,
        tokens=all_tokens,
        lemmas=all_lemmas,
        filtered_tokens=filtered_tokens,
        page_count=page_count,
    )


def sentence_contains_any(sentence: str, candidates: Iterable[str]) -> bool:
    sentence_lower = sentence.lower()
    return any(candidate.lower() in sentence_lower for candidate in candidates)
