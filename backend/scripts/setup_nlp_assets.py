from __future__ import annotations

import subprocess
import sys

import nltk


NLTK_PACKAGES = [
    "punkt",
    "stopwords",
    "wordnet",
    "omw-1.4",
]


def ensure_nltk_data() -> None:
    for package in NLTK_PACKAGES:
        try:
            resource_path = {
                "punkt": "tokenizers/punkt",
                "stopwords": "corpora/stopwords",
                "wordnet": "corpora/wordnet",
                "omw-1.4": "corpora/omw-1.4",
            }[package]
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package)


def ensure_spacy_model() -> None:
    try:
        import spacy

        spacy.load("en_core_web_sm")
    except Exception:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])


if __name__ == "__main__":
    ensure_nltk_data()
    ensure_spacy_model()
    print("NLP assets are ready.")
