# Klubbkveld Voss - plan

Rammer: **ca. én time**, **Simen alene** (Dagfinn er ikke med). Loen-decket
gjenbrukes ikke rett fram, det er kildebiblioteket vi plukker fra.

- Loen-decket, konvertert og komplett: `presentasjon.qmd` (50 slides)
- Voss-decket: `voss.qmd` (ikke laget ennå)

## Målet

**Alle i salen skal ha pgpilot installert og ha prøvd den før de går hjem.**

Det er ikke et biprodukt, det er hele poenget. India er ikke temaet, India er
*formen*: den er grunnen til at hver enkelt feature dukker opp akkurat der den
gjør.

## Grepet: hele timen er én flytur, og salen er med på den

Ikke et foredrag med en demo på slutten. Ikke en featureliste med bilder fra
India mellom. **Vi tar av fra Billing sammen, og vi lander sammen femti minutter
senere.** Alt appen kan, kommer fram fordi flyturen krever det, i den
rekkefølgen flyturen krever det.

Det løser tre problemer på én gang:

1. **Rekkefølgen gir seg selv.** Du skal ikke lenger finne på en logisk
   gruppering av førti features. Flyturen har allerede en.
2. **Appen er på skjermen hele timen.** Ingen veksling mellom "nå snakker jeg" og
   "nå demonstrerer jeg".
3. **Nettet som dør bak fjellryggen blir dramaturgi.** Det er ikke en
   begrensning du må unnskylde, det er vendepunktet i historien. Før: alt
   virker. Etter: hva står igjen?

Og det er sant. Jeg sjekket hva appen faktisk har av data over Bir mot prod:

| Datakilde | Voss | Bir |
|---|---|---|
| Startplasser (ParaglidingEarth) | ja | **ja**, "Billing - Bir", 2428 moh |
| Kart, terreng, høydekoter | ja | ja |
| Vario, flightcomputer, replay | ja | ja, kjører på telefonen |
| Gruppe, PTT, sporing | ja | ja, så lenge det er data |
| Luftrom | ja, luftrom.info på gjeldende AIP-syklus | **nei**, ett polygon: Delhi FIR |
| Værvarsel | ja, MEPS | **nei**, MEPS og ICON-EU stopper i Europa |
| Vindstasjoner | ja, Frost | **nei**, winds.mobi og Frost dekker Europa |
| NOTAM | ja | **nei**, 19 europeiske nasjonale kilder |

Poenget er ikke at appen er mangelfull i India. Poenget er at **India stripper
den ned til kjernen**, og det som står igjen er nøyaktig det som bærer:
sensorene i telefonen, kartet i minnet, sporet, og sambandet med de du flyr med.

## Kjøreplan (53 min + spørsmål)

| Akt | Hva skjer | Min | **Hvor** | Features |
|---|---|-----|---|----------|
| 0 | Krok + "hvor er India?" | 3 | deck | - |
| 1 | **Bli med på turen** | 5 | deck → **app** | gjestepålogging, `/join`, presence |
| 2 | **På startplassen** | 10 | **app, live** | startplassbase, BLE-vario, PTT, task-push |
| 3 | **Vi tar av** | 14 | deck, **video** | replay, vario, termikk, sirkling, vind, barogram |
| 4 | **Innover i fjellene** | 12 | deck, med ett app-innhopp | offline, VHF, FLARM, Meshtastic, InReach |
| 5 | **Landing og hjem** | 6 | deck | IGC, XContest, feed, AreaContest |
| 6 | Bli med i 2026 | 3 | deck | - |

**Bare to steder forlater du decket:** akt 2 er ren live-app, og akt 4 har ett
kort innhopp for å vise prikkene i rommet. Alt annet, inkludert hele replayen,
kjører fra decket. Det er med vilje. Se "Riggen" under.

---

## Riggen: ikke plugg ut, speil telefonen inn i maskina

**Svaret på "skal jeg plugge ut presentasjonen?" er nei.** Å bytte HDMI-kilde
midt i et foredrag er den vanligste måten å miste tre minutter og all flyt på,
og projektoren bruker gjerne ti sekunder på å synke om igjen hver gang.

Gjør dette i stedet: **én kabel fra maskina til projektoren, telefonen speilet
inn i et vindu på maskina, og alt-tab mellom deck og telefon.**

| Oppsett | Verktøy | Merknad |
|---|---|---|
| Android | **`scrcpy`** | USB eller `scrcpy --tcpip`. Lav latens, gratis, vindu du kan gjøre fullskjerm. Det klart beste alternativet. |
| iPhone + Mac | **QuickTime Player** | File → New Movie Recording → velg iPhone som kilde. Kablet, ingen installasjon. |
| iPhone + Linux | `uxplay` (AirPlay-mottaker) | Over wifi, så mer skjørt i et ukjent lokale. Test på stedet. |

Reveal beholder slide-posisjonen når du alt-tabber, så du mister ingenting. Og
**`b` svartlegger decket** - fint å trykke rett før du bytter, så ser skiftet
tilsiktet ut i stedet for rotete.

### Kan telefonen legges *inni* Quarto-presentasjonen?

Teknisk ja, men jeg fraråder det. `ws-scrcpy` serverer telefonskjermen som en
nettside, som du kan `<iframe>`-e inn i et slide. Men det er en server til som
må kjøre, og du alt-tabber uansett bare to ganger hele kvelden. Feilmodusen er
verre enn gevinsten: hvis iframen ryker står du med et dødt slide i stedet for
et vindu du bare kan klikke på.

### Hvor mye trenger du egentlig telefonen?

Mindre enn du tror, men ikke null:

- **Appen kjører i nettleseren.** Kart, startplassøk, gruppe, `/join`, PTT og
  task funker alt sammen i en vanlig fane ved siden av decket. Ingen speiling
  nødvendig.
- **Men installasjonen (akt 1) og BLE-varioen (akt 2) må være ekte telefon.**
  BLE-varioen er låst bak `isNative()` i `useBleVario.ts` og vil ikke funke i en
  nettleser på maskina, uansett hvor mye Web Bluetooth Chrome har.

Så: speil telefonen for akt 1 og 2, og bruk nettleserfanen hvis noe ryker.
Det er reserveplanen din, og den er gratis.

---

### Akt 0: Krok, og "hvor er India?" (3 min)

Video i fullskjerm, uten tekst, uten deg. La den gå. Ikke si noe. Så tittel.

Hensikten er å kjøpe deg retten til å be om noe i neste akt. Ikke bytt om: en
installasjonsoppfordring som det *første* du sier er et krav. Den samme
oppfordringen etter nitti sekunder Himalaya er en invitasjon.

**Så: "vi skal på tur til India og fly. Hvor er India?"**

Zoom ut fra Voss, over Europa, og inn igjen på Bir. Det er en billig effekt og
den funker hver gang, fordi den gjør avstanden fysisk i stedet for et tall.
Bygg den som et kartklipp i decket, ikke live - du vil ikke være avhengig av
nett og tile-lasting i minutt tre.

Landingspunktet for zoomen er startplassen, og det er der akt 2 begynner. Da har
du allerede plassert oss geografisk før du ber om noe som helst.

### Akt 1: Bli med på turen (5 min)

**Send en melding til klubben kvelden før:** "last ned pgpilot før du kommer, vi
skal bruke den." Det er verdt å gjøre, fordi App Store-nedlastingen er det
eneste i hele opplegget du ikke kontrollerer, og tretti samtidige nedlastinger
på et klubblokale-wifi er en reell måte å brenne fem minutter på.

De som har gjort det er klare med én gang. De som ikke har det, tar
nettleserveien på tredve sekunder. **Begge deler skal fram, ingen skal føle at
de kom for sent.**

> "Vi skal fly en tur i India sammen nå. Ta opp telefonen."

Du installerer live, telefonen speilet på storskjerm, mens du snakker. Si tallet
høyt når du er ferdig. Det beviser lav terskel i stedet for å påstå den.

**To veier, begge på lerretet samtidig:**

- **Butikken**, hvis de vil ha den i lomma til helgen.
- **`pgpilot.app` i nettleseren**, ferdig på under et halvt minutt.

Nettleser-veien er verdt å si høyt, for terskelen er lavere enn folk tror:
visningsnavn og ingenting mer. Ingen e-post, ingen konto. Verifisert i koden:
`useAuth.ts` (anonym gjest med bare visningsnavn), `useDeepLink.ts`
(`/join/{kode}` funker fra en vanlig nettleser-URL),
`lib/voice/web-aac-transport.ts` (PTT over web, ikke bare native).

Så **QR-koden til `pgpilot.app/join/voss`**, stor på lerretet, og la den stå. Ikke
få noen til å taste en URL. Kartet ved siden av, med prikkene deres som dukker
opp mens du snakker videre.

**Si tydelig at de skal la appen ligge på.** Akt 2 og akt 4 avhenger begge av at
de fortsatt er i gruppa senere på kvelden.

### Akt 2: På startplassen i Billing (10 min)

Vi står på 2428 meter. Sivilisasjonen er rett nedenfor, og **nettet virker**. Så
her gjør vi alt det vanlige, det de ville gjort på Voss en tirsdag.

- **Hvor er vi?** Kartet, terrenget, fjellkjeden som fortsetter bakover. Søk opp
  startplassen: ParaglidingEarth har "Billing - Bir" på 2428 moh. Det er en
  liten ting, men den viser at dette ikke er en Norge-app.
- **Koble på varioen.** BLE-vario hvis du har en med, ellers barometeret i
  telefonen. Vis at den plukker den opp.
- **Prat sammen.** PTT i gruppa. Én frivillig i salen trykker og snakker,
  stemmen kommer ut av høyttaleren. *Si eksplisitt "alle lytter, én snakker"* -
  ikke slipp tretti mikrofoner løs samtidig.
- **Lag tasken.** Du setter ruta vi skal fly, og den lander på telefonen deres
  med "Load task". Bekreftet i `useGroupTaskOrchestration.ts`: lederen setter,
  medlemmene aksepterer én gang, og etterpå oppdateres den stille. Det er det
  fineste øyeblikket i hele akten, fordi de ser at *du* gjorde noe og *deres*
  telefon endret seg.

Her er slide 47 sin "Why Bir?" argumentet du snakker over: sesong i oktober og
november, fjellkjede som ikke tar slutt.

*Bakgrunnstråd: samtidig som du snakker fylles kartet med prikker fra folk som
fortsatt holder på å bli med.*

### Akt 3: Vi tar av (14 min)

Den lengste akten, og den skal være det. **17. oktober 2024, Bir mot
Saurkundi.**

**Dette er et skjermopptak, ikke live app.** Det er et bevisst valg og det er
riktig valg: dette er den lengste sammenhengende bolken, den som er lettest å
snuble i live, og den eneste der du både skal styre appen og fortelle en
historie samtidig. Et opptak lar deg snakke fritt, pause der du vil, og aldri
vente på at et kart laster.

Formuleringen som gjør poenget uten å motsi videoen du står og viser:

> Dette er ikke en video av flyturen. Det er et opptak av **appen** som flyr den
> på nytt. Alt dere ser av tall og piler regnes ut mens sporet spilles av,
> akkurat som når jeg flyr.

Samme kode i replay som live. Det er hele poenget med at motoren er React-fri,
og det er verdt å si rett ut, for ingen gjetter det selv.

**Ta opp lyden.** Den akustiske varioen er halve opplevelsen, og en pipende
vario over høyttaleranlegget er det som får en sal med paragliderpiloter til å
kjenne det i magen. Et stumt skjermopptak er halve demoen.

Stopp der historien er, og bruk pauseknappen:

- Soaring på frontryggen rett etter start. Terrassene under.
- **Termikkboblene som dukker opp** mens vi flyr. Det er det du selv trakk fram,
  og det er den mest overbevisende enkeltbiten: appen tegner opp hvor det
  stiger, mens du ser på.
- Sirklingen, og hvordan **vindpila strammer seg opp** når den har nok sirkler.
- Barogrammet som bygger seg. 4677 meter på det høyeste.
- Glidetall og rekkevidde. *Hvor langt ned er det til noe flatt?* Det spørsmålet
  er broen til neste akt.

**Nøkternt om dataene, så du ikke lover for mye:** dag 1 er importert fra
XContest, IGC med 10 843 punkter på 1 Hz. 2026-flighten er tatt opp med appen
og har 79 107 punkter, altså 5 Hz. Men blobben har posisjon, trykkhøyde og fart,
**ikke vario- eller vindfelt**. Appen utleder stigning fra trykksporet. De to
replayer altså omtrent like godt, forskjellen er oppløsning.

#### Opptaket du må lage

Dette er den eneste virkelige produksjonsjobben som gjenstår før fredag.

- **Kilde:** telefonen, skjermopptak med lyd, i stående eller liggende alt etter
  hvordan du vil ha det i decket. Liggende fyller lerretet best.
- **Innhold:** demo 1 spilt av i replay, i et tempo som gir deg tid til å
  snakke. Vurder å ta opp lengre enn du trenger og heller klippe.
- **Klipp det ned til fire-fem minutter.** Fjorten minutter akt betyr ikke
  fjorten minutter video: du skal pause og snakke mellom høydepunktene. Video
  som ren bakgrunnsstrøm gjør at salen slutter å høre på deg.
- **Legg det i decket som `<video>`**, samme mønster som Himalaya-klippene i
  `presentasjon.qmd`. Da er det én ting som spiller av, ikke en app som kan
  henge.
- **Ha klippet lokalt**, ikke fra Drive. Se sjekklisten.

### Akt 4: Innover i fjellene (12 min)

**Vendepunktet.** Vi passerer siste rygg. Nettet dør.

Nå slukker du data-lagene ett for ett, og det er her salen skjønner hva slags
flyging dette faktisk er. Notatene dine er allerede det beste du har:

> Floor is lava. Risiko snus på hodet. Du gjør ting i lufta du ikke ville gjort
> om du kunne landet og tatt en taxi til pubben.

Marginer, høydesyke, buddysystem, mat og vann for en uke. Og det å vite hvor de
andre er når det ikke finnes noen vei ned.

Hva står igjen når nettet er borte:

- **Offline-kartet**, lastet ned på forhånd. Kartet dør ikke.
- **VHF-radioen** over KV4P, og broen som mikser VHF-prat inn i gruppa.
- **FLARM og Meshtastic** for pilot-til-pilot uten infrastruktur i det hele
  tatt. Verdt å nevne at **OGN og FLARM-bakkestasjoner knapt finnes i
  Himalaya**, som er nettopp derfor direkte pilot-til-pilot er det som bærer der
  nede.
- **InReach** når det ikke er noe som helst. Satellitt, og noen hjemme som ser
  prikken din bevege seg.
- **Buddies**: hvor er de andre, sist sett når.

*(Jeg leste "v- og f-funksjonen" som VHF og FLARM. Si fra hvis du mente noe
annet, så bytter jeg.)*

**Publikums-beatet her:** de er fortsatt i gruppa fra akt 1. Vis kartet med alle
prikkene i rommet og si at dette er nøyaktig samme mekanisme som holdt oss
sammen over ryggen, bare med bedre dekning.

*Prøv nå: last ned offline-pakken for Voss.* Praktisk, virker på klubbturen, og
de har den neste gang de flyr uten dekning.

### Akt 5: Landing og hjem (6 min)

Vi lander ved teltplassen. Dag 1 lander 200 meter fra der dag 2 starter, og det
er ikke tilfeldig, det er teltet.

Så det som skjer etterpå, som er grunnen til at de åpner appen igjen på tirsdag:

- IGC ut, automatisk opplasting til XContest, dedup mot det som alt ligger der.
- Den offentlige feeden, profiler, kudos.
- **AreaContest.** Territoriespillet er den beste retensjonsmekanikken du har,
  og et Voss-publikum er nøyaktig folk som vil krangle om hvem som eier hvilke
  ruter. Vis kartet over deres eget område.

*Prøv nå: koble XContest-kontoen din.*

### Akt 6: Bli med i 2026 (3 min)

2026-turen er beviset på at det lar seg gjenta. Avslutt på tandoori-videoen,
ikke på en punktliste.

**Slide 46 sier fortsatt "Oktober 2024?"** Rekrutteringsslidet er fra en eldre
versjon og må oppdateres før Voss.

Siste ord bør være en oppfordring, ikke en takk: appen er gratis, den ligger på
telefonen deres nå, og du vil ha tilbakemelding fra folk som flyr på Voss.

---

## Hvis du må kutte

I denne rekkefølgen:

1. **Akt 5** ned til to minutter. AreaContest alene, dropp IGC/XContest.
2. **Akt 2**, dropp BLE-varioen. Telefonens barometer holder.
3. **Akt 3**, dropp glidetall og FAI. Behold termikkboblene og vindpila.

Ikke kutt i akt 1 eller akt 4. Det er de to som gjør salen til deltakere.

## Sjekkliste

**Denne uka**

- [ ] **Lag replay-opptaket til akt 3.** Skjermopptak av demo 1, *med lyd*,
      klippet til fire-fem minutter. Den eneste reelle produksjonsjobben igjen.
- [ ] **Bygg zoom-klippet til akt 0**: Voss → Europa → Bir, som video, ikke live.
- [ ] **Sett opp og test speilingen** (`scrcpy` eller QuickTime), se "Riggen".
      Gjør dette nå, ikke i lokalet.

**Dagen før**

- [ ] **Meld i klubbkanalen:** "last ned pgpilot før du kommer."
- [ ] **Ikke lag gruppa ennå**, se under. Bestem bare koden, kort og uttalbar,
      så du får laget QR-koden: `pgpilot.app/join/voss`.
- [ ] Last ned offline-pakke for Voss på demotelefonen.
- [ ] Åpne begge demoflightene én gang så de er i cache.
- [ ] Lag tasken du skal pushe i akt 2 på forhånd, så du bare henter den fram.
- [ ] **Test at replay og gruppa fungerer samtidig, på to telefoner.** Kjør
      replay på den ene og se på den andre. Jeg fant ikke ut sikkert av koden om
      en replay sender posisjonen din ut til gruppa eller ikke, og det er
      raskere for deg å teste enn for meg å bevise. Uansett svar funker akten,
      men du bør vite hva salen ser på sin egen telefon når du flyr.
- [ ] Avinstaller appen fra demotelefonen. Akt 1 må være ekte.

**På stedet, før du starter**

- [ ] **Lag gruppa nå, ikke før.** Verdt de tre setningene, for dette er den
      enkleste måten å ødelegge både akt 1 og akt 4 på:

      Reaperen kjører hvert tiende minutt og arkiverer alle grupper der
      `last_activity_at` er eldre enn **fire timer**. Ikke 24 timer, som
      `docs/subsystems.md` fortsatt påstår. Join-oppslaget filtrerer på
      `archived = false`, så en arkivert gruppe er *borte* for lenken: QR-koden
      din leder til ingenting, foran hele salen.

      Den gode nyheten: **join tupper `last_activity_at`**. Så snart de første i
      salen er inne, holder gruppa seg selv i live resten av kvelden. De førti
      minuttene mellom akt 1 og akt 4 er helt trygge.

      Risikovinduet er bare fra du lager den til første join. Lag den når du
      rigger.

- [ ] Test speiling av telefon til projektor. Dette er den vanligste
      teknikkfeilen, og den dreper akt 1.
- [ ] Sjekk nettet. Takler lokalets wifi tretti telefoner? Ha hotspot som
      reserve for **din egen** maskin uansett.
- [ ] QR-koden oppe på et slide du kan la stå. Ikke få folk til å taste URL-er.
- [ ] Kjør decket **lokalt**, ikke fra eide.ai. Videoene ligger i full
      oppløsning i `himalaya/video/`, så slipper du Drive-iframene.

**Reserveplan**

| Hvis dette feiler | Gjør dette |
|---|---|
| Nettet i lokalet | Hotspot for egen maskin. Replay funker offline. |
| Ingen blir med i gruppa | Ha en andre telefon i lomma som alt er med |
| Speiling til projektor | Nettleserfanen på maskina. Alt i akt 2 unntatt BLE-varioen funker der. |
| Replay-videoen spiller ikke | Slide 8, 10, 17 viser samme flight statisk |
| Live-appen henger i akt 2 | Hopp videre. Akt 3 er video og rammes ikke. |
| PTT-demoen gir bare støy | Kutt til fortelling, vis kartet med prikkene i stedet |

## Demoflightene

Begge er offentlige og spiller av uten innlogging.

| | Dato | Rute | Tid | Langs sporet | Topp | Flight |
|---|---|---|---|---|---|---|
| **Demo 1** | 2024-10-17 | Bir → Saurkundi | 3t 00m | 123 km | 4677 m | `08609297-a5f3-4e03-8b0e-d24af4d5be74` |
| **Demo 2** | 2026-04-05 | Bir, tur/retur | 4t 24m | 171 km | 3426 m | `2e516665-78cd-43c5-a307-643bc232d352` |

    https://pgpilot.app/flight/08609297-a5f3-4e03-8b0e-d24af4d5be74
    https://pgpilot.app/flight/2e516665-78cd-43c5-a307-643bc232d352

Dag 2 fra 2024, hvis du vil ha den: `0307393d-69aa-4e16-9613-cc1502f13252`
(5t 43m, 219 km, topp 5509 m). Dag 1 lander 200 meter fra der dag 2 starter.

## Om materialet

Kontoen har 78 flighter i Bir/Billing fordelt på tre turer: okt/nov 2023 (10,
importert), okt 2024 (10, importert), mars/april 2026 (~58, stort sett tatt opp
med appen).

De største dagene i 2026 (14. april: 8t 06m, 339 km, 212 km XC) ligger bare som
XContest-importer, ikke som appopptak.

### Sett i forbifarten

XContest-synken lager dupliserte rader: flere flighter finnes to ganger, én med
`source_platform=xcontest, is_public=false` og én med `source_platform=null,
is_public=true`. Og 2026-04-12 har en rad på 1080 min / 482 km klassifisert som
`junk`. Påvirker ikke foredraget, men det er ekte.
