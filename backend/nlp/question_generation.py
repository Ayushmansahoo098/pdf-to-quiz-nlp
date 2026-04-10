from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from hashlib import sha1
from random import Random
from typing import Iterable

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

from .distractor_generation import generate_distractors
from .keyword_extraction import KeywordItem
from .ner import EntityItem
from .preprocessing import PreprocessedDocument, SentenceFeatures


class QuestionType(str, Enum):
    MCQ = "mcq"
    FILL_BLANK = "fill_blank"
    WH = "wh"
    TRUE_FALSE = "true_false"


@dataclass
class QuizQuestion:
    id: str
    type: str
    prompt: str
    answer: str | bool
    options: list[str] = field(default_factory=list)
    source_sentence: str = ""
    focus_term: str = ""
    focus_label: str = ""
    explanation: str = ""


@dataclass
class RankedSentence:
    index: int
    text: str
    score: float
    sentence: SentenceFeatures


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


@lru_cache(maxsize=1)
def _stopword_lookup() -> set[str]:
    try:
        return set(stopwords.words("english"))
    except LookupError:
        return {"a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has", "have", "in", "is", "it", "of", "on", "or", "that", "the", "to", "was", "were", "with"}


def rank_sentences(
    document: PreprocessedDocument,
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
) -> list[RankedSentence]:
    sentences = [sentence for sentence in document.sentences if sentence.text.strip()]
    if not sentences:
        return []

    corpus = [sentence.cleaned_text or sentence.text.lower() for sentence in sentences]
    try:
        matrix = TfidfVectorizer(ngram_range=(1, 2), max_features=1000, min_df=1).fit_transform(corpus)
        tfidf_scores = matrix.sum(axis=1).A1
    except ValueError:
        tfidf_scores = [0.0 for _ in sentences]

    keyword_terms = [keyword.text.lower() for keyword in keywords if keyword.text]
    entity_terms = [entity.text.lower() for entity in entities if entity.text]
    stopword_lookup = _stopword_lookup()

    ranked: list[RankedSentence] = []
    for sentence, tfidf_score in zip(sentences, tfidf_scores):
        sentence_lower = sentence.text.lower()
        keyword_bonus = sum(1 for keyword in keyword_terms if keyword in sentence_lower) * 0.18
        entity_bonus = sum(1 for entity in entity_terms if entity in sentence_lower) * 0.24
        content_bonus = min(len([token for token in sentence.tokens if token.lower() not in stopword_lookup]), 24) * 0.015
        ranked.append(
            RankedSentence(
                index=sentence.index,
                text=sentence.text,
                score=float(tfidf_score) + keyword_bonus + entity_bonus + content_bonus,
                sentence=sentence,
            )
        )

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked


def _keyword_match(sentence: str, keywords: Iterable[KeywordItem]) -> str | None:
    sentence_lower = sentence.lower()
    for keyword in sorted(keywords, key=lambda item: len(item.text), reverse=True):
        if keyword.text and keyword.text.lower() in sentence_lower:
            return keyword.text
    return None


def _entity_match(sentence: str, entities: Iterable[EntityItem]) -> EntityItem | None:
    sentence_lower = sentence.lower()
    priority = {"PERSON": 0, "DATE": 1, "TIME": 1, "GPE": 2, "LOC": 2, "ORG": 3}
    candidates = [entity for entity in entities if entity.text.lower() in sentence_lower]
    if not candidates:
        return None
    candidates.sort(key=lambda entity: (priority.get(entity.label.upper(), 10), -len(entity.text)))
    return candidates[0]


def _fallback_focus_term(sentence: SentenceFeatures) -> tuple[str, str]:
    content_tokens = [
        token
        for token in sentence.tokens
        if token.isalpha() and len(token) > 3 and token.lower() not in _stopword_lookup()
    ]
    if content_tokens:
        return max(content_tokens, key=len), "KEYWORD"
    return (sentence.tokens[0] if sentence.tokens else ""), "KEYWORD"


def select_focus_term(
    sentence: SentenceFeatures,
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
) -> tuple[str, str]:
    entity_match = _entity_match(sentence.text, entities)
    if entity_match:
        return entity_match.text, entity_match.label

    keyword_match = _keyword_match(sentence.text, keywords)
    if keyword_match:
        return keyword_match, "KEYWORD"

    return _fallback_focus_term(sentence)


def _replace_first(text: str, target: str, replacement: str) -> str:
    if not target.strip():
        return text
    return re.compile(re.escape(target), re.IGNORECASE).sub(replacement, text, count=1)


def _with_question_mark(text: str) -> str:
    return text.rstrip(".!? ") + "?"


def build_fill_blank_question(sentence: SentenceFeatures, target: str) -> QuizQuestion:
    blanked = _replace_first(sentence.text, target, "_____")
    return QuizQuestion(
        id=f"fill-{sentence.index}",
        type=QuestionType.FILL_BLANK.value,
        prompt=f"Fill in the blank: {blanked}",
        answer=target,
        source_sentence=sentence.text,
        focus_term=target,
        explanation="The blank replaces an important keyword or entity identified by the NLP pipeline.",
    )


def build_wh_question(sentence: SentenceFeatures, target: str, label: str) -> QuizQuestion:
    label_upper = label.upper()
    if label_upper == "PERSON":
        wh_word = "Who"
    elif label_upper in {"DATE", "TIME"}:
        wh_word = "When"
    elif label_upper in {"GPE", "LOC"}:
        wh_word = "Where"
    else:
        wh_word = "What"

    return QuizQuestion(
        id=f"wh-{sentence.index}",
        type=QuestionType.WH.value,
        prompt=_with_question_mark(_replace_first(sentence.text, target, wh_word)),
        answer=target,
        source_sentence=sentence.text,
        focus_term=target,
        focus_label=label,
        explanation=f"The question word is chosen from the detected {label_upper or 'keyword'} type.",
    )


def _make_false_variant(
    sentence: SentenceFeatures,
    target: str,
    label: str,
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
) -> str:
    distractors = generate_distractors(target, label, keywords, entities, count=1)
    if distractors:
        return _replace_first(sentence.text, target, distractors[0])

    number_match = re.search(r"\b\d+\b", sentence.text)
    if number_match:
        number = int(number_match.group(0))
        replacement = str(number + 1 if number < 1000 else number - 1)
        return sentence.text[: number_match.start()] + replacement + sentence.text[number_match.end() :]

    auxiliary_match = re.search(r"\b(is|are|was|were|has|have|can|will|did|does)\b", sentence.text, re.IGNORECASE)
    if auxiliary_match:
        word = auxiliary_match.group(0).lower()
        replacement = "is not" if word in {"is", "was", "has", "does", "did"} else "are not"
        return sentence.text[: auxiliary_match.start()] + replacement + sentence.text[auxiliary_match.end() :]

    return "Not " + sentence.text[0].lower() + sentence.text[1:] if sentence.text else sentence.text


def build_true_false_question(
    sentence: SentenceFeatures,
    target: str,
    label: str,
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
    make_true: bool,
) -> QuizQuestion:
    statement = sentence.text if make_true else _make_false_variant(sentence, target, label, keywords, entities)
    return QuizQuestion(
        id=f"tf-{sentence.index}",
        type=QuestionType.TRUE_FALSE.value,
        prompt=f"True or False: {statement}",
        answer=make_true,
        source_sentence=sentence.text,
        focus_term=target,
        focus_label=label,
        explanation="The statement is lightly modified to create a true/false prompt.",
    )


def build_mcq_question(
    sentence: SentenceFeatures,
    target: str,
    label: str,
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
) -> QuizQuestion:
    distractors = generate_distractors(target, label, keywords, entities, count=3)
    options = [target] + distractors
    Random(int(sha1(sentence.text.encode("utf-8")).hexdigest()[:8], 16)).shuffle(options)
    return QuizQuestion(
        id=f"mcq-{sentence.index}",
        type=QuestionType.MCQ.value,
        prompt=f"Which option best completes the sentence? {_replace_first(sentence.text, target, '_____')}",
        answer=target,
        options=options,
        source_sentence=sentence.text,
        focus_term=target,
        focus_label=label,
        explanation="The correct option is the target keyword or entity extracted from the sentence.",
    )


def generate_quiz_questions(
    ranked_sentences: list[RankedSentence],
    keywords: Iterable[KeywordItem],
    entities: Iterable[EntityItem],
    counts: dict[str, int],
) -> list[QuizQuestion]:
    generated: list[QuizQuestion] = []
    per_type_counts = {key: 0 for key in ["mcq", "fill_blank", "wh", "true_false"]}

    for sentence_entry in ranked_sentences:
        sentence = sentence_entry.sentence
        target, label = select_focus_term(sentence, keywords, entities)
        if not target:
            continue

        if per_type_counts["mcq"] < counts.get("mcq", 0):
            generated.append(build_mcq_question(sentence, target, label, keywords, entities))
            per_type_counts["mcq"] += 1

        if per_type_counts["fill_blank"] < counts.get("fill_blank", 0):
            generated.append(build_fill_blank_question(sentence, target))
            per_type_counts["fill_blank"] += 1

        if per_type_counts["wh"] < counts.get("wh", 0):
            generated.append(build_wh_question(sentence, target, label))
            per_type_counts["wh"] += 1

        if per_type_counts["true_false"] < counts.get("true_false", 0):
            generated.append(
                build_true_false_question(
                    sentence,
                    target,
                    label,
                    keywords,
                    entities,
                    make_true=sentence_entry.index % 2 == 0,
                )
            )
            per_type_counts["true_false"] += 1

        if all(per_type_counts[key] >= counts.get(key, 0) for key in per_type_counts):
            break

    return generated
