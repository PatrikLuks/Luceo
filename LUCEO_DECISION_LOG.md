# LUCEO — Decision Log
**Živý dokument. Každé klíčové rozhodnutí se zapisuje sem.**  
**Formát: Datum | Rozhodnutí | Proč | Kdo rozhodl**

---

## SESSION 0 — 5. dubna 2026

---

### DEC-001 | Název: Luceo
**Datum:** 5. dubna 2026  
**Rozhodnutí:** Název projektu je **Luceo** (latina: svítím/zářím).  
**Proč:**
- Globálně vyslovitelný bez překladu
- Žádná přímá asociace se závislostí — odstraňuje stigma
- Framing recovery jako světlo, ne jako problém
- Prémiový feel — stojí vedle velkých healthtech značek
- Funguje jako .app doména, App Store název, brand

**Zamítnuté alternativy:**
- *Sobrio* — silný kandidát, ale Luceo má silnější emocionální náboj
- *Jasno* — česká duše, ale globálně slabší
- *Auro* — příliš generické
- *Luceo* bylo původně zamítnuto kvůli podobnosti s "Luks" (Josef Luks / JPL Servis) — PM rozhodl pokračovat, protože projekt stojí samostatně

**Rozhodl:** Patrik (PM)

---

### DEC-002 | AI engine: Claude API (Anthropic)
**Datum:** 5. dubna 2026  
**Rozhodnutí:** Core LLM je **Claude API** od Anthropic.  
**Proč:**
- PM má přímé zkušenosti s Claude API (projekt pro JPL Servis)
- Claude je vnímán jako bezpečnější a více "careful" v citlivých kontextech oproti GPT-4
- Anthropic má silný focus na AI safety — kritické pro healthtech
- Technická znalost na straně PM = rychlejší development
- RAG architektura je dobře zdokumentovaná pro Claude

**Rozhodl:** Patrik (PM)

---

### DEC-003 | Primární vertikála: Alkoholismus
**Datum:** 5. dubna 2026  
**Rozhodnutí:** MVP se zaměřuje primárně na **alkoholismus**. Ostatní závislosti jsou fáze 2+.  
**Proč:**
- Největší segment v ČR (1,3–1,7 mil. rizikových osob)
- Nejlepší dostupnost klinických dat, standardizovaných nástrojů (AUDIT, CBT protokoly)
- Nejsilnější epidemiologický argument pro granty
- Kulturně nejviditelnější problém v ČR/Moravě — stigma je největší, mezera největší
- Focus beats breadth v MVP fázi

**Rozhodl:** Patrik (PM)

---

### DEC-004 | Positioning: Wellness app, ne medical device
**Datum:** 5. dubna 2026  
**Rozhodnutí:** Luceo MVP se pozicionuje jako **wellness a informační platforma**, nikoli jako medical device.  
**Proč:**
- EU MDR (2017/745) by vyžadoval CE marking, klinické validace, notifikovaný orgán → náklady desetitisíce EUR, měsíce zpoždění
- MVP nemůže čekat na regulační proces
- Wellness positioning je legálně udržitelný pokud app nediagnostikuje a neléčí
- Strategické rozhodnutí: launch rychle, validuj, pak případně jdi do MDR procesu

**Riziko:** Pokud app překročí wellness framing v komunikaci → regulační problém.  
**Mitigace:** Právník od začátku, přísná content policy.

**Rozhodl:** Patrik (PM) na základě analýzy regulačního prostředí

---

### DEC-005 | Go-to-market: Granty → AT pilot → scale
**Datum:** 5. dubna 2026  
**Rozhodnutí:** Primární cesta k financování MVP jsou **granty**, první trakce přes **AT ambulance pilot**.  
**Proč:**
- B2C subscription selže bez brand awareness a klinické důvěryhodnosti
- Granty nevyžadují okamžitý produkt — stačí silný pitch
- AT ambulance jako pilot = klinická validace + reference + distribuce zároveň
- Rodiny jako sekundární distribuční kanál (lidé se závislostí sami nehledají pomoc)

**Rozhodl:** Patrik (PM)

---

### DEC-006 | Zakládající tým: Patrik (PM) + Jarda (business) + Josef (potenciální)
**Datum:** 5. dubna 2026  
**Rozhodnutí:** Projekt startuje s PM Patrikem, business managerem Jardou. Josef Luks je identifikován jako potenciální stakeholder/advisor — role zatím nepotvrzena.  
**Kritická mezera:** Clinical advisor a legal advisor jsou TBD — musí být vyřešeno ve Fázi 1.

**Rozhodl:** Patrik (PM)

---

### DEC-007 | Tento chat = Session 0, zakládající dokument
**Datum:** 5. dubna 2026  
**Rozhodnutí:** Konverzace ze 5. dubna 2026 (Claude.ai) je oficiálně **Session 0** projektu Luceo — zakládající dokument.  
**Proč:** Všechna klíčová rozhodnutí (název, vertikála, positioning, tým, architektura) padla v této session. Je důležité mít dohledatelný reasoning.

**Rozhodl:** Patrik (PM)

---

## ŠABLONA PRO BUDOUCÍ ROZHODNUTÍ

```
### DEC-XXX | [Název rozhodnutí]
**Datum:** DD. měsíce YYYY  
**Rozhodnutí:** [Co bylo rozhodnuto]  
**Proč:** [Reasoning]  
**Zamítnuté alternativy:** [Co bylo zvažováno]  
**Riziko:** [Pokud existuje]  
**Rozhodl:** [Kdo]
```

---

*Každé rozhodnutí s dopadem na produkt, tým, business model nebo regulaci se zapisuje sem.*  
*Tento log je interní dokument — není určen pro externí prezentace.*
