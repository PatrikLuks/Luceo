# LUCEO — Main Project Document
**Version:** 1.0  
**Datum:** 5. dubna 2026  
**Status:** Ideová fáze — živý dokument  
**Tento dokument je primárním zdrojem pravdy pro projekt Luceo. Vše se řídí tímto dokumentem.**

---

## 1. IDENTITA PROJEKTU

### Název
**Luceo**  
Latina: *luceo* = svítím, zářím.  
Framing: Ne "přestávám pít." Ale "začínám svítit." Recovery jako světlo, ne trest.

### Vize
Vybudovat nejlepší AI-powered addiction support platformu na světě — začínající v ČR, s globální ambicí.  
Luceo bude první opravdové digitální řešení pro lidi bojující se závislostí, které kombinuje klinicky ověřené metody, moderní AI a hlubokou empatii.

### Mise
Zpřístupnit efektivní podporu při závislosti každému člověku — bez ohledu na stigma, dostupnost klinik, nebo finanční situaci.

### Positioning
- **Není to chatbot.** Je to personalizovaný průvodce recovery.
- **Není to náhrada terapeuta.** Je to 24/7 podpora mezi sezeními.
- **Není to detox app.** Je to dlouhodobý partner.

---

## 2. TÝM

| Role | Osoba | Background |
|---|---|---|
| **Project Manager / CEO** | Patrik | Software developer, 19 let, IT podnikatel, finance background přes JPL Servis, nastupující VŠB-TUO Informatika → Kvantová informatika |
| **Business Manager** | Jarda | Manažer, spolupracovník PM |
| **Potenciální stakeholder / advisor** | Josef Luks | CFA charterholder, zakladatel JPL Servis (wealth management Praha), rodinné propojení s PM |
| **Clinical Advisor** | TBD | AT lékař nebo adiktolog — klíčová mezera k zaplnění |
| **Legal Advisor** | TBD | Healthtech/medtech právník — klíčová mezera |

---

## 3. PROBLÉM

### Epidemiologie — ČR
- **1,3–1,7 mil.** dospělých s rizikovým pitím alkoholu
- **720–900 tis.** v kategorii škodlivého pití
- ČR trvale v **top 5 světa** v konzumaci alkoholu na hlavu
- AT ambulance jsou přetížené, kapacity nedostatečné
- **Stigma** je zásadní bariéra — lidé nepůjdou k lékaři, ale telefon mají vždy u sebe

### Mezera na trhu
- Česky lokalizované digitální řešení pro závislosti **prakticky neexistuje**
- Existující zahraniční apps (Monument, Tempest, Woebot) nejsou dostupné v češtině ani kulturně lokalizované
- Česká a moravská mentalita je specifická — "nepůjdu k psychologovi" je silnější než v USA

### Rozsah problému (ČR — kompletní obrázek)
| Typ závislosti | Odhadovaný počet rizikových osob |
|---|---|
| Alkohol (rizikové pití) | 1,3–1,7 mil. |
| Alkohol (škodlivé pití) | 720–900 tis. |
| Psychoaktivní léky | 720 tis.–1,2 mil. |
| Tabák (denní kuřáci) | 1,5–2,0 mil. |
| Hazard (rizikové) | 60–110 tis. |
| Digitální závislosti | 360–540 tis. |

---

## 4. ŘEŠENÍ — PRODUKT

### Core produkt: Co Luceo dělá

**AI asistent** postavený na Claude API (RAG architektura) s databází klinicky ověřených informací, který poskytuje:

1. **Personalizovaná podpora** — konverzace přizpůsobená uživatelově fázi recovery, triggerům a historii
2. **Tracking** — craving logy, sobriety streak, mood tracking, identifikace triggerů
3. **CBT-based intervence** — kognitivně-behaviorální techniky dostupné 24/7
4. **Crisis protocol** — detekce krizového stavu + eskalace na krizové linky a odborníky
5. **Edukace** — databáze informací o závislosti, recovery procesech, farmakoterapii
6. **Rodinný modul** — podpora blízkých osob

### MVP scope (Verze 1.0)
- [ ] Onboarding screening (AUDIT dotazník pro alkohol)
- [ ] AI chat asistent (Claude API + RAG)
- [ ] Sobriety tracker + craving log
- [ ] Crisis detection + krizové kontakty (Linka bezpečí, AT linky)
- [ ] Základní CBT techniky (structured exercises)
- [ ] GDPR-compliant auth + data storage

### Co MVP NEOBSAHUJE (vědomá rozhodnutí)
- Přímé propojení s EHR systémy (fáze 2)
- Telemedicína / video s terapeutem (fáze 2)
- Wearables integrace (fáze 3)
- Gamifikace (fáze 2)
- Rodinný modul (fáze 2)

### Primární zaměření
**Alkoholismus** jako launching vertikála. Důvody:
- Největší segment (epidemiologicky)
- Nejvíce klinických dat a standardizovaných nástrojů (AUDIT, CBT protokoly)
- Nejsilnější argument pro granty (veřejné zdraví)

---

## 5. TECHNICKÁ ARCHITEKTURA

### Stack (navrhovaný)

| Vrstva | Technologie | Poznámka |
|---|---|---|
| **LLM** | Claude API (Anthropic) | Core AI engine |
| **RAG** | pgvector (PostgreSQL) | Semantic search přes klinickou databázi |
| **Backend** | Python (FastAPI) | Rozhodnuto DEC-008 |
| **Databáze** | PostgreSQL + pgvector | User data + vector store |
| **Auth** | Vlastní JWT | GDPR-compliant, refresh tokens |
| **Frontend** | React Native (mobile-first) | iOS + Android |
| **Hosting** | EU region povinně | GDPR požadavek |

### AI architektura — klíčové principy

**RAG (Retrieval-Augmented Generation)**  
LLM nedostane jen prompt — dostane relevantní klinický kontext vytažený z databáze. Minimalizuje hallucination, zvyšuje přesnost.

**User state management**  
Kontext uživatele (fáze recovery, triggery, historie) musí přežít mezi sezeními. Není to one-shot chatbot.

**Crisis detection layer**  
Běží PŘED LLM odpovědí, ne po. Keyword + sentiment analýza. Při detekci krizového stavu → předdefinovaný protokol, ne AI improvizace.

**Guardrails**  
- Luceo nikdy nediagnostikuje
- Luceo nikdy nedoporučuje konkrétní léky
- Luceo vždy odkáže na odborníka při přesahu kompetencí
- Disclaimer v každé session: "Nejsem terapeut, jsem podpůrný nástroj"

### Klinická databáze — obsah
- CBT techniky pro závislosti (česky)
- AUDIT, CAGE, DAST screening protokoly
- Motivational interviewing scripty
- Krizové kontakty ČR (AT linky, krizová centra, Linka bezpečí)
- WHO guidelines pro závislosti
- Doporučené postupy Českého adiktologického institutu

---

## 6. REGULACE

### Klíčové regulační rámce

| Nařízení | Dopad na Luceo | Priorita |
|---|---|---|
| **GDPR (EU 2016/679)** | Zdravotní data = Article 9, special category. Privacy by design, šifrování, EU hosting, explicitní souhlas. | KRITICKÁ |
| **EU MDR (2017/745)** | Pokud app terapeuticky tvrdí → může být SaMD (Software as Medical Device) → CE marking. | VYSOKÁ |
| **EU AI Act** | AI pro zdravotní účely = high-risk. Nutný human oversight, risk management, vysvětlitelnost. | VYSOKÁ |
| **Zákon 379/2005 Sb.** | ČR zákon o ochraně zdraví před závislostmi. | STŘEDNÍ |

### Strategie pro MDR (jak se vyhnout CE markingu v MVP fázi)
Luceo MVP se pozicionuje jako **"wellness a informační platforma"**, nikoli jako medical device:
- Nesmí tvrdit, že *léčí* závislost
- Nesmí nahrazovat klinické rozhodnutí
- Terminologie: "podpora", "průvodce", "informace" — ne "terapie", "léčba", "diagnóza"

**Toto je vědomé rozhodnutí pro MVP. Fáze 2 může zahrnovat klinickou validaci a MDR proces.**

### Okamžité kroky v oblasti regulace
- [ ] Konzultace s healthtech právníkem (1 session = základ)
- [ ] GDPR posouzení a DPA template
- [ ] ToS a disclaimer drafts

---

## 7. BUSINESS MODEL

### Revenue streams (dle priority)

| Model | Potenciál | Fáze |
|---|---|---|
| **Granty** (EU4Health, TAČR, MZČR, krajské granty) | Reálný pro MVP financování | Fáze 0–1 |
| **B2B → AT ambulance pilot** | Nízký revenue, vysoká validace | Fáze 1 |
| **B2C subscription** | Střední — stigma snižuje konverzi | Fáze 2 |
| **B2B → Pojišťovny (VZP, ZP MV)** | Vysoký — mají motivaci snižovat náklady na léčbu | Fáze 2–3 |
| **B2G → Obce/kraje/MZČR** | Solidní — veřejné zdraví agenda | Fáze 2 |
| **Corporate wellness** | Zajímavý — firmy platí za zaměstnance | Fáze 3 |

### Go-to-market — první trakce
1. **Granty** → financování MVP (bez nutnosti okamžitého revenue)
2. **Jeden AT pilot partner** → klinická validace + reference + první uživatelé
3. **Rodiny** jako distribuční kanál → lidé se závislostí sami nehledají pomoc, ale jejich blízcí ano

### Konkurence

| Produkt | Trh | Slabina vůči Luceo |
|---|---|---|
| Monument | USA | Anglicky, kulturně nepřizpůsobený |
| Tempest | USA | Anglicky, drahý |
| Woebot | Globální | Obecná mental health, ne závislosti specificky |
| Sober Grid | Globální | Jen peer support, žádný AI |
| Reframe | USA | Gamifikace, mělký klinický základ |
| České alternativy | ČR | Jednoduché trackery, žádný AI |

**Závěr:** Mezera v češtině je reálná. Lokalizovaný klinicky solidní AI asistent neexistuje.

---

## 8. ROADMAP

### Fáze 0 — Foundations (duben 2026, paralelně s maturitou)
- [ ] Registrace domény luceo.app
- [ ] Kontakt Jarda — zahájení spolupráce
- [ ] Vision & Scope dokument (pro Jardu a Josefa)
- [ ] Základní legal scan (MDR riziko)

### Fáze 1 — Validation (květen–červen 2026, po maturitě)
- [ ] Pitch Josefovi v Praze (JPL Servis) — seed funding nebo advisory
- [ ] Najít clinical advisor (AT lékař nebo adiktolog, i dobrovolně)
- [ ] Definovat MVP scope natvrdo
- [ ] Začít budovat klinickou databázi (CBT, AUDIT, české zdroje)
- [ ] Pitch deck v1 pro granty
- [ ] Kontakt: TAČR, EU4Health, případně krajský úřad MSK

### Fáze 2 — Build (léto–podzim 2026)
- [ ] MVP development: Claude API + RAG + tracking + crisis protocol
- [ ] Pilot partner: jedna AT ambulance (Ostrava nebo Praha)
- [ ] První uživatelé, první feedback
- [ ] Grant aplikace (EU4Health nebo TAČR)
- [ ] GDPR compliance finalizace

### Fáze 3 — Scale (2027)
- [ ] Klinická validace (pilotní studie)
- [ ] B2B expanze (pojišťovny, korporátní wellness)
- [ ] Internacionalizace (SK jako první krok, pak DE, PL)
- [ ] MDR proces (pokud ambice pharmaceutical grade)

---

## 9. KPI — Jak měříme úspěch

### MVP KPI
- Počet aktivních uživatelů (DAU/MAU)
- Retention rate (day 7, day 30)
- Průměrná délka sobriety streak
- Crisis escalation rate (% uživatelů, kteří dostali crisis support)
- Uživatelská spokojenost (NPS)

### Klinické KPI (po pilotu s AT ambulancí)
- Adherence k programu
- Snížení počtu relapsů vs. kontrolní skupina
- Zlepšení AUDIT skóre
- Počet úspěšných krizových intervencí

---

## 10. RIZIKA

| Riziko | Dopad | Pravděpodobnost | Mitigace |
|---|---|---|---|
| EU MDR klasifikace jako medical device | Blokuje launch | Střední | Pozicionování jako wellness app; právník od začátku |
| AI hallucination v krizovém kontextu | Kritický | Vysoká | Crisis layer před LLM; guardrails; disclaimer |
| Absence klinického advisora | Ztráta důvěryhodnosti | Střední | Aktivní hledání od Fáze 1 |
| GDPR porušení | Právní, reputační | Nízká (pokud správně) | Privacy by design od začátku |
| Distribuce — jak dostat app k uživatelům | Stagnace growth | Vysoká | AT ambulance jako distribuční kanál; rodiny |
| Financování MVP | Blokuje build | Střední | Granty jako primární cesta |

---

## 11. OTEVŘENÉ OTÁZKY (k rozhodnutí)

- [ ] Legal entity — pod jakým subjektem Luceo vznikne?
- [ ] Josef Luks — jaká je jeho role? (Investor, advisor, nebo jen kontakt?)
- [ ] Mobile-first nebo web-first v MVP?
- [ ] Freemium nebo subscription od začátku?
- [ ] Název v App Store: "Luceo" nebo přidat podtitul pro SEO?

---

## 12. REFERENCE A ZDROJE

- ChatGPT Deep Research Report (Příloha A) — klinická a regulační reference
- Národní monitorovací centrum pro drogy a závislosti (NMS)
- WHO Guidelines pro závislosti (2024)
- EU MDR 2017/745
- EU AI Act (platný od 2024)
- GDPR (EU 2016/679)
- Zákon č. 379/2005 Sb. (ČR)
- Český adiktologický institut — doporučené postupy
- Konkurenční analýza: Monument, Tempest, Woebot, Sober Grid, Reframe

---

## METADATA DOKUMENTU

| Pole | Hodnota |
|---|---|
| Verze | 1.0 |
| Datum vytvoření | 5. dubna 2026 |
| Autor | Patrik (PM) + Claude (AI asistent) |
| Zakládající konverzace | Session 1, 5. dubna 2026 |
| Příští review | Po maturitě (po 13. dubna 2026) |
| Jazyk | Čeština (primární), angličtina (technické termíny) |

---

*Tento dokument je živý. Aktualizuje se s každým klíčovým rozhodnutím PM.*  
*Verze dokumentu se zvyšuje při každé zásadní změně.*  
*Veškeré AI nástroje pracující s projektem Luceo používají tento dokument jako primární kontext.*
