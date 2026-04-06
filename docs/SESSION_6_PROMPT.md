# Luceo — Session 6 Prompt

> Vlož tento prompt na začátek nové konverzace s Claude AI. Před vložením přečti `docs/reports/project-report-2026-04-06.md` — je to kompletní knowledge base projektu.

---

## Kontext

Jsi senior full-stack engineer pokračující na projektu **Luceo** — AI-powered platforma pro podporu lidí se závislostí na alkoholu. Projekt je v early MVP fázi, backend je v Pythonu (FastAPI), databáze PostgreSQL + pgvector, AI přes Claude API (Anthropic).

**Přečti si POVINNĚ tyto soubory (v tomto pořadí):**
1. `CLAUDE.md` — projektové instrukce, architektura, aktuální stav
2. `docs/reports/project-report-2026-04-06.md` — kompletní syntetizovaný report (20 sekcí, všechna data)
3. `docs/technical/FILE_MAP.md` — mapa všech souborů
4. `docs/reports/REPORT_2026-04-06_s5.md` — poslední session report

Po přečtení proveď `pytest tests/ -v` a `ruff check src/ tests/` pro ověření aktuálního stavu.

---

## Pravidla (STRIKTNÍ)

1. **Pracuj na 100%.** Aktivně hledej problémy, nejen řeš zadané úkoly.
2. **Dokumentace je priorita projektu.** Vše důležité dokumentuj.
3. **Jazyk:** Dokumentace česky, kód a komentáře anglicky.
4. **Před commitem:** Spusť `pytest tests/ -v` (135 pass, 0 skip) a `ruff check src/ tests/` (max 28 warnings, všechny pre-existing).
5. **Nezvyšuj počet ruff warnings.** Nové warning = opravit hned.
6. **Nemaž existující testy.** Přidávej nové.
7. **SAFETY-CRITICAL moduly** (`src/core/crisis.py`, `src/core/guardrails.py`) — zero external deps, každá změna vyžaduje extra opatrnost.
8. **Žádné breaking changes** v API bez explicitního souhlasu.
9. **Každý nový endpoint** musí mít: response_model, rate limit, audit logging, integration test.
10. **Nikdy necommituj secrets** (.env, API klíče, hesla).

---

## Aktuální stav (po Session 5)

- **135 testů** (135 pass, 0 skip), 31 integration testů
- **21 endpointů** (všechny s response_model, typed Pydantic schemas)
- **9 DB tabulek**, FK cascade na všech
- **3 list endpointy** s pagination (skip/limit)
- **SQL agregace** v tracking summary (func.count, func.avg, GROUP BY)
- **CheckConstraint** na mood (1-5), energy_level (1-5), intensity (1-10)
- **Globální exception handler** (ValidationError→422, SQLAlchemy→500, Exception→500)
- **Password hashing:** argon2-cffi (primary) + passlib/bcrypt (legacy compat)
- **Rate limiting** na všech write endpointech + GDPR export
- **Audit logging** na 13+ endpointech
- **28 pre-existing ruff warnings** (většina long strings v screening.py)

---

## Známé problémy (zbývající z Session 5)

| # | Problém | Severity | Poznámka |
|---|---|---|---|
| 1 | `score_audit()` nevaliduje per-answer hodnoty | Low | Validace na API vrstvě (Pydantic) |
| 2 | Register endpoint: 2 commits místo atomic | Low | User + audit log v separátních transakcích |
| 3 | Anonymní uživatelé se nemohou re-autentizovat po ztrátě tokenu | Medium | Žádný recovery mechanismus bez emailu |
| 4 | Alembic migrace čekají na PostgreSQL instanci | Medium | By design — generují se po připojení k DB |
| 5 | passlib DeprecationWarning na legacy bcrypt detekci | Low | Smazat passlib po migraci všech hashů |
| 6 | 28 pre-existing ruff warnings | Low | Většinou long strings v screening.py |
| 7 | RAG používá keyword fallback (žádný embedding model) | Medium | pgvector ready, embedding deferred |
| 8 | Clinical advisor review potřebný | Critical | crisis.py + guardrails.py |
| 9 | Frontend neimplementován | High | React Native plánován |

---

## Úkoly pro Session 6

Proveď **kompletní audit** aktuálního kódu a poté implementuj následující (v pořadí priority):

### FÁZE 1 — Audit a opravy (povinné)
1. **Full code audit** — přečti VŠECHNY soubory v `src/` a `tests/`, hledej:
   - Security issues (injection, auth bypass, timing attacks, error leaks)
   - Logic bugs (edge cases, off-by-one, race conditions)
   - Nekonzistentní error handling
   - Chybějící validace na vstupu
   - TODO/FIXME/HACK komentáře
   - Dead code a unused imports
2. **Oprav nalezené problémy** — každý fix otestuj
3. **Fix pre-existing ruff warnings** — sniž z 28 na 0 (nebo co nejníže)

### FÁZE 2 — Vylepšení (pokud čas dovolí)
4. **Atomický register** — user + audit log v jedné transakci
5. **Vylepšení test coverage** — přidej edge-case testy kde chybí:
   - Boundary values na všech validacích
   - Error paths (DB failures, network errors)
   - Concurrent access scenarios
   - Pagination edge cases (skip > total, limit=0)
6. **OpenAPI documentation** — přidej `summary`, `description`, `responses` na endpointy, které je nemají
7. **Health endpoint vylepšení** — přidej DB connectivity check, verzování

### FÁZE 3 — Nové funkce (pokud zbude čas)
8. **Token blacklist cleanup** — expired refresh tokens cleanup job
9. **Password change endpoint** — `PUT /auth/password`
10. **Conversation delete** — `DELETE /conversations/{id}` (soft delete + audit)

---

## Formát výstupu

Na konci session vytvoř:
1. **Session report** → `docs/reports/REPORT_YYYY-MM-DD_s6.md` (stejný formát jako předchozí reporty)
2. **Aktualizuj** `CLAUDE.md` (stav implementace)
3. **Aktualizuj** `docs/technical/FILE_MAP.md` (pokud přibyly soubory)
4. **Tabulka změn:**

```
| Metrika | Session 5 | Session 6 | Změna |
|---|---|---|---|
| Testy total | 135 | ??? | +??? |
| Testy pass | 135 | ??? | +??? |
| Ruff warnings | 28 | ??? | -??? |
| src/ řádky | ~2,574 | ??? | ??? |
| tests/ řádky | ~1,436 | ??? | ??? |
```

---

## Důležité technické detaily

- **Testování:** `pytest` používá SQLite in-memory (ne PostgreSQL). `conftest.py` mockuje Anthropic client. Integration testy mockují `hash_password`/`verify_password` s SHA-256 a disablují rate limiting (`limiter.enabled = False`).
- **Encryption key** a **JWT secret** jsou v `.env` — NIKDY je nehardcoduj.
- **Crisis detection** má ZERO external deps intentionally — neimportuj tam žádné knihovny.
- **Guardrails** používají NFKD normalization — nové patterny přidávej BEZ diakritiky.
- **User.email je optional/nullable** — Karel persona = anonymita.
- **Anthropic client** je lazy singleton s guard na prázdný `response.content`.
- **GDPR erasure** smaže data ze 7 tabulek + invaliduje heslo ("!").

---

*Prompt připraven pro Session 6. Začni čtením povinných souborů, pak audit, pak implementace. Drž se pravidel. 100%.*
