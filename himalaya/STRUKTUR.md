# Klubbkveld Voss - plan

Rammer: **ca. én time**, **Simen alene** (Dagfinn er ikke med), og decket fra
Loen skal **ikke gjenbrukes rett fram**. Det er kildebiblioteket; Voss får sitt
eget deck der vi plukker inn det som er nyttig.

- Loen-decket, konvertert og komplett: `presentasjon.qmd` (50 slides)
- Voss-decket: `voss.qmd`

## Hovedgrepet

pgpilot er ikke et kapittel på slutten. Det er verktøyet turen vises med.

Tolv av slidene fra Loen er Google Earth- og XContest-bilder med tracket tegnet
oppå. Det er døde bilder av nøyaktig det pgpilot gjør levende. Bytter du dem mot
ekte replay, har du vist appen i tjue minutter før du sier at den finnes, og da
lander den eksplisitte bolken som en avsløring i stedet for et pitch.

Siden Dagfinn ikke er med, faller dobbeltnummeret på slide 36 og 38 bort. Det er
greit: alene er det lettere å holde én tråd gjennom timen.

## Kjøreplan (50 min + 10 min spørsmål)

| # | Bolk | Min | Henter fra | pgpilot |
|---|---|-----|------------|---------|
| 1 | Krok: bare fly | 3 | video 48 eller 09 | - |
| 2 | Hvor og hvorfor Bir | 5 | 2, 3, 4, 5, 47 | Kartet, ikke to screenshots |
| 3 | Fronten: det milde møtet | 7 | 8, 10, 17 | **Replay 2024 dag 1 starter** |
| 4 | Volbiv over ryggen | 10 | 11, 15, 18, 20, 22, 24, 27 | Samme replay, scrubbet |
| 5 | Flyging uten infrastruktur | 10 | 21, 28, 29 + notatene | Broen til appen |
| 6 | pgpilot: hva og hvorfor | 10 | - | **Live demo, 2026-turen** |
| 7 | Bli med i 2026 | 5 | 46, 49, 50 | - |

### 1. Krok (3 min)

Video i fullskjerm, uten tekst, uten deg. La den gå. Så tittel.

### 2. Hvor og hvorfor (5 min)

Bir og Billing: startplass på 2400 meter, fjellkjede som bare fortsetter bakover,
sesong i oktober og november. Slide 47 sin "Why Bir?" er allerede argumentet.

### 3. Fronten (7 min)

Det milde møtet: soaring på frontryggen, terrasser under, termikk som funker.
Her starter replayen av **2024 dag 1**, som er nettopp den flighten.

### 4. Volbiv over ryggen (10 min)

Dag 1 fortsetter innover og lander ved Saurkundi. Teltplassen. Dag 2 tilbake.
Scrub replayen mens du snakker og stopp der historien er. Høydeprofilen er
poenget: hvor høyt, og hvor langt ned til noe flatt.

### 5. Flyging uten infrastruktur (10 min)

Bolken klubben faktisk får noe ut av, og den har allerede de beste notatene dine:

> Floor is lava. Risiko snus på hodet, du gjør ting i lufta du ikke ville gjort
> om du kunne landet og tatt en taxi til pubben.

Marginer, høydesyke, buddysystem, satellittkommunikasjon, mat og vann for en uke.
**Broen skriver seg selv:** du snakker om å vite hvor de andre er og samband uten
dekning. Det er det appen gjør.

### 6. pgpilot (10 min)

Nå er den fortjent. Live demo på **2026-turen**, som er tatt opp med appen selv.
Live-posisjoner, gruppesamband, sporing, luftrom, varsel. Avslutt med at den er
gratis og at du vil ha tilbakemelding fra folk som flyr på Voss.

### 7. Bli med (5 min)

2026-turen er beviset på at det lar seg gjenta. Avslutt på tandoori-videoen, ikke
på en punktliste.

**Slide 46 sier fortsatt "Oktober 2024?"** - det er rekrutteringsslidet fra en
eldre versjon og må oppdateres.

## Demoflightene

Begge er offentlige og spiller av uten innlogging.

| | Dato | Rute | Tid | Langs sporet | Topp | Flight |
|---|---|---|---|---|---|---|
| **Demo 1** | 2024-10-17 | Bir → Saurkundi | 3t 00m | 123 km | 4677 m | `08609297-a5f3-4e03-8b0e-d24af4d5be74` |
| **Demo 2** | 2026-04-05 | Bir, tur/retur | 4t 24m | 171 km | 3426 m | `2e516665-78cd-43c5-a307-643bc232d352` |

    https://pgpilot.app/flight/08609297-a5f3-4e03-8b0e-d24af4d5be74
    https://pgpilot.app/flight/2e516665-78cd-43c5-a307-643bc232d352

Dag 2 fra 2024, hvis du vil ha den også:
`0307393d-69aa-4e16-9613-cc1502f13252` (5t 43m, 219 km, topp 5509 m).

### Hva de to faktisk viser

Verdt å vite før du bygger demoen rundt en antakelse:

- **2024 dag 1** er importert fra XContest. IGC med 10 843 punkter, 1 Hz, og
  trykkhøyde opp til 4677 m. Replay, kart og høydeprofil funker fullt ut.
- **2026-05-04** er tatt opp med appen. Track-blob med **79 107 punkter, altså
  5 Hz**, fem ganger tettere enn IGC-en.

Men blobben inneholder posisjon, trykkhøyde og fart - **ikke vario- eller
vindfelt**. Appen utleder stigning fra trykksporet, så barogram og vario vises
fint, men det er ikke noe vindsensor-data å vise fram. De to flightene replayer
altså omtrent like godt; forskjellen er oppløsning, ikke flere målinger.

De største dagene i 2026 (14. april: 8t 06m, 339 km, 212 km XC) ligger bare som
XContest-importer, ikke som appopptak.

## Om materialet

Kontoen har 78 flighter i Bir/Billing fordelt på tre turer: okt/nov 2023 (10,
importert), okt 2024 (10, importert), mars/april 2026 (~58, stort sett tatt opp
med appen).

### Sett i forbifarten

XContest-synken lager dupliserte rader: flere flighter finnes to ganger, én med
`source_platform=xcontest, is_public=false` og én med `source_platform=null,
is_public=true`. Og 2026-04-12 har en rad på 1080 min / 482 km klassifisert som
`junk`. Påvirker ikke foredraget, men det er ekte.
