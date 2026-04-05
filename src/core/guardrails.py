"""Post-LLM output guardrails — defense in depth.

Scans LLM responses for forbidden patterns that should not appear
in Luceo's output, even if the system prompt was bypassed.
"""

import re

_DIAGNOSTIC_PATTERNS = [
    r"\bF1[0-9]\.[0-9]\b",  # ICD-10 codes
    r"\b(diagnostikuji|vaše diagnóza|trpíte)\b",
    r"\bmáš\s+(diagnózu|poruchu|nemoc)\b",
    r"\bjsi\s+alkoholik\b",
    r"\bjsi\s+závislý\b",
]

_MEDICATION_PATTERNS = [
    r"\b(naltrexon|acampros[aá]t|disulfiram|antabus|campral)\b",
    r"\b(diazepam|lorazepam|alprazolam|xanax|lexaurin)\b",
    r"\b(sertralin|fluoxetin|escitalopram|citalopram|paroxetin)\b",
    r"\b(\d+\s*mg\s*(denně|ráno|večer|2x|3x))\b",
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
    for pattern in _COMPILED_DIAGNOSTIC:
        if pattern.search(response):
            return False, f"Diagnostic language detected: {pattern.pattern}"

    for pattern in _COMPILED_MEDICATION:
        if pattern.search(response):
            return False, f"Medication recommendation detected: {pattern.pattern}"

    return True, None
