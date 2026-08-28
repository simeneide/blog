# Overlevering: Voss-decket

Du overtar et foredrag som skal holdes **fredag på klubbkveld på Voss**. Det
meste er bygget. Dette dokumentet er alt du trenger for å fullføre det.

Skriv på norsk til Simen. **Bruk aldri tankestrek (—)**, bruk vanlig bindestrek,
komma eller punktum.

## Hva dette er

| | |
|---|---|
| Decket | `pgpilot/voss.qmd` i dette repoet, Quarto revealjs, 42 slides |
| Publisert | https://eide.ai/pgpilot/voss.html |
| Planen | `pgpilot/STRUKTUR.md` |
| Kildebibliotek | `himalaya/presentasjon.qmd`, det gamle India-decket fra Loen, 50 slides |

Bygg med `quarto render pgpilot/voss.qmd`. Output havner i `docs/`, som er det
GitHub Pages serverer. Commit og push til `main` publiserer.

Forhåndsvisning lokalt:

    cd docs && python3 -m http.server 8791 --bind 127.0.0.1
    # http://127.0.0.1:8791/pgpilot/voss.html

## Formen på foredraget

Hele timen er **én flytur salen er med på**. Ikke et foredrag med en demo på
slutten. Vi tar av fra Billing sammen og lander sammen. Featurene kommer fram
fordi flyturen krever dem.

Målet er at **alle i salen installerer appen og prøver den**. Derfor er
installasjonen åpningsnummeret, og gruppa holdes levende gjennom kvelden.

Aktene: åpning og hvorfor Bir, installer appen, på startplassen, vi tar av,
innover i fjellene, landing og hjem, sees vi.

## Det som gjenstår

1. **Task-bildet** i akt 2, sliden `## Lag tasken`. Trenger en skjermdump fra
   Simens telefon av en ferdig utfylt oppgave. Enda bedre med to: én av tasken
   han lager, og én av "Load task"-varselet slik det ser ut på en annens
   telefon. Det er poenget med sliden.
2. **`## Dere er fortsatt i gruppa`** i akt 4 er et live app-innhopp og trenger
   ikke bilde.

Bilder hentes fra Simens telefon via Google Photos:

    uv run ~/.claude/skills/google-photos/scripts/google_photos.py pick --no-wait
    # gi ham URL-en, vent til han sier fra, så:
    uv run ~/.claude/skills/google-photos/scripts/google_photos.py pick-resume \
        --session-id <id> --download ~/nedlastet

## Riggen på fredag

**Ikke plugg ut projektoren for å vise telefonen.** Én HDMI-kabel fra maskina,
telefonen speilet inn i et vindu, og alt-tab mellom deck og telefon.

Simen har **Android**, så det er `scrcpy` over **USB**:

    brew install scrcpy      # hvis den mangler
    scrcpy

Kabel framfor trådløst, av tre grunner: gjestewifi i klubblokaler har ofte
klientisolering som blokkerer trådløs scrcpy, kabelen har lavere latens, og
telefonen lader gjennom en time med skjermen på.

**Gjør dette hjemme, ikke i lokalet:** slå på USB-debugging under
utvikleralternativer og huk av "tillat alltid fra denne maskinen". Ellers
spretter den dialogen opp midt i akt 1, på en telefon som er speilet på
lerretet.

Reveal beholder slide-posisjonen når du alt-tabber. `b` svartlegger decket, fint
å trykke rett før du bytter.

## Gruppa: den enkleste måten å ødelegge kvelden

Reaperen arkiverer grupper der `last_activity_at` er eldre enn **fire timer**,
og join-oppslaget filtrerer på `archived = false`. En gammel gruppe gir altså en
QR-kode som leder til ingenting, foran hele salen.

**Gruppa lages når han rigger, ikke før.** Join tupper aktiviteten, så når de
første i salen er inne holder den seg selv i live resten av kvelden.

QR-koden i decket peker på `pgpilot.app/join/voss`.

## Fellene vi allerede har gått i

Disse kostet timer. Ikke oppdag dem på nytt.

- **KK7 er nede.** `thermal.kk7.ch` svarer ikke, verifisert fra to maskiner.
  Derfor er termikk-overlegget ikke med noe sted. Sjekk om de er oppe igjen.
- **Estimatorene er kalde etter søk.** Spiller du ikke fram før opptak, viser
  WIND og GLIDE bare `--`.
- **Søk tømmer sporhistorikken.** Vil du vise spor som vokser, må du spille fram
  på høy hastighet og filme i 1x.
- **Replay-slideren er indeksbasert, ikke tidsbasert.** På en flight med 18 000
  punkter er ett hakk 18 sekunder. Les flighttiden fra teksten i stedet.
- **Kartzoom settes med minus-knappen mens replay står på pause.** Gjennom
  kartobjektet blir den overstyrt av følg-logikken.
- **Glide range i høy kvalitet** ber om rundt 120 terrengfliser mens cachen tar
  128, og laget tegnes ikke før hele settet er inne. Prefetchen prøver bare på
  nytt når posisjonen endrer seg, så pauset replay prøver aldri igjen. Løsningen
  var å hoppe ni sekunder fram og tilbake fjorten ganger.
- **Utzoomet kart med høydekoter rendrer for tregt til jevn video** på Linux-
  boksen. MacBook-en er fire ganger raskere: 20 fps mot 5.
- **BLE-varioen er låst bak `isNative()`**, så hardware-seksjonen finnes ikke i
  webversjonen. De skjermdumpene må tas på telefon.

Oppskriften for app-opptak står i `pgpilot_reels`-skillen, og **3D-delen ligger
bare i `origin/main`**, ikke i arbeidskopien:

    cd ~/pgpilot && git show origin/main:.opencode/skills/pgpilot_reels/SKILL.md

## CSS-regler som ikke må ryddes bort

I `pgpilot/voss.css`. Alle tre er der fordi noe gikk galt uten dem:

- `:has(> .fullbleed)` med `>`. Uten pilen traff regelen hele akt-stabelen og
  gjorde alle slidene i akten svarte.
- `section.stack { padding: 0 }`. Stabelen er også en `<section>`, så den
  generelle paddingen dyttet fullskjermsbilder inn 64 px og la igjen en hvit
  stripe.
- `h2:empty { display: none }`. Bildeslides uten tittel fikk ellers en tom svart
  tittelboks nederst til venstre.

## Arbeidsmåte

- Verifiser med Playwright mot forhåndsvisningen, ikke bare at Quarto bygget.
  Sjekk at videoer har `videoWidth > 0` og `error === null`, og at ingen bilder
  har `naturalWidth === 0`.
- **Se på skjermbilder med Read før du bruker dem.** Flere ganger har et bilde
  lastet fint og likevel vist feil ting. Det er den vanligste feilen her.
- Portrettbilder i et 16:9-slide blir beskåret av `object-fit: cover`. Sett
  `style="object-position: 50% NN%"` og verifiser med skjermdump.
- Commit på norsk, forklar hvorfor. Ingen "Generated with"-fottekst, ingen
  Co-Authored-By.
