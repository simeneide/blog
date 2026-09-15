# pgpilot kiosk, Coupe Icare 2026

A title-first, continuously looping feature demo for a 1920x1080 stand screen.
16 slides, about four and a half minutes. No introduction or closing slide.
Most slides contain only a title; five retain one short supporting line.

## Run it

The complete, self-contained deck is `docs/pgpilot/coupe-kiosk/` in the blog
checkout. Its videos, stills, fonts, Reveal.js and QR codes are local files.
Copy that entire folder to the stand computer for offline use.

```sh
google-chrome --kiosk --autoplay-policy=no-user-gesture-required \
  --disable-features=Translate --noerrdialogs --disable-infobars \
  "file:///home/simen/blog/docs/pgpilot/coupe-kiosk/index.html"
```

Online review: <https://eide.ai/pgpilot/coupe-kiosk/>.
Quit Chrome completely before relaunching if its autoplay flag is ignored.
Exit kiosk mode with Alt+F4 on Linux or Cmd+Q on macOS.

## Controls

Every entry in the bottom strip is a button. The screen edges and arrow keys
step backward or forward. Any manual jump restarts that slide and its timer;
auto-play continues without further input.

| Key | Feature |
|---|---|
| `Home`, `T` | Thermal assist |
| `W` | Wind estimation |
| `N` | Competition navigation |
| `S` | Side view and glide range |
| `3` | 3D replay |
| `L` | Live tracking |
| `C` | Group voice |
| `R` | VHF bridge |
| `H` | Button on the brake line |
| `F` | Weather forecast |
| Strip button | Regional forecast |
| `G` | Ground contacts |
| `X` | Analyse your flight |
| `I` | Automatic activity segments |
| `A` | AreaContest |
| `End`, `O` | Works without coverage |

`Esc` opens the overview. Type a slide number followed by `Enter` to jump.
A lone `3` waits 0.6 seconds before opening 3D replay, allowing `3` plus
`Enter` to mean slide number 3 instead.

## Rebuild

Edit the `SLIDES` list in `build.py`, then run from the blog checkout:

```sh
uv run pgpilot/coupe-kiosk/build.py
```

The builder stages H264 clips and posters, writes `slides.js`, and mirrors the
runtime into **this checkout's** `docs/pgpilot/coupe-kiosk/`. Source recordings
are named explicitly. A missing source fails the build; rejected recordings
are not fallbacks. `NOTES.md` records the selected footage and its provenance.

The source folder's `video/` is a local encoding cache, not tracked in git.
The published `docs/` videos are tracked. Use the published folder, not the
source folder, when running a fresh clone without rebuilding.

For an HTTP preview with working video seeking, serve the published folder
with `uv run --no-project --with rangehttpserver python -m RangeHTTPServer`.
A plain Python HTTP server does not provide the required byte-range support.

After changing deployed scripts, styles or the slide manifest, bump their
`v` query in `index.html` so a previous kiosk cut cannot remain in cache.
Verify the actual browser surface, including edge readouts and the full loop.

## Presentation rules

- Show the feature, not an explanation of its implementation.
- Keep app captures bright and uncropped. Never add synthetic feature HUDs.
- Put titles in the app header band when bottom overlays would cover readouts.
- Keep the activity edit's complete aspect ratio and chart labels.
- Regional forecast is marked **Coming soon**.
- Tracking distinguishes internet updates from direct radio off-grid.
- No static leaderboard masquerading as live standings.

The QR targets are `https://pgpilot.app` and `https://pgpilot.app/coupe`.
