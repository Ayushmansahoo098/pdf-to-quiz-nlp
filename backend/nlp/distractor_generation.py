from __future__ import annotations

import hashlib
import random
import re
from difflib import SequenceMatcher
from typing import Iterable

from nltk.corpus import wordnet as wn

from .keyword_extraction import KeywordItem
from .ner import EntityItem


_FALLBACK_WORDS = [
    "analysis",
    "process",
    "system",
    "method",
    "network",
    "model",
    "device",
    "service",
    "module",
    "pattern",
    "feature",
    "signal",
]

_LABEL_FALLBACKS = {
    "PERSON": ["Alan Turing", "Marie Curie", "Ada Lovelace", "Nikola Tesla"],
    "DATE": ["1999", "2005", "2012", "2020"],
    "TIME": ["morning", "noon", "evening", "midnight"],
    "GPE": ["London", "Paris", "Tokyo", "Berlin"],
    "LOC": ["mountain", "river", "desert", "coast"],
    "ORG": ["Google", "UNICEF", "Microsoft", "NASA"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _seed_from_text(text: str) -> int:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _wordnet_candidates(answer: str) -> list[str]:
    candidates: list[str] = []
    base_terms = [token for token in re.findall(r"[A-Za-z]+", answer) if token]
    if not base_terms:
        return candidates

    try:
        synsets = wn.synsets(base_terms[-1].lower())
    except LookupError:
        return candidates

    for synset in synsets[:4]:
        related_synsets = (
            synset.hypernyms()
            + synset.hyponyms()
            + synset.similar_tos()
            + synset.instance_hypernyms()
            + synset.instance_hyponyms()
        )
        for related_synset in related_synsets:
            for lemma in related_synset.lemma_names():
                lemma_text = lemma.replace("_", " ")
                if lemma_text:
                    candidates.append(lemma_text)
        for lemma in synset.lemma_names():
            lemma_text = lemma.replace("_", " ")
            if lemma_text:
                candidates.append(lemma_text)

    return candidates


def _label_candidates(label: str | None, entities: Iterable[EntityItem], keywords: Iterable[KeywordItem]) -> list[str]:
    label = (label or "").upper()
    candidates: list[str] = []

    if label in {"PERSON", "DATE", "TIME", "GPE", "LOC", "ORG"}:
        candidates.extend(entity.text for entity in entities if entity.label.upper() == label)

    if not candidates:
        candidates.extend(keyword.text for keyword in keywords)

    return candidates


def _rank_candidates(answer: str, candidates: Iterable[str]) -> list[str]:
    normalized_answer = _normalize(answer)
    scored: list[tuple[float, str]] = []
    for candidate in candidates:
        normalized_candidate = _normalize(candidate)
        if not normalized_candidate or normalized_candidate == normalized_answer:
            continue
        if normalized_candidate in normalized_answer or normalized_answer in normalized_candidate:
            continue
        similarity = SequenceMatcher(None, normalized_answer, normalized_candidate).ratio()
        if similarity >= 0.15:
            scored.append((similarity, candidate))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [candidate for _, candidate in scored]


def generate_distractors(
    answer: str,
    label: str | None,
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
    count: int = 3,
) -> list[str]:
    answer = answer.strip()
    if not answer:
        return []

    candidates: list[str] = []
    candidates.extend(_wordnet_candidates(answer))
    candidates.extend(_label_candidates(label, entities, keywords))
    candidates.extend(_FALLBACK_WORDS)

    ranked_candidates = _rank_candidates(answer, candidates)
    if len(ranked_candidates) < count:
        ranked_candidates.extend(candidate for candidate in candidates if candidate not in ranked_candidates)

    unique: list[str] = []
    normalized_answer = _normalize(answer)
    for candidate in ranked_candidates:
        normalized_candidate = _normalize(candidate)
        if not normalized_candidate or normalized_candidate == normalized_answer:
            continue
        if normalized_candidate in {_normalize(item) for item in unique}:
            continue
        unique.append(candidate)
        if len(unique) >= count:
            break

    if len(unique) < count:
        fallback_pool = _LABEL_FALLBACKS.get((label or "").upper(), _FALLBACK_WORDS)
        for item in fallback_pool:
            if _normalize(item) != normalized_answer and item not in unique:
                unique.append(item)
            if len(unique) >= count:
                break

    if len(unique) < count:
        rng = random.Random(_seed_from_text(answer))
        while len(unique) < count:
            candidate = rng.choice(_FALLBACK_WORDS)
            if _normalize(candidate) != normalized_answer and candidate not in unique:
                unique.append(candidate)

    return unique[:count]
