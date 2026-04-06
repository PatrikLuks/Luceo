"""Post-LLM output guardrails — defense in depth.

Scans LLM responses for forbidden patterns that should not appear
in Luceo's output, even if the system prompt was bypassed.
"""

import re

from src.core.text_utils import normalize_text

# Patterns are written WITHOUT diacritics — normalization strips them
_DIAGNOSTIC_PATTERNS = [
    r"\bF1[0-9]\.[0-9]\b",  # ICD-10 codes
    r"\b(diagnostikuji|vase diagnoza|trpite)\b",
    r"\bmas\s+(diagnozu|poruchu|nemoc)\b",
    r"\bjsi\s+alkoholi[ck]\w*\b",  # alkoholik, alkoholicka, alkoholikem...
    r"\bjsi\s+zavisl[yae]\w*\b",  # zavisly, zavisla, zavisle, zavislym...
]

_MEDICATION_PATTERNS = [
    r"\b(naltrexon|acamprosat|disulfiram|antabus|campral)\b",
    r"\b(baclofen|baklofen|gabapentin|topiramat|nalmefen|nalmefene)\b",
    r"\b(diazepam|lorazepam|alprazolam|xanax|lexaurin)\b",
    r"\b(sertralin|fluoxetin|escitalopram|citalopram|paroxetin)\b",
    r"\b(\d+\s*mg\s*(denne|rano|vecer|2x|3x|daily|twice|once))\b",
]

_COMPILED_DIAGNOSTIC = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _DIAGNOSTIC_PATTERNS]
_COMPILED_MEDICATION = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _MEDICATION_PATTERNS]

SAFE_FALLBACK = (
    "Na toto se prosím zeptej svého lékaře. "
    "Mohu ti ale pomoci s technikami zvládání chutí, sledováním nálad "
    "a dalšími podpůrnými nástroji."
)


def check_response_guardrails(response: str) -> tuple[bool, str | None]:
    """Check LLM response for forbidden content.

    Returns (is_safe, reason). If not safe, caller should replace
    the offending response with SAFE_FALLBACK.
    """
    normalized = normalize_text(response)

    for pattern in _COMPILED_DIAGNOSTIC:
        if pattern.search(normalized):
            return False, "Diagnostic language detected"

    for pattern in _COMPILED_MEDICATION:
        if pattern.search(normalized):
            return False, "Medication recommendation detected"

    return True, None
