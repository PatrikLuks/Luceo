# Luceo — Report 5. 4. 2026

## Souhrn Session 1

### Implementované komponenty

| Oblast | Stav | Detail |
|--------|------|--------|
| **Refresh tokeny** | DONE | SHA-256 hash, 30d expiry, rotace při refresh |
| **Rate limiting** | DONE | slowapi (in-memory), JWT-aware key function |
| **Alembic migrace** | DONE | Async template, pgvector extension, 9 modelů |
| **Security headers** | DONE | CSP, HSTS (prod), Permissions-Policy |
| **Audit logging** | DONE | Napojeno na auth, chat, screening |
| **CORS fix** | DONE | Odstraněn double-https bug |
| **AUDIT Q9/Q10** | DONE | Validace set membership {0, 2, 4} |
| **GDPR erasure** | DONE | +audit_logs, +refresh_tokens, password="!" |
| **Anthropic singleton** | DONE | Lazy `_get_client()` pattern |
| **Unused code cleanup** | DONE | Odstraněny mrtvé importy a třídy |

### Kvantitativní přehled

| Metrika | Hodnota |
|---------|---------|
| Testy | **67/67 pass** (0 failures) |
| Endpointy | **21** (20 v routerech + /health) |
| Routery | **6** (auth, chat, screening, tracking, crisis, admin) |
| DB tabulky | **9** (vč. refresh_tokens) |
| Nové soubory | 7 (rate_limit.py, refresh_token.py, alembic/, 3 test files) |
| Upravené soubory | 24 |
| Lint (ruff) | 29 E501 — vše pre-existing Czech/EN strings, 1 UP042 |

### Bezpečnostní stav

- JWT access tokeny: **1h** (sníženo z 24h)
- Refresh tokeny: **30 dní**, SHA-256 hash uložen v DB
- Rate limity: login/register 5/min, refresh 10/min, chat 20/min, tracking 60/min
- GDPR erasure: kompletní — 7 tabulek + password invalidation
- Security headers: CSP `default-src 'none'`, HSTS 1 rok (prod), X-Frame-Options DENY
- Audit trail: všechny klíčové akce logované s hashed IP

### Konzistence (manažerská kontrola)

| Kontrola | Výsledek |
|----------|----------|
| Testy vs kód | OK — 67/67, všechny nové featury pokryté |
| Modely vs Alembic env.py | OK — 9/9 modelů importováno |
| Modely vs conftest.py | OK — 9/9 modelů importováno |
| ForeignKeys | OK — 7 FK, všechny ukazují na existující tabulky |
| CLAUDE.md vs kód | OK — počty endpointů, tabulek, testů sedí |
| Dokumentace API | OK — refresh/logout/429 zdokumentovány |
| .env.example | OK — nové proměnné přidány |

### Identifikované nefixované problémy (low priority)

1. **E501 lint warnings (29)** — České a anglické WHO AUDIT řetězce přesahují 100 znaků. Záměrné — čitelnost > formátování.
2. **UP042** — `CrisisLevel(str, enum.Enum)` → `StrEnum`. Low priority, crisis.py je safety-critical modul s nulovou závislostí.
3. **pgvector embedding** — Sloupec se nedefinuje v SQLite test DB. Záměrné — RAG testy vyžadují PostgreSQL.
4. **passlib DeprecationWarning** — `crypt` modul deprecated v Python 3.12, odstraněn v 3.13. Nutno migrovat na bcrypt přímo.

### Další kroky (doporučení)

1. **Frontend** — React Native (dosud neimplementováno)
2. **PostgreSQL připojení** — Spustit `alembic upgrade head` pro vytvoření tabulek
3. **Redis** — Přepnout rate limiting ze in-memory na Redis pro production
4. **Clinical advisor review** — crisis.py + guardrails.py vyžadují klinický review
5. **passlib → bcrypt** — Migrace před Python 3.13

---

*Report generován: 5. dubna 2026*
*Stav: Session 1 kompletní, backend MVP funkční*
