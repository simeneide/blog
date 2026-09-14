# Notes, and what is still missing

Built 14 September 2026. 23 slides, 7 minutes 31 seconds per lap.

## TODO: eight recordings are not in yet

Eight landscape 1920x1080 screen recordings were being made while this deck was
built. None of them existed at build time, so every slide that wants one is
running on a fallback. The fallbacks are real clips, not placeholders, so the
deck is show-ready as it stands, but these are the upgrades.

Drop the file in `/home/simen/.claude/jobs/eeb1fb3a/tmp/kiosk-clips/` under
exactly this name and re-run `uv run build.py`. The slide switches from the
fallback to the recording by itself, no edits needed.

| Expected file | Slide | Running on instead |
|---|---|---|
| `thermal-assist.mp4` | Thermal assist | phone, `klipp-termikk.mp4` (14 s, bubble and vario while circling) |
| `wind-estimation.mp4` | Wind estimation | phone, `hook_S_gaggle_wind.mp4` (12 s, 3D gaggle with wind) |
| `navigation.mp4` | Navigation | wide, `hvor-er-bir.mp4` (15 s, map zoom) |
| `sideview-glide.mp4` | Side view and glide range | phone, `klipp-sideview.mp4` (10 s, side view panel) |
| `replay-3d.mp4` | 3D replay | wide, `bir-3d.mp4` (38 s, Himalaya flyover) |
| `live-tracking.mp4` | Live tracking | phone, `klipp-tracking.mp4` (5 s, two pilots in one thermal) |
| `forecast-airgram.mp4` | Wind and forecast at the takeoff | duo stills, `app-bavallen-vind.jpg` + `app-bavallen-airgram.jpg` |
| `areacontest-whale.mp4` | AreaContest | blurred still behind the phone |

AreaContest is the one that behaves differently, on purpose. The Coupe whale
reel (`coupe_whale_v8.mp4`) stays in the phone frame either way, because that
reel *is* the AreaContest pitch for this stand. If `areacontest-whale.mp4`
lands it becomes the moving backdrop behind the phone instead of the blurred
still.

## Which source each slide uses right now

| # | Slide | Layout | Source |
|---|---|---|---|
| 1 | All you need in one flight app | title | `bir-3d.mp4` behind the wordmark |
| 2 | Thermal assist | phone | `klipp-termikk.mp4` |
| 3 | Wind estimation | phone | `hook_S_gaggle_wind.mp4` |
| 4 | Navigation | wide | `hvor-er-bir.mp4` |
| 5 | Side view and glide range | phone | `klipp-sideview.mp4` |
| 6 | 3D replay | wide | `bir-3d.mp4` |
| 7 | Live tracking | phone | `klipp-tracking.mp4` |
| 8 | Group voice and chat | phone | `app-comms.png`, Ken Burns inside the frame |
| 9 | Button on the brake line | phone | `klipp-knapp.mp4` |
| 10 | Wind and forecast at the takeoff | duo | `app-bavallen-vind.jpg`, `app-bavallen-airgram.jpg` |
| 11 | Ground contacts | phone | `klipp-start.mp4` |
| 12 | Your flights, synced | wide | `app-flightdetails.jpg`, dimmed |
| 13 | AreaContest | phone | `coupe_whale_v8.mp4` + QR for pgpilot.app/coupe |
| 14 | Works without coverage | phone | `klipp-backcountry.mp4` |
| 15 | Try it now | closing | `bir-3d.mp4` behind the big QR |

## The "It learns from your flying" run

Six slides between Flights and AreaContest, 116 seconds in all. They are the
material of the A0 "Algorithms of pgpilot" poster, which was finished and then
dropped before print; the sources are in the pgpilot repo under
`brand/coupe-icare-2026/poster-air/` (`HANDOFF.md` first, then `README.md`'s
"Where every number comes from", and `poster.html` for the verified copy).

Only the first slide has a strip label and a key, `I`. The other five have an
empty label, which `kiosk.js` reads as "share the chip before you": the strip
is one row of 1920 px and was already full at 17 entries. Arrow keys still
step through them one at a time.

| Slide | Layout | What is on it | Source |
|---|---|---|---|
| It learns from your flying | section | The whole instrument mid-thermal, pulling back, with the four measured-against numbers dealing themselves in | `shots/thermal-overlay-wide.png`, numbers from `poster.html`'s band |
| Wind from your circles | wide | 20 s animation: 120 GPS velocity dots arriving one per second, the Kasa fit re-run on the growing set, the pitot wind dropped in at 15 s | `hodograph.json` + `hodograph.py`, rendered by `ALGO/hodograph/make.py` |
| Where the lift is | wide | The core ring, the lift bubbles and the wind arrow, pushing in on the core | same capture, cropped tight |
| Every flight keeps its forecast | duo | The pinned ICON-EU card with its provenance prose, and the flown altitude trace | `shots/flight-vs-forecast.png`, top of `shots/flight-vs-forecast-tall.png` |
| Hike, ground, fly | phone | The flight page's segment bar, altitude profile and the three ACTIVITY cards | `shots/hike-and-fly-2.png` |
| Where will it work today? | seq | The Alpine arc by region, pushing in on the region that holds Saint-Hilaire, then cross-fading to that region selected | `regional/regions-alps.png`, `regional/regions-saint-hilaire.png` |

Every claim on them is a sentence from `poster.html` or from `README.md`'s
number table. The three that are easy to get wrong, and are therefore worded
exactly as the handoff demands: the forecast is **kept as it stood that
morning**, never "your flight against the forecast"; the regional map is
**climb above local terrain**, never thermal top or strength, and is called a
research prototype on the slide; and the thermal core is a **lift and recency
weighted centre**, not a Kalman filter.

### How the media was made

Nothing in `img/` here is a raw poster asset: `ALGO/crops.py`
(`/home/simen/.claude/jobs/eeb1fb3a/tmp/algo/`, the `ALGO` path in `build.py`)
pre-crops every capture to the shape the slide shows it in, because the kiosk
covers and then pushes by up to 13%, so anything at the edge of a crop walks
out of frame. It also does two things worth knowing:

- **It blurs two labels on the thermal overlay.** Both name another pilot
  (one under the compass button, one inside the core ring, mostly behind the
  own-ship arrow), and the handoff's rule is that no other pilot's name goes
  on screen. The blur is a feathered oval, not a rectangle, because a
  rectangle of blur is the first thing the eye finds.
- **It pads two of the crops.** The duo cells get a blurred bleed of their own
  picture, the phone crop a flat fill of the app's own page colour, so the
  Ken Burns has margin to eat instead of axis labels and first words.

The hodograph clip is `ALGO/hodograph/`: `render.html` exposes `render(t)` and
draws the frame from `t` alone, `make.py` screenshots 500 frames with
Playwright and encodes them at 25 fps. Re-run either script and then
`uv run build.py`. The final numbers it lands on are the poster's:
wind 2.6 m/s from 212 deg, airspeed 9.0 m/s, pitot 2.0 m/s from 210 deg.

## Things worth a second look

- **The lap is 7 min 31 s, and the README asks for four to five.** The
  "It learns" run is 116 s of that and the deck had already grown past five
  minutes before it landed. A visitor standing still no longer sees
  everything. If that matters more than the depth, the cheapest cuts are
  "Where the lift is" (18 s, the closest thing to a repeat, since Thermal
  assist already has the same subject) and trimming the run's slides from 20 s
  to 18 s.
- **"Your flights, synced" shows another pilot's name.** `app-flightdetails.jpg`
  has a FLYING WITH row that reads "Jørgen Sørenssen (Ozone Lyght)", and at
  42% brightness it is still legible on a 1920 screen. The poster material was
  cropped and blurred specifically to keep peers' names off this monitor; this
  slide predates that rule and has not had the same treatment. A tighter crop
  of the same screenshot would fix it.
- **The corner QR sits over the top-right corner of every wide and duo
  slide.** On "Every flight keeps its forecast" that decided the order of the
  two cells: the forecast prose is on the left, the chart on the right, where
  there is nothing in the corner to lose.
- **Ground contacts (slide 11) is the weakest match.** `klipp-start.mp4` is a
  replay of a flight starting, not a takeoff notice going out. Nothing in the
  library shows the message a ground contact actually receives. A five second
  recording of the contacts screen, or of the SMS arriving on a second phone,
  would carry the slide far better than this does. There is no
  `groundcontacts.mp4` in the expected list, so it will not fix itself.
- **Your flights, synced (slide 12)** runs on a light four-panel screenshot.
  Full bleed it competed with the white text and swallowed the corner QR, so it
  is dimmed to 42 % and reads as texture: the title card carries the message,
  the picture just moves. If a recording of the flight detail page ever
  appears, that slide gains the most.
- **`video/` is 303 MB** now that the recordings have landed, and `build.py`
  mirrors the whole folder into
  `/home/simen/blog/docs/pgpilot/coupe-kiosk/`, so the blog repo carries about
  600 MB of it. `bir-3d.mp4` alone is 53 MB at crf 20, because a 3D render at
  1920x1080 is expensive to encode cleanly. Worth deciding before committing:
  raise `CRF` in `build.py`, or keep the videos out of git and copy them onto
  the stand machine by hand.
- **The phone frame clamps the clip aspect to at most 0.60 wide**
  (`PHONE_MAX_RATIO` in `kiosk.js`). `klipp-knapp.mp4` is 1080x1714, which cut
  as a real 9:16 frame lost the leading digit of the altitude readout, and a
  cut-off number reads as a bug. At 0.60 the crop is 2.4 % a side and the frame
  still matches the other eight phone slides. If a new portrait clip is wider
  than that, check the slide before trusting it.
- The kiosk hides the mouse cursor (`cursor: none`). On the stand that is
  right. While editing it is briefly confusing.

## Checks that were run

Playwright, Chromium, 1920x1080, served over `python -m http.server`:

- every hotkey jumps to the right slide, and the strip highlight follows
- clips play with no click: `currentTime` advances on every video slide
- Ken Burns is live on every still: `animationName` is `kenburns` or
  `kenburns-bg`, with the slide's own duration
- auto advance with no input at all: wind (18 s) rolled on to nav by itself
- `Esc` opens the overview, `1` `3` `Enter` jumps to slide 13, and a lone `3`
  still reaches 3D replay
- the strip fits: 18 entries between x=17 and x=1903 of 1920. It is full. The
  next slide that wants its own entry needs a shorter label somewhere, or an
  empty label so it shares the chip before it.
- the loop wraps: the closing slide ran out and came back to the title
- the published mirror in `docs/` was served and driven too, with no 404s
- no console errors on any slide
- both QR codes were rendered and decoded back: `https://pgpilot.app` and
  `https://pgpilot.app/coupe`
