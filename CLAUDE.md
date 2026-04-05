# LUCEO — Projektový kontext

## O projektu
**Luceo** (latina: svítím/zářím) je AI-powered platforma pro podporu lidí bojujících se závislostí.
Primární zaměření MVP: **alkoholismus** v ČR. Globální ambice.

## Klíčové principy
- **Není to chatbot** — je to personalizovaný průvodce recovery
- **Není to náhrada terapeuta** — je to 24/7 podpora mezi sezeními
- **Wellness app positioning** — ne medical device (pro MVP fázi)
- **Privacy-first** — GDPR, EU hosting, zero third-party tracking
- Recovery jako světlo, ne trest. Bez stigmatu.

## Tým
- **Patrik** — PM/CEO, software developer, 19 let, VŠB-TUO Informatika
- **Jarda** — Business Manager
- **Josef Luks** — potenciální advisor/stakeholder (CFA, JPL Servis)
- **Clinical Advisor** — TBD (kritická mezera)
- **Legal Advisor** — TBD (kritická mezera)

## Technický stack (navrhovaný)
- **LLM:** Claude API (Anthropic) s RAG architekturou
- **RAG:** pgvector nebo Pinecone
- **Backend:** Node.js nebo Python (FastAPI) — TBD
- **DB:** PostgreSQL + pgvector
- **Auth:** Supabase nebo vlastní JWT (GDPR-compliant)
- **Frontend:** React Native (mobile-first)
- **Hosting:** EU region povinně

## AI architektura — guardrails
- Crisis detection layer běží PŘED LLM odpovědí
- Luceo nikdy nediagnostikuje ani nedoporučuje konkrétní léky
- Vždy odkáže na odborníka při přesahu kompetencí
- Disclaimer v každé session

## Regulační kontext
- **GDPR** — zdravotní data = Article 9, special category (KRITICKÁ)
- **EU MDR** — wellness positioning pro MVP (ne SaMD)
- **EU AI Act** — deadline 2. srpna 2026 pro high-risk AI systémy
- **Zákon 379/2005 Sb.** — ČR zákon o ochraně zdraví

## Fáze projektu
- **Fáze 0** (duben 2026): Foundations — dokumentace, legal scan, kontakty
- **Fáze 1** (květen–červen 2026): Validation — pitch, clinical advisor, granty
- **Fáze 2** (léto–podzim 2026): Build — MVP development, pilot
- **Fáze 3** (2027): Scale — klinická validace, B2B, internacionalizace

## Struktura dokumentů
| Soubor | Účel |
|---|---|
| `LUCEO_MAIN_DOCUMENT_v1.md` | **Primární zdroj pravdy** — vize, tým, problém, řešení, roadmapa |
| `LUCEO_DECISION_LOG.md` | Log všech klíčových rozhodnutí |
| `LUCEO_PERSONAS.md` | User persony (Karel, Tereza, Jana, MUDr. Novák) |
| `luceo-deep-research.md` | Hloubkový výzkum — DTx trh, konkurence, regulace, granty |
| `zprava-hluboky-vyzkum.md` | Technický výzkum — klinické postupy, architektura, validace |
| `LUCEO_ACTION_PLAN.md` | Konsolidovaný akční plán s konkrétními kroky |

## Jazyk
- Primární jazyk dokumentace: **čeština**
- Technické termíny: angličtina
- Kód a komentáře: angličtina
