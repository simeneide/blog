# pgpilot kiosk, Coupe Icare 2026

An auto-playing feature cavalcade for the stand monitor at Saint-Hilaire,
14 to 20 September 2026. 1920x1080 landscape, 23 slides, seven and a half
minutes per lap, and it loops forever.

Everything it needs is in this folder. It runs with the network cable pulled
out: Reveal.js, both fonts, both QR codes, every clip and every still are
local files.

## Run it

Full screen, no browser chrome, clips allowed to start on their own:

**Linux**

```sh
google-chrome \
  --kiosk --autoplay-policy=no-user-gesture-required \
  --disable-features=Translate --noerrdialogs --disable-infobars \
  --start-fullscreen \
  "file:///home/simen/blog/pgpilot/coupe-kiosk/index.html"
```

**macOS**

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --kiosk --autoplay-policy=no-user-gesture-required \
  --disable-features=Translate --noerrdialogs --disable-infobars \
  "file:///Users/simen/blog/pgpilot/coupe-kiosk/index.html"
```

**From the published site** (needs wifi, so it is the backup, not the plan):

```sh
google-chrome --kiosk --autoplay-policy=no-user-gesture-required \
  "https://eide.ai/pgpilot/coupe-kiosk/"
```

If the clips sit on a black frame and never start, the autoplay flag did not
take. Chrome only honours it at launch, so quit Chrome completely first.

To exit kiosk mode: Alt+F4 on Linux, Cmd+Q on macOS.

## Hotkeys

The strip along the bottom lists every slide and its key. Press the key and
the deck jumps there. It keeps auto-playing from wherever you land, so the
screen never gets stuck on one slide because someone walked away.

| Key | Slide |
|---|---|
| `Home` | Title |
| `T` | Thermal assist |
| `W` | Wind estimation |
| `N` | Navigation |
| `S` | Side view and glide range |
| `3` | 3D replay |
| `L` | Live tracking |
| `C` | Group voice and chat |
| `R` | VHF bridge |
| `H` | Button on the brake line |
| `F` | Wind and forecast at the takeoff |
| `G` | Ground contacts |
| `X` | Analyse your flight |
| `I` | It learns from your flying (five slides, one entry) |
| `A` | AreaContest, the Coupe whale |
| `O` | Works without coverage |
| `End` | Try it now, the big QR |

**Or press the strip.** Every entry is a button, and the two zones down the
left and right edges of the screen step back and forward, so the whole deck is
usable on a touch monitor with no keyboard. Whatever you press, that slide then
gets its full time on screen before the deck moves on by itself.

Also: `Esc` for the overview grid, a slide number followed by `Enter` for a
direct jump, arrows or space to step by hand.

`3` is both the 3D replay hotkey and a digit. A lone `3` waits 0.6 s and then
jumps to 3D replay; type a second digit or `Enter` inside that window and it
is treated as a slide number instead.

## Add or replace a clip

Slides are defined in one place: the `SLIDES` list at the top of `build.py`.
`build.py` copies and re-encodes the sources into `video/` and `img/`, pulls a
poster frame out of every clip, writes `slides.js`, and mirrors the whole
folder into `/home/simen/blog/docs/pgpilot/coupe-kiosk/`, which is what the
blog publishes.

```sh
cd /home/simen/blog/pgpilot/coupe-kiosk
uv run build.py
```

It is safe to re-run: anything already encoded and newer than its source is
left alone, and it prints which recordings are still missing.

**To swap in a new landscape recording**, drop the file into the directory
`RECORDED` points at (`/home/simen/.claude/jobs/eeb1fb3a/tmp/kiosk-clips/`)
under the exact name the slide asks for, then re-run `build.py`. The slide
switches from its fallback to the recording by itself. The eight names it
looks for are `thermal-assist.mp4`, `wind-estimation.mp4`, `navigation.mp4`,
`sideview-glide.mp4`, `areacontest-whale.mp4`, `forecast-airgram.mp4`,
`replay-3d.mp4` and `live-tracking.mp4`. See `NOTES.md` for what each one
currently falls back to.

**To use a clip from somewhere else**, point that slide's `media` (or its
`fallback["media"]`) at the file and re-run. Any resolution works: portrait
goes in the phone frame, landscape goes full bleed. The encoder caps the long
edge at 1920, crf 20, H.264 yuv420p faststart, audio dropped.

**Six slides do not come from `RECORDED` at all.** The "It learns from your
flying" run (hotkey `I`) is built from pre-cropped poster captures and one
rendered clip in the `ALGO` directory `build.py` points at. To rebuild them,
run `crops.py` and `hodograph/make.py` in there, then `build.py`. `NOTES.md`
has the detail, including which labels are blurred and why.

**To change how long a slide stays up**, edit its `dur` in `build.py` and
re-run. The original rule was to keep the total between four and five minutes,
so a visitor standing still sees the whole thing; the deck is past that now, at
seven and a half. `NOTES.md` lists what to cut first if that matters.

The QR codes are checked in as SVG (`img/qr-pgpilot.svg` for
`https://pgpilot.app`, `img/qr-coupe.svg` for `https://pgpilot.app/coupe`).
`build.py` does not regenerate them. If a URL changes:

```sh
uv run --with qrcode python -c "
import qrcode, qrcode.image.svg
q = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage, border=2)
q.add_data('https://pgpilot.app')
q.make(fit=True)
q.make_image().save('img/qr-pgpilot.svg')"
```

## Files

| Path | What |
|---|---|
| `index.html` | The shell. Reveal container plus the two fixed pieces of chrome. |
| `kiosk.js` | Builds the slides from `slides.js`, starts Reveal, owns the keyboard, restarts clips and Ken Burns on every slide change. |
| `kiosk.css` | The look. Bevan, Questrial, near-black, sky blue. |
| `slides.js` | Generated. The resolved slide list. |
| `build.py` | The slide spec and the media pipeline. |
| `reveal/` | Reveal.js 5.1.0, vendored from the blog's `site_libs`. |
| `fonts/` | Bevan and Questrial woff2, the Voss deck's copies. |
| `img/` | Posters, stills, wordmark, QR codes. |
| `video/` | Every clip, re-encoded. About 120 MB. |

`video/` is why this folder is large, and the mirror in `docs/` doubles it in
the blog repo. Worth a look before committing.
