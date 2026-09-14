# Notes, and what is still missing

Built 14 September 2026. 15 slides, 4 minutes 45 seconds per lap.

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

## Things worth a second look

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
- **`video/` is 121 MB**, and `build.py` mirrors the whole folder into
  `/home/simen/blog/docs/pgpilot/coupe-kiosk/`, so the blog repo carries about
  240 MB of it. `bir-3d.mp4` alone is 53 MB at crf 20, because a 3D render at
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
- the strip fits: 15 entries between x=91 and x=1829 of 1920
- the loop wraps: the closing slide ran out and came back to the title
- the published mirror in `docs/` was served and driven too, with no 404s
- no console errors on any slide
- both QR codes were rendered and decoded back: `https://pgpilot.app` and
  `https://pgpilot.app/coupe`
