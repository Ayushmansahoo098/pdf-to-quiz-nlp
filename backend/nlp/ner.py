from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

import spacy


@dataclass
class EntityItem:
    text: str
    label: str
    start: int
    end: int


@lru_cache(maxsize=1)
def load_spacy_pipeline():
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp, True
    except OSError:
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp, False


def extract_entities(text: str) -> tuple[list[EntityItem], bool]:
    if not text.strip():
        return [], False

    nlp, model_loaded = load_spacy_pipeline()
    if len(text) >= nlp.max_length:
        nlp.max_length = len(text) + 1000

    doc = nlp(text)
    entities: list[EntityItem] = []
    seen: set[tuple[str, str]] = set()

    for ent in doc.ents:
        key = (ent.text.lower(), ent.label_)
        if key in seen:
            continue
        seen.add(key)
        entities.append(
            EntityItem(
                text=ent.text.strip(),
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            )
        )

    return entities, model_loaded


def entity_texts(entities: Iterable[EntityItem]) -> list[str]:
    return [entity.text for entity in entities]
