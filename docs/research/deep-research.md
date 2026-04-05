# LUCEO — Hloubkový výzkumný report
**Datum:** 5. dubna 2026  
**Zpracoval:** Claude (Anthropic) na základě live web research  
**Status:** Strategický podkladový dokument — interní

---

## EXECUTIVE SUMMARY

Projekt Luceo vstupuje na trh v ideálním timing window. Globální DTx trh poroste o 20–27 % ročně a u addictionového segmentu je tento růst strukturálně podpořen regulačními tlaky EU na digitální zdraví. Česká mezera (nulové lokalizované řešení) je reálná a potvrzená. Existují tři kritické nálezy, které hlavní dokument podceňuje: (1) Monument — největší přímý zahraniční kompetitur — byl v 2024 pokutován $2,5M za sdílení zdravotních dat s advertisery, což Luceu dává obrovský positioning argument pro privacy-first přístup; (2) německý DiGA model je validovaná cesta k pojišťovnám pro expanzi do DE a česká firma Vitadio tam již DiGA schválení získala — precedens existuje; (3) EU AI Act deadlina pro health AI je **2. srpna 2026**, tedy 4 měsíce od teď — MVP musí být architektonicky compliance-ready od prvního dne. Financování přes granty je reálné, ale podmínky TAČR vyžadují výzkumného partnera — VŠB-TUO je přirozený kandidát.

---

## 1. TRŽNÍ KONTEXT

### 1.1 Globální DTx trh 2026

Globální trh digitálních terapeutik (DTx) dosáhne v roce 2026 odhadovaně **$10–14 miliard**, přičemž různé analytické domy uvádějí odlišné metodologie (zahrnování wellness vs. pouze prescription DTx). CAGR na horizontu 2026–2034 se konzistentně pohybuje mezi **19–27 %**. Software-based řešení (vs. hardware) tvoří přes 89 % tržního podílu.

Klíčová segmentace podle terapeutické oblasti:
- **Diabetes:** ~40 % trhu — nejlépe reimbursovatelný segment
- **Mental health + addiction:** druhý největší — cca 25 % trhu, nejrychleji rostoucí z hlediska nových aplikací
- **Kardiovaskulár:** třetí segment, podporovaný specifickými EU4Health granty

**Relevance pro Luceo:** Addiction DTx je etablovaný segment s FDA-schválenými precedenty (reSET-O pro opioidní závislost). Mental health aplikace tvoří POLOVINU všech schválených německých DiGA. Trh je ověřený — otázka je pouze lokalizace.

### 1.2 Specifika addiction DTx segmentu

Reset-O (první schválená digitální terapie na světě) a A-CHESS jsou dokumentovanými precedenty. V Německu jsou mezi 68 schválenými DiGA zastoupeny aplikace pro závislost na alkoholu i tabáku — psychology DiGA obecně tvoří přibližně 50 % celého DiGA registru.

**Český kontext:** ČR v top 5 světa v konzumaci alkoholu na hlavu, 1,3–1,7 mil. lidí s rizikovým pitím — ale digitální řešení v češtině prakticky neexistuje. Mezera je prokazatelná.

---

## 2. KONKURENČNÍ ANALÝZA — AKTUALIZACE

### 2.1 Monument (USA) — hlavní benchmark

**Co to je:** Online MAT (medication-assisted treatment) platforma pro alkohol. Spolupracuje s employers, akceptuje velké pojišťovny (United, Cigna, Aetna). V roce 2022 akvizicí pohltila Tempest.

**Klíčová čísla:**
- Registrovaní uživatelé: **100 000+** (do 2023)
- Seed funding: $7,5M (2019), celkem přes $20M
- V roce 2025 rozšířil nabídku na primary care + broader mental health

**Kritická slabina — PŘÍLEŽITOST PRO LUCEO:**

V dubnu 2024 byl Monument **pokutován $2,5M ze strany FTC** za porušení Opioid Addiction Recovery Fraud Prevention Act. Důvod: sdílení citlivých zdravotních dat uživatelů (jméno, datum narození, email, zdravotní informace) s Google, Facebook a Pinterest přes tracking pixels — bez souhlasu a od roku 2020. Tempest dělal totéž od roku 2017.

**Strategický závěr:** Monument je definovaný skandálem s daty. Luceo s privacy-by-design architekturou a EU-GDPR compliance má přirozený positioning: *"Na rozdíl od amerických platforem, vaše data nevidí nikdo jiný."* To je silný argument zejména pro ČR, kde obecná důvěra k platformám je nízká.

### 2.2 Ostatní kompetitoři

| Produkt | Update 2026 | Slabina |
|---|---|---|
| Monument/Tempest | Pivot na broader healthcare, US-only | Data skandál, kulturně nepřizpůsobený |
| Woebot | General mental health, ne addiction-specific | Žádný clinical track record pro závislosti |
| Reframe | USA, gamifikace | Mělký klinický základ, vysoká churn rate |
| Sober Grid | Jen peer support | Žádný AI, žádná klinická intervence |
| České trackery | Jednoduché sobriety apps | Žádný AI, žádná klinická základna |

**Skutečný trh v ČR:** Prázdný. Neexistuje žádná česky lokalizovaná klinicky orientovaná platforma pro závislosti. Mezera potvrzena.

---

## 3. REGULAČNÍ LANDSCAPE — KRITICKÉ AKTUALIZACE

### 3.1 EU AI Act — URGENTNÍ

Toto je nejdůležitější regulační update, který hlavní dokument nepostihuje v plné naléhavosti.

**Timeline:**
- **2. února 2025:** Zákaz "unacceptable risk" AI systémů (platí)
- **2. srpna 2025:** GPAI model obligations, governance infrastruktura (platí)
- **2. srpna 2026 — KRITICKÁ DEADLINA:** Full compliance pro **high-risk AI systémy**
- **2. srpna 2027:** Legacy systémy integrované do regulovaných produktů

**Klíčová otázka pro Luceo:** Spadá AI asistent do "high-risk" kategorie?

**Analýza:**

Pokud Luceo **zůstane jako wellness/informační app** (positioning z hlavního dokumentu) → pravděpodobně **"limited risk"** → pouze transparency obligations (uživatel musí vědět, že komunikuje s AI). Toto je zvládnutelné.

Pokud Luceo **dělá jakékoli klinické claims** nebo je klasifikováno jako SaMD → **high-risk** → nutné: risk management systém, technická dokumentace, data governance, human oversight, post-market monitoring, CE marking. Deadlina **2. srpen 2026**.

**Praktický důsledek pro MVP timing:** Fáze 2 (build, léto–podzim 2026) přímo koliduje s AI Act deadlinou. Pokud MVP nebude k dispozici před 2. srpnem 2026, a Luceo se rozhodne pro klinické claims, potřebuje full AI Act compliance od prvního dne po launchi. Právník specializující se na AI + healthtech je kritický, ne volitelný.

**Doporučení:** Wellness positioning pro MVP je správná strategie — nejen kvůli MDR, ale i kvůli AI Act. Jakékoliv rozšíření na klinické claims v fázi 2 vyžaduje předchozí compliance audit.

### 3.2 EU MDR — Wellness Positioning Potvrzena

Pozicionování jako wellness app (ne SaMD) pro MVP je správné. Terminologie "podpora", "průvodce", "informace" místo "léčba", "terapie", "diagnóza" je klíčová. Toto potvrzuje strategii z hlavního dokumentu.

### 3.3 GDPR — Monument jako odstrašující příklad

Monument/Tempest scandal je přímou demonstrací, co se stane bez privacy-by-design. Pro Luceo:
- Žádné third-party tracking pixels (Google Analytics, Meta Pixel) na platformě s zdravotními daty — nikdy
- Server-side only analytics bez PII
- Explicitní souhlas před každou formou sdílení
- Data residency v EU — povinnost, ne volba

---

## 4. GRANTOVÉ FINANCOVÁNÍ — REALISTICKÁ ANALÝZA

### 4.1 EU4Health 2026

**EU4H-2026-SANTE-PJ-05** — "Lifelong prevention for a healthy life with focus on cardiovascular diseases" — zahrnuje **rizikové faktory včetně alkoholu a tabáku**. Award range: **až €2 000 000**.

**Problém:** EU4Health granty jsou primárně určeny pro "national authorities, health organisations and other bodies" — ne startupy. Jako startup bez track rekordu je přímá aplikace velmi obtížná. Reálná cesta: **konsorciální aplikace s institucí** (VŠB-TUO nebo adiktologické centrum jako lead applicant, Luceo jako technologický partner).

**EU4H-2026-SANTE-PJ-04** — AI + health data. Zaměřeno na kardiovaskulár, ale princip AI + health data je přenositelný.

**Praktický závěr:** EU4Health pro MVP fázi je příliš pomalý a komplexní (lead time 12–18 měsíců na výsledek grantu, plus konsorciální setup). Relevantní pro Fázi 2–3 s institucí jako partnerem.

### 4.2 TAČR — Reálnější cesta pro ČR

TAČR pro 2026 připravuje programy zaměřené na průmyslový výzkum a VaV:

**Program SIGMA / Nováčci:**
- Až **15 mil. CZK** pro "nováčky" (nové subjekty)
- Až 25 mil. CZK pro "Technologičtí lídři"
- Financuje: mzdy zaměstnanců, náklady na stroje a služby

**Kritická podmínka TAČR:** TAČR explicitně podporuje **spolupráci podniků s výzkumnými organizacemi**. Pro startup bez výzkumné historie je přímá aplikace problematická. Potřebuješ výzkumného partnera.

**Přirozený partner: VŠB-TUO**

Toto je specifická příležitost, která v hlavním dokumentu chybí. Nastupuješ na VŠB-TUO (Informatika). VŠB-TUO jako výzkumná instituce může být **co-applicant nebo lead applicant** v TAČR grantu, zatímco Luceo je průmyslovým partnerem. Tento setup je přesně to, pro co TAČR existuje. Kontakt na VŠB-TUO research department by měl být na roadmapě — ne po maturitě, ale před.

**EIC Accelerator (Horizon Europe):**
- Až **€2,5M grant** nebo €0,5–15M investice
- "Seal of Excellence" → alternativní financování přes NPO i při neúspěchu v EIC
- TAČR je národní poskytovatel pro Seal of Excellence projekty
- Fáze: Specifické výzvy pro "digitální a zdravotnické technologie"

**Timeline realistická pro Luceo:**
1. **Nyní → červen 2026:** Navázat kontakt s VŠB-TUO výzkumným oddělením
2. **Léto 2026:** Konsorciální přihláška TAČR SIGMA (Nováčci podprogram)
3. **2027:** EIC Accelerator po prvních validačních datech z pilotu

### 4.3 Krajské granty — MSK

Moravskoslezský kraj má specifické programy pro startup podpůrnou infrastrukturu. Jako startup z MSK (Opava) máš přirozenou výhodu u krajských programů, které jsou zaměřené na rozvoj regionu. Toto je podhodnocená příležitost s nižší konkurencí než národní/EU granty.

---

## 5. NĚMECKÝ DiGA MODEL — STRATEGICKÁ PŘÍLEŽITOST

Toto je pravděpodobně nejdůležitější nález pro dlouhodobou strategii Luceo.

### 5.1 Co je DiGA

Německý systém "Digitale Gesundheitsanwendungen" (DiGA) = apps on prescription hrazené statutoárním zdravotním pojištěním (cca 73 mil. lidí). Schvalovací orgán: BfArM (federální ústav pro léčiva). Podmínky:
- CE marking jako medical device (MDR class I nebo IIa)
- Prokázaný "positive healthcare effect" (klinická studie)
- Data protection (BSI TR-03161 od 2025)

**Čísla ke konci 2024:**
- 68 schválených DiGA (z toho ~44 permanentních)
- Přes **1 milion kumulativních preskripci**
- Kumulativní výdaje pojišťoven: **€234 milionů**
- Psychology/mental health = ~50 % všech DiGA — včetně závislostí (alkohol, tabák)

### 5.2 Precedens: česká firma získala DiGA schválení

**Vitadio (CZ)** — česká společnost pro management diabetu — získala DiGA schválení a je v německém registru. To znamená: **cesta z ČR do DiGA existuje a je prošlapaná.** Toto je klíčový precedens pro Luceo's Phase 3 internacionalizaci.

### 5.3 DiGA jako Luceo roadmap

```
MVP (2026) → wellness app, ČR pilot, žádné clinical claims
         ↓
Fáze 2 (2027) → pilot studie s AT ambulancí (klinická data)
         ↓
MDR CE Class I/IIa (2027–2028) → nutné pro DiGA
         ↓
DiGA aplikace BfArM (2028) → německý trh, 73M pojištěnců
         ↓
Replikace modelu: AT → PL → FR/IT
```

DiGA model = validovaná cesta k B2B pojišťovnám bez nutnosti budovat přímé insurance relationships ve více zemích.

### 5.4 Lekce z DiGA pro Luceo

- **Privacy-first je podmínka, ne feature:** BSI bezpečnostní požadavky jsou od 2025 ostré
- **Clinical evidence je nutná pro permanentní schválení:** Pilotní studie s AT ambulancí = investice do DiGA cesty
- **Pricing**: Průměrný DiGA stojí pojišťovnu €400–900/patient/rok — signifikantní revenue potenciál
- **Malé firmy mají výzvy s profitabilitou DiGA cesty** — vyžaduje scale nebo multiple DiGAs

---

## 6. VZP / ČESKÁ POJIŠŤOVNOVÁ CESTA

VZP provozuje program duševního zdraví s příspěvkem z **fondu prevence** — konkrétně podporuje psychoterapii. Platforma používá anonymizovanou app DeePsy (VUT Brno + Masarykova univerzita) pro monitoring terapie.

**Co z toho plyne pro Luceo:**
- VZP má aktivní zájem o digitální mental health nástroje
- Fond prevence existuje a financuje digitálně podporované programy
- Akademický partner (VUT/MU) je v jejich modelu přítomen — VŠB-TUO je analogický partner pro Luceo

**Realistická cesta k VZP:**
1. Pilot s AT ambulancí → klinická data
2. Présentace dat na VZP (oddělení prevence, ne klinická péče)
3. Příspěvek z fondu prevence = softer cesta než plné hrazení
4. Plné hrazení vyžaduje legislativní framework (v ČR neexistuje DiGA ekvivalent — mezera, ale i příležitost)

**Důležité:** ČR nemá DiGA ekvivalent. Pokud někdo (startup, VŠB-TUO nebo MZ ČR) prosadí takový framework, Luceo se může dostat do pozice first-mover. Toto je politický advocacy argument do Fáze 3.

---

## 7. KRITICKÉ MEZERY V HLAVNÍM DOKUMENTU

Toto jsou věci, které hlavní dokument buď podceňuje nebo zcela chybí:

### 7.1 Privacy jako competitive moat, ne jen compliance

Monument/Tempest scandal jasně ukazuje, že privacy není jen tick-box. Je to **business differentiator** v addiction space, kde je stigma klíčový faktor a uživatelé jsou extrémně citliví. Luceo by měl aktivně komunikovat privacy-first přístup jako součást produktového positioning — ne jen v ToS.

**Konkrétní opatření:**
- Zero third-party tracking na platformě s health daty
- Open-source audit trail dat (co se ukládá, jak dlouho, kdo vidí)
- "Privacy report" jako feature pro uživatele
- GDPR compliance jako marketing argument, ne jen legal requirement

### 7.2 VŠB-TUO jako grantový partner je chybějící článek

Nastupuješ na VŠB-TUO. TAČR vyžaduje výzkumného partnera. VŠB-TUO FEI (Fakulta elektrotechniky a informatiky) má zkušenosti s health IT projekty. Toto není náhoda — je to přirozený fit. Kontakt by měl proběhnout na začátku akademického roku (září 2026), nebo ještě lépe přes přijímací kancelář nebo vedení fakulty před nástupem.

### 7.3 B2B s employer-centric modelem

Monument's primary go-to-market v USA je **employer benefits** — firmy platí za zaměstnance, pokryto skrze skupinové pojištění. V ČR existuje analogie: firemní benefity (Benefit Plus, Cafeteria systémy). Alkoholismus stojí českou ekonomiku miliardy ročně v produktivitě. HR directoři jsou potenciální kupci, ne klinická sféra.

Toto není v roadmapě Luceo zmíněno. Corporate wellness (Fáze 3) by mohl být rychlejší cesta k revenue než pojišťovny — protože nevyžaduje regulatorní schválení, jen prodejní cyklus.

### 7.4 Clinical advisor strategy je nedostatečně konkrétní

"Aktivní hledání od Fáze 1" není strategie. Konkrétní cesty:
- **Adiktologická klinika VFN Praha** (prof. Karel Nešpor nebo jeho nástupci) — publikují, jsou otevření spolupráci
- **CARG (Czech Addiction Research Group)** — akademická síť
- **AT ambulance Ostrava** — regionální, dostupnější, přirozený pilot partner
- **Linkedin/ResearchGate outreach** s konkrétním value proposition: "bezplatný advisory role, acknowledgement v grantech, možnost spoluautorství ve validační studii"

Bez klinického advisora žádný seriózní grant nezískáš. Toto je blokátor Fáze 1.

### 7.5 Legal entity timing

Hlavní dokument má toto jako otevřenou otázku. Je to fakticky urgentní: pro podání grantu (TAČR) nebo partnership agreement s AT ambulancí potřebuješ existující legal entity. **Doporučení: s.r.o. nebo a.s. nejpozději do léta 2026**, ideálně před.

Zvažuj: Je Luceo součást JPL Servis ekosystému, nebo samostatná entita? Toto má daňové a strukturální implikace.

---

## 8. FINANČNÍ MODEL — REALISTICKÁ ČÍSLA

Toto je grounding exercise. Monument v USA potřeboval $7,5M seed k dosažení 100K uživatelů za ~3 roky v trhu 330M lidí. ČR má 10M lidí.

**Hrubé odhady pro ČR kontex:**
| Metrika | Realistický rok 1 | Ambiciózní rok 1 |
|---|---|---|
| MAU po 12 měsících | 500–2 000 | 5 000–10 000 |
| B2C subscription revenue | 0–40K CZK/měsíc | 100–200K CZK/měsíc |
| B2B (AT ambulance pilot) | 0 | 50–150K CZK/rok |
| Grant revenue | 500K–2M CZK | 2–5M CZK |

**Realistické MVP budget:**
- Development (6 měsíců PM práce + freelanceri): 300–800K CZK
- Claude API náklady (odhad 10K messages/měsíc): 2–5K CZK/měsíc
- Legal (GDPR, ToS, healthtech konzultace): 50–150K CZK
- **Celkem MVP:** 500K–1,5M CZK

Toto je částka, kterou granty nebo seed investment může pokrýt. VŠB-TUO TAČR grant by pokryl výzkumnou složku, Josef Luks mohl pokrýt startup náklady jako seed/loan.

---

## 9. AKTUALIZOVANÁ PRIORITNÍ ROADMAP

Na základě výzkumu navrhuji přehodnocení pořadí priorit Fáze 0:

### Okamžité (duben 2026, před maturitou)
1. **Kontakt na klinického advisora** — blokátor všeho dalšího. Konkrétně: AT ambulance Ostrava nebo VFN Praha. Email s konkrétním value prop.
2. **Legal scan s healthtech právníkem** — jedno sezení, focus na AI Act + MDR positioning pro MVP. Toto je investice $500–1000, která může ušetřit miliony v přepracování.
3. **Registrace domény** + základní privacy-first brand positioning dokumentu

### Post-maturita (květen–červen 2026)
4. **Josef Luks pitch** — ale s revidovaným framing: nejde jen o seed capital, ale o jeho síť (pojišťovny, korporáti). CFA background = rozumí ROI argumentům přes zdravotní náklady.
5. **VŠB-TUO research office kontakt** — i před nástupem. FEI má experience s health IT projekty.
6. **TAČR konzultace** — první schůzka je zdarma (Innovation Office). Zjistit přesné podmínky pro Nováčci program.

### Léto 2026 (paralelně s buildem)
7. **MVP development** — ale s AI Act compliance architekturou od dne 1
8. **Pilot partner** — jedna AT ambulance (Ostrava preferovaná pro proximity)
9. **TAČR grant aplikace** — s VŠB-TUO jako výzkumným partnerem

---

## 10. SYNTÉZA — CO VÝZKUM MĚNÍ NA STRATEGII

| Oblast | Původní přístup | Doporučená úprava |
|---|---|---|
| Privacy | Compliance checkbox | **Core competitive moat** — aktivně komunikovat vs. Monument scandal |
| Granty | EU4Health + TAČR obecně | TAČR Nováčci s VŠB-TUO partnerem je priorita; EU4Health až Fáze 2 |
| AI Act | Zmíněno, bez urgence | **Deadline 2. srpna 2026** — architektura od dne 1 musí být compliance-ready |
| Internacionalizace | SK, pak DE, PL | **DE přes DiGA** je validovaný model; Vitadio precedens z ČR |
| Clinical advisor | "Aktivní hledání od Fáze 1" | Blokátor — musí proběhnout **před** všemi ostatními kroky |
| Employer channel | Fáze 3 "corporate wellness" | **Zvážit dřív** — nevyžaduje regulatorní schválení, rychlejší revenue |
| VZP | Obecný záměr | Fond prevence je reálnější cesta než plné hrazení; vyžaduje klinická data |

---

## ZÁVĚR

Luceo je projekt se solidními základy a reálnou tržní mezerou. Timing je dobrý — DTx trh roste, Monument je morálně kompromitovaný, česká lokalizace chybí. Největší rizika nejsou tržní, jsou operační: absence klinického advisora, absence legal clarity před buildem, a AI Act deadline, která přijde dřív než si projekt uvědomuje. Priorita #1 před vším ostatním je klinický advisor — bez něj je každý grant a každý pilot rozhovor slabší.

---

*Report zpracován na základě live web research k 5. dubnu 2026.*  
*Zdroje: EU AI Act official documentation, DiGA research (PubMed, BfArM), Monument/FTC case records, DTx market reports (Fortune Business Insights, ResearchNester), EU4Health programme documentation, TAČR programme overview, VZP mental health programme.*
