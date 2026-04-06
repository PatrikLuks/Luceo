# Luceo — Safety Systems Documentation

This document describes the multi-layer safety architecture. It is critical reading for the clinical advisor before production deployment.

## Overview

Luceo handles vulnerable users (people struggling with addiction). Safety is the #1 priority. The system uses multiple independent layers — if one fails, others catch it.

```
User message
    │
    ▼
┌─────────────────────────┐
│ Layer 1: Crisis Detection│  ← BEFORE LLM, no dependencies, <1ms
│ (src/core/crisis.py)     │
└────────┬────────────────┘
         │
    ├── CRITICAL/HIGH → Predefined response, NO LLM call
    │
    ▼
┌─────────────────────────┐
│ Layer 2: System Prompt   │  ← Instructions to Claude API
│ (src/core/prompts.py)    │
└────────┬────────────────┘
         │
    ▼ LLM response
┌─────────────────────────┐
│ Layer 3: Output Guardrails│ ← Post-LLM regex filter
│ (src/core/guardrails.py)  │
└─────────────────────────┘
```

## Layer 1: Crisis Detection (`src/core/crisis.py`)

### Design Principles
- **Zero dependencies** — no database, no API calls, no imports from services/models
- **Runs BEFORE the LLM** — if DB or API is down, crisis detection still works
- **Deterministic** — regex pattern matching, not ML. Output is auditable
- **Fast** — <1ms execution time
- **Clinical advisor reviewable** — keyword lists are human-readable

### Crisis Levels

| Level | Trigger Examples | Response |
|---|---|---|
| **CRITICAL** | "chci zemřít", "sebevražda", "kill myself" | Predefined message + all crisis contacts. NO LLM call. |
| **HIGH** | "chci si ublížit", "předávkovat se", "self-harm" | Predefined message + key contacts. NO LLM call. |
| **MEDIUM** | "relaps", "chci pít", "neschopnost dál" | LLM responds normally, crisis resources appended. |
| **NONE** | Normal conversation | Normal LLM response. |

### Diacritics Handling
Czech text is normalized (NFKD decomposition via `src/core/text_utils.py`, combining chars stripped) so that "chci zemřít" and "chci zemrit" both trigger detection. The normalization also strips zero-width characters to prevent bypass attempts.

### Crisis Contacts (`src/core/crisis_contacts.py`)
Hardcoded Czech crisis numbers:
- Linka bezpečí: 116 111 (24/7)
- Krizová pomoc: 116 123 (24/7)
- Národní linka pro odvykání: 800 350 000
- Podané ruce: 549 257 217
- Záchranná služba: 155
- Tísňová linka: 112

### Keyword Pattern Format
Patterns are Python regexes matching normalized (no-diacritics, lowercase) text:
```python
_CRITICAL_PATTERNS = [
    r"\bchci\s+zemrit\b",
    r"\bsebevrazd",
    r"\bwant\s+to\s+die\b",
    ...
]
```

### TODO for Clinical Advisor
- [ ] Review all keyword patterns for completeness and false positive rate
- [ ] Review all predefined crisis responses for clinical appropriateness
- [ ] Add patterns for drug-specific crisis (beyond alcohol)
- [ ] Add patterns for domestic violence context

## Layer 2: System Prompt (`src/core/prompts.py`)

The system prompt is built via `build_system_prompt()` using `string.Template.safe_substitute()` to prevent prompt injection through RAG context or user data.

The system prompt instructs Claude to:
1. Never diagnose ("máš závislost", "jsi alkoholik")
2. Never recommend specific medications or dosages
3. Immediately refer to emergency services for symptoms of withdrawal (tremors, hallucinations, seizures)
4. Use empathetic, non-stigmatizing language
5. Stay within provided RAG context
6. Respond in Czech unless user writes in English
7. Respect the disclaimer reminder interval
8. Use personalized user context (streak, mood, cravings, AUDIT)

The system prompt is a **constant in code** (not stored in DB) so that changes go through version control and code review.

## Layer 3: Output Guardrails (`src/core/guardrails.py`)

Post-LLM regex filter catches responses that slip past the system prompt:

### Diagnostic Language Patterns
- ICD-10 codes (F10.x-F19.x)
- "diagnostikuji", "vaše diagnóza", "trpíte"
- "máš diagnózu/poruchu/nemoc"
- "jsi alkoholik", "jsi závislý"

### Medication Patterns
- Specific medication names: naltrexon, acamprosat, disulfiram, antabus, campral
- Benzodiazepines: diazepam, lorazepam, alprazolam, xanax, lexaurin
- SSRIs: sertralin, fluoxetin, escitalopram, citalopram, paroxetin
- Dosage patterns: "X mg denně/ráno/večer"

### When Guardrail Triggers
The unsafe LLM response is replaced with:
> "Na toto se prosím zeptej svého lékaře. Mohu ti ale pomoci s technikami zvládání chutí, sledováním nálad a dalšími podpůrnými nástroji."

The triggering event is logged with the reason for audit trail.

## AI Act Compliance

- **AI Disclaimer** shown at conversation start: "Komunikuješ s AI asistentem Luceo..."
- **Disclaimer Reminder** shown every 10 messages
- **Audit trail**: every message stored with `crisis_level` field
- **AuditLog model**: logs all AI interactions, crisis detections, logins, data deletions

## Test Coverage

- `tests/test_crisis.py` — 32 tests covering all crisis levels, diacritics normalization, zero-width char bypass, edge cases
- `tests/test_guardrails.py` — 15 tests covering diagnostic and medication pattern detection, diacritics normalization, feminine forms
- `tests/test_security.py` — 19 tests covering AES-GCM, AAD, JWT, password hashing, prompt template safety
- `tests/test_auth.py` — 7 tests covering refresh token lifecycle
- `tests/test_rate_limit.py` — 3 tests covering rate limit key extraction
- `tests/test_middleware.py` — 7 tests covering security headers (CSP, HSTS, Permissions-Policy)
- `tests/test_screening.py` — 13 tests covering AUDIT scoring boundaries and Q9/Q10 validation
- `tests/test_chat_service.py` — 5 tests covering guardrail triggering, crisis levels, disclaimer interval

## Future Work
- ML-based crisis detection (complementing, not replacing, keyword matching)
- Sentiment analysis for mood tracking
- Multi-language crisis patterns (English, Slovak)
- Integration with Czech IZS (Integrovaný záchranný systém) protocols
