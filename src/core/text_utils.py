"""Shared text normalization for safety-critical modules.

Used by crisis.py (pre-LLM crisis detection) and guardrails.py (post-LLM
output filtering). Both modules need identical normalization so that
keyword/pattern matching works consistently.

This module intentionally has zero external dependencies — only stdlib.
"""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Strip diacritics, zero-width characters, lowercase, collapse whitespace."""
    # Remove zero-width and invisible characters that could bypass keyword matching
    text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad\u2060\u180e]", "", text)
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_text.lower().strip())
