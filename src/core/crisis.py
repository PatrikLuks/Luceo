"""Crisis detection layer — runs BEFORE any LLM call.

This module is intentionally dependency-free (no database, no API calls,
no imports from src.services or src.models). It must be fast (<1ms),
deterministic, and auditable. If the LLM or database is down, crisis
detection still works.

All crisis responses are predefined — NO AI improvisation during crisis.
"""

import enum
import re
import unicodedata

from pydantic import BaseModel

from src.core.crisis_contacts import CZECH_CRISIS_CONTACTS, CrisisContact


class CrisisLevel(str, enum.Enum):
    NONE = "none"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrisisResult(BaseModel):
    level: CrisisLevel
    matched_keywords: list[str]
    recommended_action: str
    crisis_contacts: list[CrisisContact]


def normalize_text(text: str) -> str:
    """Strip diacritics, lowercase, collapse whitespace."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_text.lower().strip())


# --- Keyword tiers (Czech-first, normalized/no-diacritics form) ---

_CRITICAL_PATTERNS: list[str] = [
    r"\bchci\s+zemrit\b",
    r"\bchci\s+umrit\b",
    r"\bchci\s+se\s+zabit\b",
    r"\bzabiju\s+se\b",
    r"\bsebevrazd",
    r"\bnemam\s+duvod\s+zit\b",
    r"\bskoncit\s+se?\s+vsim\b",
    r"\bskoncit\s+se\s+zivotem\b",
    r"\bnechci\s+zit\b",
    r"\bchci\s+skoncit\b",
    r"\bobesi[mt]\b",
    r"\botravit\s+se\b",
    r"\bskocim\b",
    # English equivalents
    r"\bwant\s+to\s+die\b",
    r"\bkill\s+myself\b",
    r"\bsuicid",
    r"\bend\s+(my|it\s+all)\b",
]

_HIGH_PATTERNS: list[str] = [
    r"\bchci\s+si\s+ublizit\b",
    r"\bchci\s+se\s+porezat\b",
    r"\bublizit\s+si\b",
    r"\bpredavkovat\s+se\b",
    r"\bse\s+predavkovat\b",
    r"\bpredavkovani\b",
    r"\bsebeposk",
    r"\bself.?harm",
    r"\boverdos",
]

_MEDIUM_PATTERNS: list[str] = [
    r"\brelaps\b",
    r"\bchci\s+pit\b",
    r"\bmusim\s+se\s+napit\b",
    r"\bnedokazu\s+to\b",
    r"\bneunesu\s+to\b",
    r"\bnezvladam\s+to\b",
    r"\bnemam\s+silu\b",
    r"\bvse\s+je\s+ztracen[eo]\b",
    r"\bbeznadej",
    r"\bnema\s+to\s+cenu\b",
    r"\bnema\s+to\s+smysl\b",
    r"\bnikomu\s+na\s+mne\s+nezalezi\b",
    r"\bnemohu\s+dal\b",
    r"\bnemuzu\s+dal\b",
    r"\bnevydrzim\b",
    r"\bcraving\b",
    r"\bi\s+can'?t\s+stop\b",
]

_COMPILED_CRITICAL = [re.compile(p) for p in _CRITICAL_PATTERNS]
_COMPILED_HIGH = [re.compile(p) for p in _HIGH_PATTERNS]
_COMPILED_MEDIUM = [re.compile(p) for p in _MEDIUM_PATTERNS]


def detect_crisis(message: str) -> CrisisResult:
    """Detect crisis level in a user message.

    Normalizes text (strips diacritics, lowercases) and checks against
    keyword tiers from highest to lowest.
    """
    normalized = normalize_text(message)
    matched: list[str] = []

    # Check CRITICAL first
    for pattern in _COMPILED_CRITICAL:
        m = pattern.search(normalized)
        if m:
            matched.append(m.group())
    if matched:
        return CrisisResult(
            level=CrisisLevel.CRITICAL,
            matched_keywords=matched,
            recommended_action="immediate_crisis_response",
            crisis_contacts=CZECH_CRISIS_CONTACTS,
        )

    # Check HIGH
    for pattern in _COMPILED_HIGH:
        m = pattern.search(normalized)
        if m:
            matched.append(m.group())
    if matched:
        return CrisisResult(
            level=CrisisLevel.HIGH,
            matched_keywords=matched,
            recommended_action="crisis_response_with_contacts",
            crisis_contacts=CZECH_CRISIS_CONTACTS,
        )

    # Check MEDIUM
    for pattern in _COMPILED_MEDIUM:
        m = pattern.search(normalized)
        if m:
            matched.append(m.group())
    if matched:
        return CrisisResult(
            level=CrisisLevel.MEDIUM,
            matched_keywords=matched,
            recommended_action="append_crisis_resources",
            crisis_contacts=CZECH_CRISIS_CONTACTS[:4],
        )

    return CrisisResult(
        level=CrisisLevel.NONE,
        matched_keywords=[],
        recommended_action="proceed_normally",
        crisis_contacts=[],
    )


def get_crisis_response(result: CrisisResult) -> str:
    """Return a predefined crisis response. NO AI improvisation.

    These messages should be reviewed by a clinical advisor.
    """
    if result.level == CrisisLevel.CRITICAL:
        return (
            "Rozumím, že procházíš velmi těžkým obdobím. Tvůj život má hodnotu "
            "a zasloužíš si podporu.\n\n"
            "Prosím, zavolej na krizovou linku — jsou dostupní 24/7 a pomohou ti:\n"
            "📞 Krizová pomoc: 116 123\n"
            "📞 Linka bezpečí: 116 111\n"
            "📞 Záchranná služba: 155\n\n"
            "Nejsi na to sám/sama. Odborníci na těchto linkách ti pomohou."
        )

    if result.level == CrisisLevel.HIGH:
        return (
            "Slyším tě a beru to vážně. To, co popisuješ, vyžaduje odbornou pomoc.\n\n"
            "Prosím, obrať se na krizovou linku:\n"
            "📞 Krizová pomoc: 116 123 (24/7)\n"
            "📞 Národní linka pro odvykání: 800 350 000\n\n"
            "Nechci ti radit něco, co přesahuje moje možnosti jako AI nástroje. "
            "Na těchto linkách jsou lidé, kteří ti skutečně pomohou."
        )

    if result.level == CrisisLevel.MEDIUM:
        return (
            "\n\n---\n"
            "💡 Pokud cítíš silnou touhu po alkoholu nebo ti není dobře, "
            "můžeš zavolat na Národní linku pro odvykání: 800 350 000 (Po-Pá 10-18). "
            "Pro akutní krizi: 116 123 (24/7)."
        )

    return ""
