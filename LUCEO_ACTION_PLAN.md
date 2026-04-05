# LUCEO — Konsolidovaný akční plán
**Verze:** 1.0
**Datum:** 5. dubna 2026
**Status:** Aktivní — prioritizované kroky synthesizované z výzkumných reportů
**Zdroje:** LUCEO_MAIN_DOCUMENT_v1.md, luceo-deep-research.md, zprava-hluboky-vyzkum.md

---

## URGENTNÍ KONTEXT

### EU AI Act deadline: 2. srpna 2026
Full compliance pro high-risk AI systémy. Pokud Luceo zůstane jako wellness/informační app (aktuální positioning) → spadá do "limited risk" → pouze transparency obligations. **Jakékoliv klinické claims posunují do high-risk kategorie.**

### Monument/Tempest skandál jako příležitost
FTC pokuta $2,5M (duben 2024) za sdílení zdravotních dat s advertisery. Luceo má přirozený positioning: **privacy-first jako competitive moat, ne jen compliance checkbox.**

---

## FÁZE 0 — FOUNDATIONS (duben 2026, paralelně s maturitou)

### Priorita KRITICKÁ (blokátory dalších fází)

| # | Akce | Detail | Deadline | Status |
|---|---|---|---|---|
| 0.1 | **Kontakt klinického advisora** | Blokátor pro granty i pilot. Konkrétní cíle: AT ambulance Ostrava, Adiktologická klinika VFN Praha, CARG (Czech Addiction Research Group). Value prop: bezplatný advisory, acknowledgement v grantech, spoluautorství ve validační studii. | Do konce dubna | [ ] |
| 0.2 | **Legal scan s healthtech právníkem** | Jedno sezení, focus: AI Act + MDR positioning pro MVP. Investice ~500–1000 EUR. Zjistit: je wellness positioning udržitelný? Jaké termíny nesmíme používat? | Do konce dubna | [ ] |
| 0.3 | **Registrace domény luceo.app** | Základní krok pro brand. | Tento týden | [ ] |

### Priorita VYSOKÁ

| # | Akce | Detail | Deadline | Status |
|---|---|---|---|---|
| 0.4 | **Kontakt Jarda** | Zahájení spolupráce, sdílení vision documentu. | Tento týden | [ ] |
| 0.5 | **Vision & Scope dokument** | Zkrácená verze pro Jardu a Josefa — ne celý main document, ale 2-stránkový executive summary. | Do konce dubna | [ ] |
| 0.6 | **Legal entity rozhodnutí** | s.r.o. nebo a.s. nejpozději do léta 2026. Klíčová otázka: součást JPL Servis ekosystému, nebo samostatná entita? Pro TAČR grant a partnership agreements je právní entita podmínkou. | Do konce května | [ ] |

---

## FÁZE 1 — VALIDATION (květen–červen 2026, po maturitě)

### Pitch a financování

| # | Akce | Detail | Zdroj info |
|---|---|---|---|
| 1.1 | **Pitch Josefovi (JPL Servis, Praha)** | Nejde jen o seed capital — klíčová je jeho síť (pojišťovny, korporáti). CFA background = rozumí ROI argumentům. Framing: zdravotní náklady alkoholismu v ČR = miliardy CZK ročně. | deep-research |
| 1.2 | **VŠB-TUO research office kontakt** | I před nástupem na školu. FEI má zkušenosti s health IT. VŠB-TUO jako co-applicant v TAČR grantu. Toto je chybějící článek pro grantové financování. | deep-research |
| 1.3 | **TAČR konzultace** | První schůzka je zdarma (Innovation Office). Program SIGMA / Nováčci: až 15 mil. CZK. Podmínka: výzkumný partner (→ VŠB-TUO). | deep-research |

### Grantový přehled (konsolidovaný)

| Grant | Částka | Reálnost pro Luceo | Podmínky | Timing |
|---|---|---|---|---|
| **TAČR SIGMA / Nováčci** | Až 15 mil. CZK | VYSOKÁ | Výzkumný partner (VŠB-TUO) | Léto 2026 aplikace |
| **Krajské granty MSK** | Variabilní | STŘEDNÍ-VYSOKÁ | Startup z MSK regionu (Opava) = výhoda | Průběžně |
| **EU4Health** | Až €2 000 000 | NÍZKÁ pro MVP | Konsorciální aplikace s institucí, lead time 12–18 měsíců | Fáze 2–3 |
| **EIC Accelerator** | Až €2,5M grant | STŘEDNÍ | Potřebuje validační data z pilotu | 2027 |

### Klinická databáze

| # | Akce | Obsah |
|---|---|---|
| 1.4 | **Začít budovat klinickou databázi** | CBT techniky pro závislosti (česky), AUDIT/CAGE/DAST screening protokoly, Motivational interviewing scripty, Krizové kontakty ČR, WHO guidelines, Doporučené postupy Českého adiktologického institutu |
| 1.5 | **Pitch deck v1.0** | Pro granty a investory. Musí obsahovat: problém (epidemiologie), řešení (AI + RAG), tým, MVP scope, financní model, competitive moat (privacy-first vs. Monument). |

---

## FÁZE 2 — BUILD (léto–podzim 2026)

### MVP Development

| Komponenta | Popis | Priorita |
|---|---|---|
| **Onboarding screening** | AUDIT dotazník pro alkohol | P0 |
| **AI chat asistent** | Claude API + RAG přes klinickou databázi | P0 |
| **Sobriety tracker + craving log** | Denní tracking, streak, mood | P0 |
| **Crisis detection + kontakty** | Keyword + sentiment analýza PŘED LLM, krizové linky ČR | P0 |
| **Základní CBT techniky** | Strukturovaná cvičení | P1 |
| **GDPR-compliant auth + storage** | EU hosting, šifrování, explicitní souhlas | P0 |

### Architektonické požadavky od dne 1

Z výzkumných reportů vyplývají tyto non-negotiable požadavky:

1. **AI Act compliance architektura**
   - Transparency: uživatel musí vědět, že komunikuje s AI
   - Logging: audit trail všech AI interakcí
   - Human oversight mechanismus

2. **Privacy-first design**
   - Zero third-party tracking pixels (žádný Google Analytics, Meta Pixel)
   - Server-side only analytics bez PII
   - Data residency v EU — povinnost
   - Šifrování at-rest (AES-256) i in-transit (TLS)

3. **Crisis layer architektura**
   - Běží PŘED LLM odpovědí
   - Keyword + sentiment analýza
   - Předdefinovaný protokol při detekci krize — žádná AI improvizace
   - Fallback na krizové kontakty

4. **RAG pipeline**
   - Klinicky ověřená databáze jako zdroj kontextu
   - Minimalizace hallucination
   - Guardrails: žádné diagnózy, žádná konkrétní léková doporučení

### Pilot partner

| # | Akce | Detail |
|---|---|---|
| 2.1 | **AT ambulance Ostrava** | Preferovaná pro proximity. Alternativa: Praha. |
| 2.2 | **TAČR grant aplikace** | S VŠB-TUO jako výzkumným partnerem. |
| 2.3 | **GDPR compliance finalizace** | DPA template, ToS, disclaimer, privacy policy. |

---

## FÁZE 3 — SCALE (2027+)

### Dlouhodobá strategie (z výzkumu)

| Oblast | Strategie | Detail |
|---|---|---|
| **DiGA (Německo)** | Validovaná cesta k pojišťovnám | Vitadio (CZ) precedens. Vyžaduje: CE marking + klinická studie. Revenue: €400–900/patient/rok. |
| **VZP (ČR)** | Fond prevence | Softex cesta než plné hrazení. Vyžaduje klinická data z pilotu. VZP už financuje DeePsy (VUT Brno). |
| **Corporate wellness** | Employer benefits | Nevyžaduje regulatorní schválení. Firemní benefity (Benefit Plus, Cafeteria). Zvážit dříve než Fáze 3. |
| **Internacionalizace** | SK → DE (DiGA) → PL | DE přes DiGA model je nejvíce validovaný. |

### Klinická validace

- Pilotní RCT studie s AT ambulancí
- Primární outcome: snížení AUDIT skóre, počet abstinentních dnů
- Sekundární: NPS, retence, kvalita života
- Potřebné pro: DiGA aplikaci, VZP fond prevence, seriózní B2B partnerství

---

## FINANČNÍ RÁMEC

### MVP rozpočet (odhad)

| Položka | Odhad |
|---|---|
| Development (6 měsíců) | 300–800K CZK |
| Claude API (10K messages/měsíc) | 2–5K CZK/měsíc |
| Legal (GDPR, ToS, healthtech) | 50–150K CZK |
| **Celkem MVP** | **500K–1,5M CZK** |

### Revenue projekce rok 1

| Zdroj | Realistický | Ambiciózní |
|---|---|---|
| MAU po 12 měsících | 500–2 000 | 5 000–10 000 |
| B2C subscription | 0–40K CZK/měsíc | 100–200K CZK/měsíc |
| B2B (AT pilot) | 0 | 50–150K CZK/rok |
| Granty | 500K–2M CZK | 2–5M CZK |

---

## COMPETITIVE MOAT — SYNTHESIZOVANÉ ARGUMENTY

1. **Privacy-first** — Monument pokutován $2,5M za sdílení dat. Luceo: zero third-party tracking, EU data residency, GDPR by design.
2. **Lokalizace** — Žádná česky lokalizovaná klinicky orientovaná AI platforma neexistuje.
3. **Kulturní fit** — Česká/moravská mentalita ("nepůjdu k psychologovi") vyžaduje specifický přístup. Anonymita jako feature.
4. **AI safety** — Claude API (Anthropic) má nejsilnější safety focus. Crisis layer před LLM. Guardrails.
5. **Akademický partner** — VŠB-TUO pro TAČR granty = strukturální výhoda.

---

## OTEVŘENÉ OTÁZKY (k rozhodnutí PM)

- [ ] Legal entity — s.r.o. nebo a.s.? Součást JPL Servis nebo samostatně?
- [ ] Backend: Node.js nebo Python (FastAPI)?
- [ ] Mobile-first (React Native) nebo web-first v MVP?
- [ ] Freemium nebo subscription od začátku?
- [ ] Corporate wellness (Fáze 2 místo 3)?
- [ ] Josef Luks — investor, advisor, nebo jen kontakt?

---

*Tento dokument konsoliduje poznatky ze všech výzkumných reportů do jednoho akčního plánu.*
*Aktualizovat po každém splnění milestonu nebo novém rozhodnutí PM.*
