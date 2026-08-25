# Klubbkveld Voss - struktur

Arbeidsdokument. Utgangspunktet er India-decket fra Loen (okt 2025, 50 slides),
som nå er konvertert til `presentasjon.qmd`. Her er forslaget til hvordan
pgpilot flettes inn.

## Hovedgrepet

**pgpilot skal ikke være et eget kapittel på slutten.** Det skal være verktøyet
du viser turen med.

Sju av slidene i dagens deck er Google Earth-screenshots med tracket tegnet oppå
(6, 7, 12, 30, 31, 40, 43), og fem er XContest-kartbilder der en rød sirkel
flytter seg langs ruta (13, 14, 16, 19, 23). Det er tolv slides som gjør nøyaktig
det pgpilot gjør, bare som døde bilder. Bytt dem mot ekte pgpilot-replay, og da
har du vist appen i ti minutter før du har sagt at den finnes.

Så tar du én kort eksplisitt bolk: "dette kartet dere har sett på hele kvelden er
noe jeg har bygget". Da lander det som en avsløring i stedet for et salgspitch,
og du får avslutte på flyging i stedet for på software.

## Kjøreplan (~45 min + spørsmål)

| # | Bolk | Min | Gamle slides | pgpilot |
|---|---|-----|--------------|---------|
| 1 | Krok: bare fly | 2 | 1, 9 | - |
| 2 | Hvor i all verden er Bir? | 3 | 2, 3, 4, 5 | Kartet zoomer fra Voss til Bir |
| 3 | Fronten: første møte | 7 | 6, 7, 8, 10, 17 | **Replay av frontflygingen** (erstatter 6/7) |
| 4 | Volbiv: over til baksiden | 10 | 11, 12, 15, 18, 20, 22 | **Replay som scrubber langs dag 1** (erstatter 13/14/16/19/23) |
| 5 | Flyging uten infrastruktur | 8 | 21, 24, 27, 28, 29 | Avsløringen ligger her |
| 6 | Dag 2: Shikah Beh | 8 | 30-35, 39-45 | **Replay av dag 2** (erstatter 30/31/40/43) |
| 7 | Hva skal til? | 4 | 36, 37 | - |
| 8 | Bli med i 2026 | 3 | 46, 47, 48, 49, 50 | - |

### 1. Krok (2 min)

Start med video, ikke med deg selv. Slide 9 (volbiv) eller 48 (kjøre mot sky) i
fullskjerm, uten tekst. La den gå 30-40 sekunder. Så tittelslide.

### 2. Hvor er Bir? (3 min)

Slide 2/3 er to Google Maps-screenshots der den andre har en rød sirkel på Bir.
Det er en zoom, og en zoom er noe et kart gjør bedre enn to bilder.

### 3. Fronten (7 min)

Det milde møtet: soaring på frontryggen, termikk som funker, terrasser under.
Slide 6/7 er Google Earth med track. Erstatt med replay.

### 4. Volbiv over til baksiden (10 min)

Kjernen i dag 1. Dagens fem XContest-slides er egentlig én animasjon delt i fem
bilder. En replay som du scrubber i mens du snakker gjør samme jobb, og du kan
stoppe der historien er.

Her ligger også høydeprofilen som poeng: hvor høyt de faktisk var, og hvor langt
det var ned til noe flatt.

### 5. Flyging uten infrastruktur (8 min)

Dette er bolken klubben faktisk får noe ut av, og den har allerede de beste
notatene dine:

> Floor is lava. Risiko snus på hodet, du gjør ting i lufta du ikke ville gjort
> om du kunne landet og tatt en taxi til pubben.

Slide 21 og 28 er punktlister om marginer, høydesyke, buddysystem,
satellittkommunikasjon, mat og vann for en uke.

**Her ligger avsløringen.** Broen skriver seg selv: du snakker om buddysystem, om
å vite hvor de andre er, om samband uten dekning. Det er nøyaktig det pgpilot
gjør. Fem minutter: hva appen er, live-posisjoner, gruppesamband, sporing, og
"last den ned, den er gratis, jeg vil gjerne ha tilbakemelding fra folk som
flyr på Voss".

Så tilbake til India.

### 6. Dag 2 (8 min)

Ørna som flyr forbi (42), regnet (41), skyene (45), Bara Bhangal (44). Mest
video, minst snakk.

### 7. Hva skal til? (4 min)

Slide 36: "Hvem kan gjøre dette? Hvem kan gjøre dette trygt?" Ærlig svar.

### 8. Bli med (3 min)

Slide 47/49 "Why Bir?" er allerede en ferdig rekrutteringsslide. Avslutt på
tandoori-videoen (50), ikke på en punktliste.

## Hvordan pgpilot faktisk kommer inn i decket

Tre alternativer, i rekkefølge etter hvor trygge de er:

**A. Forhåndsopptak (anbefalt).** Kjør pgpilot-replay av India-flightene i
nettleser, ta opp skjermen, legg inn som lokale mp4-er akkurat som de andre
videoene. Maskineriet finnes allerede i `pgpilot_reels`-skillet. Funker uten
nett, ingen overraskelser på Voss, og du kan klippe til de gode partiene.

**B. Innebygd iframe** mot `pgpilot.app/flight/<slug>` i slidet. Ekte og
interaktivt, men krever nett i lokalet og at flighten er offentlig.

**C. Live demo.** Bytt til appen, vis turen der. Best hvis det funker, verst
hvis det ikke gjør det.

Forslag: **A som ryggrad, C som ett enkelt øyeblikk** i bolk 5, der du uansett
skal vise appen. Da har du ikke noe å tape på at nettet er dårlig.

## Flightene finnes allerede i pgpilot

Sjekket mot databasen. Kontoen har **78 flighter i Bir/Billing-området**, fordelt
på tre turer:

| Tur | Antall | Kilde |
|---|---|---|
| Okt/nov 2023 | 10 | importert fra flightlog/XContest |
| **Okt 2024** | 10 | importert fra XContest |
| Mars/april 2026 | ~58 | **tatt opp med pgpilot selv** |

**Volbiv-en i decket er 17.-18. oktober 2024.** Det er entydig: dag 1 lander på
(32.2143, 77.1107) og dag 2 starter på (32.2126, 77.1119), altså 200 meter unna.
Det er teltplassen.

| | Dato | Rute | Tid | Distanse | Topp | Flight |
|---|---|---|---|---|---|---|
| **Dag 1** | 2024-10-17 | Bir → Saurkundi | 3t 0m | 123 km | 4677 m | `08609297-a5f3-4e03-8b0e-d24af4d5be74` |
| **Dag 2** | 2024-10-18 | Saurkundi → Bir | 5t 43m | 219 km | 5772 m | `0307393d-69aa-4e16-9613-cc1502f13252` |

"Flying on the front ridge" (slide 6/7) er trolig 2024-10-10: 7t 21m, 312 km.

### Det viktige: replay funker allerede, offentlig

    https://pgpilot.app/flight/0307393d-69aa-4e16-9613-cc1502f13252

Flightene er `is_public = true`, og siden krever **ingen innlogging**. Testet:
kartet tegner hele tracket fra Saurkundi til Bir, høydeprofilen er der, og
"Replay full track"-knappen virker.

Merk at disse er XContest-importer uten track-blob, så appen faller tilbake til
IGC-en fra backend. Det fungerer, men det betyr **ingen vario, vind eller
temperatur** i dataene, bare posisjon og høyde.

**2026-turen er tatt opp med appen selv** og har ekte track-blobs. Hvis du vil
vise fram hva instrumentet faktisk måler, er vår-turen et bedre materiale enn
2024-importene. Verdt å vurdere: fortell 2024-historien, men bruk en 2026-flight
når du viser fram selve appen i bolk 5.

### Sett i forbifarten

XContest-synken lager **dupliserte rader**: flere flighter finnes to ganger, én
med `source_platform=xcontest, is_public=false` og én med `source_platform=null,
is_public=true`. Og 2026-04-12 har en rad på 1080 min / 482 km klassifisert som
`junk`. Ikke noe som påvirker foredraget, men det er ekte.

## Ting som må avklares

1. **Hvor lang tid har du?** Planen over er 45 min. Skal den ned til 30 kuttes
   bolk 3 og 7, og bolk 6 blir kortere.
2. **Er du alene?** Notatene på slide 36 og 38 sier "Dagfinn regi, simen
   sidekick". Hvis Dagfinn ikke er med må de to slidene skrives om.
3. **Slide 46 sier "Oktober 2024?"** Det er rekrutteringsslidet fra en eldre
   versjon. Skal den bli 2026?
4. **Hvilke India-flighter ligger i pgpilot?** Krever innlogging for å sjekke
   (`python3 .claude/skills/pgpilot_mydata/scripts/pgpilot_api.py login` i
   pgpilot-repoet, ett klikk i nettleseren). Uten dette vet vi ikke om replay
   er mulig, eller om tracket må importeres fra XContest først.
