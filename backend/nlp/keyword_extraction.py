from __future__ import annotations
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .preprocessing import PreprocessedDocument


@dataclass
class KeywordItem:
    text: str
    score: float


def _fallback_keywords(tokens: Iterable[str], top_n: int) -> list[KeywordItem]:
    counts = Counter(token.lower() for token in tokens if token and token.isalpha())
    return [KeywordItem(text=token, score=float(score)) for token, score in counts.most_common(top_n)]


def extract_keywords(document: PreprocessedDocument, top_n: int = 15) -> list[KeywordItem]:
    corpus = [sentence.cleaned_text for sentence in document.sentences if sentence.cleaned_text.strip()]

    if not corpus:
        return _fallback_keywords(document.filtered_tokens, top_n)

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=500,
            min_df=1,
        )
        matrix = vectorizer.fit_transform(corpus)
        scores = np.asarray(matrix.sum(axis=0)).ravel()
        ranked = sorted(
            zip(vectorizer.get_feature_names_out(), scores),
            key=lambda item: item[1],
            reverse=True,
        )
        return [KeywordItem(text=term, score=float(score)) for term, score in ranked[:top_n]]
    except ValueError:
        return _fallback_keywords(document.filtered_tokens, top_n)
import collections
import dataclasses
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .preprocessing import PreprocessedDocument


@dataclasses.dataclass
class KeywordItem:
    text: str
    score: float


def _fallback_keywords(tokens: Iterable[str], top_n: int) -> list[KeywordItem]:
    counts = collections.Counter(
        token.lower() for token in tokens if token and token.isalpha()
    )
    items = [
        KeywordItem(text=token, score=float(score))
        for token, score in counts.most_common(top_n)
    ]
    return items

 
def extract_keywords(
    document: PreprocessedDocument, top_n: int = 15
) -> list[KeywordItem]:
    corpus = [
        sentence.cleaned_text
        for sentence in document.sentences
        if sentence.cleaned_text.strip()
    ]

    if not corpus:
        return _fallback_keywords(document.filtered_tokens, top_n)

    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500, min_df=1)
        matrix = vectorizer.fit_transform(corpus)
        scores = np.asarray(matrix.sum(axis=0)).ravel()
        feature_names = vectorizer.get_feature_names_out()

        ranked = sorted(
            zip(feature_names, scores), key=lambda item: item[1], reverse=True
        )

        keywords = [
            KeywordItem(text=term, score=float(score))
            for term, score in ranked
            if term and term.strip()
        ]
        return keywords[:top_n]
    except ValueError:
        return _fallback_keywords(document.filtered_tokens, top_n)
