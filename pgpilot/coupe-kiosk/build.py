#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Build the media for the Coupe Icare kiosk deck.

Copies and re-encodes every source clip into video/, every still into img/,
extracts a poster jpg per clip, and writes slides.js, which is the slide list
index.html renders. Re-run it whenever a new recording lands in
RECORDED_DIR: a slide picks the recorded landscape clip if it is there and
falls back to an existing portrait clip or still if it is not.

    ./build.py            (or: uv run build.py)

Nothing here touches git, and nothing is downloaded. ffmpeg is used through
its stderr only, because this box has no ffprobe.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
VIDEO_OUT = HERE / "video"
IMG_OUT = HERE / "img"
SLIDES_JS = HERE / "slides.js"

FFMPEG = Path.home() / ".local" / "bin" / "ffmpeg"

VOSS_VIDEO = Path("/home/simen/blog/pgpilot/voss-video")
VOSS_IMG = Path("/home/simen/blog/pgpilot/img")
SOCIAL = Path("/home/simen/social-review")
# Where the landscape 1920x1080 screen recordings land.
RECORDED = Path("/home/simen/.claude/jobs/eeb1fb3a/tmp/kiosk-clips")
# Pre-cropped captures and the rendered hodograph clip for the "It learns
# from your flying" run. crops.py and hodograph/make.py in there rebuild them
# from the poster sources; see NOTES.md.
ALGO = Path("/home/simen/.claude/jobs/eeb1fb3a/tmp/algo")

MAX_EDGE = 1920
CRF = "20"
PRESET = "fast"

# The mirror the blog actually publishes. Quarto is not installed on this box,
# so the built page is copied into docs/ by hand.
MIRROR = Path("/home/simen/blog/docs/pgpilot/coupe-kiosk")


# --------------------------------------------------------------------------
# slide spec
# --------------------------------------------------------------------------


@dataclass
class Slide:
    """One slide.

    ``wide`` is the landscape recording this slide wants. If it is missing,
    ``fallback`` decides what the slide becomes instead: a phone slide with a
    portrait clip, a wide slide with an older landscape clip, or a still.
    """

    id: str
    label: str  # short name for the hotkey strip, "" to share the one before
    title: str  # feature name, big, Bevan
    lines: list[str]
    dur: int  # seconds on screen
    key: str | None = None  # hotkey, "" for none
    wide: str | None = None  # filename expected in RECORDED
    fallback: dict = field(default_factory=dict)
    layout: str | None = None  # forced layout, otherwise "wide"
    media: str | None = None  # forced media source path
    media_fallback: str | None = None  # used if media is not on disk yet
    images: list[str] = field(default_factory=list)
    qr: str | None = None  # extra QR on the slide itself
    footnote: str | None = None
    corner_qr: bool = True
    dim: bool = False  # push a light still back behind the words
    card: str = "bottom"  # where the title card sits on a wide slide
    scrim: bool = True  # the dark wash under the card on a wide slide
    card_max: int | None = None  # narrow the card to leave room in the frame
    kb: str = "in"  # Ken Burns direction: in, out, pan, zoom, big
    kb_video: bool = False  # let the push run on a clip too, not just a still
    kb_origin: str | None = None  # what the push aims at, "38% 50%"
    kb_seq: list[str] = field(default_factory=list)  # per image, seq layout
    kb_origin_seq: list[str] = field(default_factory=list)
    eyebrow: str | None = None  # section slides only
    stats_label: str | None = None
    stats: list[list[str]] = field(default_factory=list)  # [value, caption]


SLIDES: list[Slide] = [
    Slide(
        id="home",
        label="Home",
        key="Home",
        title="All you need in one flight app",
        lines=["iOS and Android"],
        dur=15,
        layout="title",
        media=str(VOSS_VIDEO / "bir-3d.mp4"),
    ),
    Slide(
        id="thermal",
        label="Thermal",
        key="T",
        title="Thermal assist",
        lines=[
            "The bubble is drawn where the lift was.",
            "The vario tells you how strong.",
        ],
        dur=20,
        wide="thermal-assist.mp4",
        fallback={"layout": "phone", "media": str(VOSS_VIDEO / "klipp-termikk.mp4")},
    ),
    Slide(
        id="wind",
        label="Wind",
        key="W",
        title="Wind estimation",
        lines=[
            "Learned from your own circles, no sensor needed.",
            "Updated every turn.",
        ],
        dur=18,
        wide="wind-estimation.mp4",
        fallback={"layout": "phone", "media": str(SOCIAL / "hook_S_gaggle_wind.mp4")},
    ),
    Slide(
        id="nav",
        label="Nav",
        key="N",
        title="Navigation",
        lines=[
            "Tasks, waypoints and a heading line.",
            "Competition start countdown, then glide to goal.",
        ],
        dur=18,
        wide="navigation.mp4",
        fallback={"layout": "wide", "media": str(VOSS_VIDEO / "hvor-er-bir.mp4")},
    ),
    Slide(
        id="sideview",
        label="Side",
        key="S",
        title="Side view and glide range",
        lines=[
            "Will you clear that ridge?",
            "Glide rays and range contours say so before you commit.",
        ],
        dur=20,
        wide="sideview-glide.mp4",
        card="top",
        # The card is at the top and the side view panel runs along the
        # bottom, which is exactly where the scrim would wash it out.
        scrim=False,
        fallback={"layout": "phone", "media": str(VOSS_VIDEO / "klipp-sideview.mp4")},
    ),
    Slide(
        id="replay",
        label="3D",
        key="3",
        title="3D replay",
        lines=[
            "Fly it again in 3D.",
            "Every flight, every thermal, every glide. With the pilots who were there.",
        ],
        dur=22,
        # The Sogndal gaggle in the phone, several pilots thermalling together,
        # with the landscape chase recording behind it.
        layout="phone",
        media=str(RECORDED / "gaggle-3d.mp4"),
        media_fallback=str(SOCIAL / "hook_S_gaggle_wind.mp4"),
        wide="replay-3d.mp4",
        fallback={},
    ),
    Slide(
        id="tracking",
        label="Track",
        key="L",
        title="Live tracking",
        lines=[
            "See your friends in the air, one position per second.",
            "Internet, FANET, OGN, FLARM, inReach and Meshtastic on one map.",
        ],
        dur=18,
        wide="live-tracking.mp4",
        fallback={"layout": "phone", "media": str(VOSS_VIDEO / "klipp-tracking.mp4")},
    ),
    Slide(
        id="comms",
        label="Comms",
        key="C",
        title="Group voice",
        lines=[
            "Push to talk to everyone in your group. No range limit.",
            "Voice messages are auto-transcribed on display.",
            "Hold the button on the brake line, hands stay on the brakes.",
        ],
        dur=20,
        wide="voice-groups.mp4",
        card="none",  # the clip carries its own title card
        scrim=False,
        fallback={"layout": "phone", "media": str(VOSS_IMG / "app-comms.png")},
    ),
    Slide(
        id="vhf",
        label="VHF",
        key="R",
        title="VHF bridge",
        lines=[
            "Radio pilots and app pilots in one conversation.",
            "No coverage? The radio still talks.",
        ],
        dur=20,
        wide="vhf-bridge.mp4",
        card="none",
        scrim=False,
        fallback={"layout": "phone", "media": str(VOSS_IMG / "app-hardware.png")},
    ),
    Slide(
        id="hardware",
        label="Button",
        key="H",
        title="Button on the brake line",
        lines=[
            "Hold to talk.",
            "Double tap to zoom in, triple tap to zoom out.",
            "Tap and hold for the voice assistant.",
        ],
        dur=20,
        layout="phone",
        media=str(VOSS_VIDEO / "klipp-knapp.mp4"),
    ),
    Slide(
        id="forecast",
        label="Forecast",
        key="F",
        title="Wind and forecast at the takeoff",
        lines=[
            "Wind stations with history, airgram forecast for the launch.",
            "Before you leave home.",
        ],
        dur=20,
        wide="forecast-airgram.mp4",
        kb="zoom",
        kb_video=True,
        fallback={
            "layout": "duo",
            "images": [
                str(VOSS_IMG / "app-bavallen-vind.jpg"),
                str(VOSS_IMG / "app-bavallen-airgram.jpg"),
            ],
        },
    ),
    Slide(
        id="regional",
        label="Regional",
        title="Regional forecast is on its way!",
        lines=[
            "Where will it work today? 1 226 regions across Europe,",
            "climb above local terrain.",
            "A research prototype, not yet in the app.",
        ],
        dur=20,
        layout="seq",
        images=[
            str(ALGO / "algo-regions-europe.png"),
            str(ALGO / "algo-regions-alps.png"),
        ],
        kb_seq=["in", "in"],
        # The Alpine arc in the Europe figure, then the region that holds
        # Saint-Hilaire in the Alpine one.
        kb_origin_seq=["46% 64%", "39% 50%"],
    ),
    Slide(
        id="contacts",
        label="Contacts",
        key="G",
        title="Ground contacts",
        lines=[
            "Your people get a message when you take off and when you land.",
            "SMS, email or push.",
        ],
        dur=22,
        wide="ground-contacts.mp4",
        fallback={"layout": "phone", "media": str(VOSS_VIDEO / "klipp-start.mp4")},
    ),
    Slide(
        id="flights",
        label="Analyse",
        key="X",
        title="Analyse your flight!",
        lines=[
            "Glides and thermals, your turn direction, the air you flew in.",
            "Temperature, lapse rate and wind from the VectorVario, on your flight.",
        ],
        dur=18,
        wide="analyse-flight.mp4",
        # Until the recording lands: the four-panel still, pushed hard enough
        # that it plainly moves. Same screenshot the slide always had, with
        # the peer name and the prose blurred out.
        fallback={
            "layout": "wide",
            "media": "/home/simen/.claude/jobs/eeb1fb3a/tmp/flightdetails-noname.jpg",
        },
        kb="big",
        dim=True,
    ),
    # ---------------------------------------------------------------- the
    # "It learns from your flying" run. Built from the A0 algorithms poster
    # that was dropped before print (brand/coupe-icare-2026/poster-air in the
    # pgpilot repo: HANDOFF.md, README.md's "Where every number comes from",
    # and the verified copy in poster.html). Every capture is pre-cropped by
    # ALGO/crops.py, which also blurs the two peer labels on the thermal
    # overlay, and the hodograph is rendered by ALGO/hodograph/make.py.
    # Only the first slide carries a strip label: the six share one entry,
    # because the strip is one row of 1920 px and was already full.
    Slide(
        id="learns",
        label="Learns",
        key="I",
        title="It learns from your flying",
        lines=["Wind, thermals and forecasts, estimated from your flights."],
        dur=20,
        layout="section",
        eyebrow="Under the hood",
        media=str(ALGO / "algo-thermal-wide.png"),
        kb="out",
        stats_label="Measured against",
        stats=[
            ["9", "flights with pitot wind"],
            ["613", "hand-labelled thermals"],
            ["194", "hand-labelled recordings"],
            ["894 280", "flights behind the regions"],
        ],
    ),
    Slide(
        id="hodograph",
        label="",
        title="Wind from your circles",
        lines=[
            "Each circle is fitted in velocity space. The centre is the wind,",
            "the radius your airspeed. A Kalman filter fuses the fits.",
        ],
        dur=20,
        layout="wide",
        # 20 s, rendered frame by frame from the 120 GPS velocity vectors in
        # the poster's hodograph.json. The card is narrowed so it cannot sit
        # on the circle.
        media=str(ALGO / "hodograph-wind.mp4"),
        card_max=780,
        scrim=False,
    ),
    Slide(
        id="core",
        label="",
        title="Where the lift is",
        lines=[
            "A lift and recency weighted centre of the last two minutes,",
            "drifted with the wind.",
        ],
        dur=18,
        layout="wide",
        media=str(ALGO / "algo-thermal-core.png"),
        kb_origin="51% 54%",  # the core ring
    ),
    Slide(
        id="pinned",
        label="",
        title="Every flight keeps its forecast",
        lines=[
            "The forecast it was flown on, kept as it stood that morning.",
            "Hvittingfoss, 13 September, the ICON-EU 05:00 run.",
        ],
        dur=20,
        layout="duo",
        # Forecast first, flown trace second: the corner QR sits over the
        # right cell's top corner, and the chart has nothing up there to lose.
        images=[
            str(ALGO / "algo-flight-pinned.png"),
            str(ALGO / "algo-flight-flown.png"),
        ],
    ),
    Slide(
        id="segments",
        label="",
        title="Hike, ground, fly",
        lines=[
            "One recording, several activities: hike, ground, fly.",
            "A Viterbi decode over random forest costs.",
            "Learned from 194 hand-labelled recordings.",
        ],
        dur=18,
        layout="phone",
        media=str(ALGO / "algo-hike-phone.png"),
    ),
    Slide(
        id="areacontest",
        label="Area",
        key="A",
        title="AreaContest",
        lines=[
            "Fly around an area to claim it.",
            "Whoever has the biggest claim rules it.",
        ],
        dur=25,
        layout="phone",
        media=str(SOCIAL / "coupe_whale_v8.mp4"),
        # The landscape recording, if it lands, becomes the moving backdrop
        # behind the phone instead of a blurred still.
        wide="areacontest-whale.mp4",
        fallback={},
        qr="coupe",
        footnote=(
            "This week: the whale over Saint-Hilaire. "
            "Biggest claim on Sunday 13:00 wins."
        ),
    ),
    Slide(
        id="board",
        label="Board",
        title="The whale, right now",
        lines=[
            "The real board, scored every hour this week. Everyone on pgpilot is already in."
        ],
        dur=21,
        wide="areacontest-whale.mp4",
        fallback={"layout": "phone", "media": str(SOCIAL / "coupe_whale_v8.mp4")},
        qr="coupe",
    ),
    Slide(
        id="offline",
        label="Offline",
        key="O",
        title="Works without coverage",
        lines=[
            "Maps, terrain and instruments offline.",
            "Backcountry ready.",
        ],
        dur=18,
        layout="phone",
        media=str(VOSS_VIDEO / "klipp-backcountry.mp4"),
    ),
    Slide(
        id="try",
        label="Try it",
        key=None,
        title="Try it now",
        lines=["Ask us at the stand"],
        dur=20,
        layout="closing",
        media=str(VOSS_VIDEO / "bir-3d.mp4"),
        qr="pgpilot",
        corner_qr=False,
    ),
]


# --------------------------------------------------------------------------
# ffmpeg helpers
# --------------------------------------------------------------------------


def probe(path: Path) -> tuple[float, int, int]:
    """Duration in seconds plus width and height, read off ffmpeg's stderr."""
    out = subprocess.run(
        [str(FFMPEG), "-i", str(path)], capture_output=True, text=True, check=False
    ).stderr
    dur = 0.0
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", out)
    if m:
        dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    w = h = 0
    m = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", out)
    if m:
        w, h = int(m[1]), int(m[2])
    return dur, w, h


def encode_video(src: Path, dst: Path) -> None:
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        print(f"  video  {dst.name:<28} up to date")
        return
    print(f"  video  {dst.name:<28} encoding from {src}")
    subprocess.run(
        [
            str(FFMPEG),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(src),
            "-an",
            "-vf",
            # Cap the long edge, never upscale: force_original_aspect_ratio on
            # a plain 1920x1920 box happily blows a 780x1688 phone recording up
            # to 886x1920 and triples the file for nothing.
            (
                f"scale='min({MAX_EDGE},iw)':'min({MAX_EDGE},ih)'"
                ":force_original_aspect_ratio=decrease,"
                "scale=trunc(iw/2)*2:trunc(ih/2)*2"
            ),
            "-c:v",
            "libx264",
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            CRF,
            "-preset",
            PRESET,
            "-movflags",
            "+faststart",
            str(dst),
        ],
        check=True,
    )


def extract_poster(video: Path, dst: Path, dur: float) -> None:
    if dst.exists() and dst.stat().st_mtime >= video.stat().st_mtime:
        print(f"  poster {dst.name:<28} up to date")
        return
    at = max(0.1, dur * 0.35)
    print(f"  poster {dst.name:<28} at {at:.1f}s")
    subprocess.run(
        [
            str(FFMPEG),
            "-y",
            "-loglevel",
            "error",
            "-ss",
            f"{at:.2f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "3",
            str(dst),
        ],
        check=True,
    )


def readable(p: Path) -> bool:
    """Does this still actually decode all the way to the bottom?

    This box runs out of disk regularly. A save that dies half way leaves a
    file that is newer than its source, so every later build skips it, and the
    deck shows a picture that stops in a hard line two thirds down. Cost is one
    decode per still per build; worth it.
    """
    try:
        with Image.open(p) as im:
            im.load()
    except Exception:  # noqa: BLE001 - any decode failure means re-stage it
        return False
    return True


def copy_still(src: Path, dst: Path) -> None:
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        if readable(dst):
            print(f"  still  {dst.name:<28} up to date")
            return
        print(f"  still  {dst.name:<28} truncated, re-staging")
    with Image.open(src) as im:
        if max(im.size) > MAX_EDGE:
            scale = MAX_EDGE / max(im.size)
            im = im.resize(
                (round(im.width * scale), round(im.height * scale)),
                Image.LANCZOS,
            )
        if dst.suffix.lower() in {".jpg", ".jpeg"} and im.mode != "RGB":
            im = im.convert("RGB")
        im.save(dst, quality=88)
    print(f"  still  {dst.name:<28} {src}")


# --------------------------------------------------------------------------
# resolve + stage
# --------------------------------------------------------------------------


def stage_video(src: Path) -> dict:
    """Encode a clip into video/, extract its poster, return the web paths."""
    dst = VIDEO_OUT / src.name
    encode_video(src, dst)
    dur, w, h = probe(dst)
    poster = IMG_OUT / f"poster-{src.stem}.jpg"
    extract_poster(dst, poster, dur)
    return {
        "type": "video",
        "src": f"video/{dst.name}",
        "poster": f"img/{poster.name}",
        "dur": round(dur, 2),
        "w": w,
        "h": h,
    }


def stage_image(src: Path) -> dict:
    dst = IMG_OUT / src.name
    copy_still(src, dst)
    with Image.open(dst) as im:
        w, h = im.size
    return {
        "type": "image",
        "src": f"img/{dst.name}",
        "poster": f"img/{dst.name}",
        "w": w,
        "h": h,
    }


def stage(src: Path) -> dict:
    return (
        stage_image(src)
        if src.suffix.lower() in {".jpg", ".jpeg", ".png"}
        else stage_video(src)
    )


def main() -> int:
    if not FFMPEG.exists():
        print(f"ffmpeg not found at {FFMPEG}", file=sys.stderr)
        return 1
    VIDEO_OUT.mkdir(exist_ok=True)
    IMG_OUT.mkdir(exist_ok=True)

    missing: list[tuple[str, str]] = []
    found: list[tuple[str, str]] = []
    out: list[dict] = []

    for s in SLIDES:
        print(f"[{s.id}] {s.title}")
        layout = s.layout or "wide"
        media_src: Path | None = Path(s.media) if s.media else None
        images = [Path(p) for p in s.images]
        bg_src: Path | None = None

        recorded = RECORDED / s.wide if s.wide else None
        if recorded and recorded.exists():
            found.append((s.id, s.wide))
            if s.layout == "phone":
                # The recording is the moving backdrop, the phone keeps its reel.
                bg_src = recorded
            else:
                layout = "wide"
                media_src = recorded
        else:
            if s.wide:
                missing.append((s.id, s.wide))
            if s.fallback:
                layout = s.fallback.get("layout", layout)
                if s.fallback.get("media"):
                    media_src = Path(s.fallback["media"])
                if s.fallback.get("images"):
                    images = [Path(p) for p in s.fallback["images"]]

        # A slide can also name a clip that is still being made. Same idea as
        # ``wide``, but for the piece the layout is built around rather than
        # the backdrop.
        if media_src and not media_src.exists() and s.media_fallback:
            missing.append((s.id, media_src.name))
            print(f"  !!     {media_src.name} not here yet, using {s.media_fallback}")
            media_src = Path(s.media_fallback)

        entry: dict = {
            "id": s.id,
            "label": s.label,
            "key": s.key,
            "layout": layout,
            "title": s.title,
            "lines": s.lines,
            "dur": s.dur,
            "qr": s.qr,
            "footnote": s.footnote,
            "cornerQr": s.corner_qr,
            "dim": s.dim,
            "card": s.card,
            "scrim": s.scrim,
            "cardMax": s.card_max,
            "kb": s.kb,
            "kbVideo": s.kb_video,
            "kbOrigin": s.kb_origin,
            "kbSeq": s.kb_seq,
            "kbOriginSeq": s.kb_origin_seq,
            "eyebrow": s.eyebrow,
            "statsLabel": s.stats_label,
            "stats": s.stats,
        }
        if media_src:
            entry["media"] = stage(media_src)
        if images:
            entry["images"] = [stage(p) for p in images]
        if bg_src:
            entry["bg"] = stage(bg_src)
        out.append(entry)

    SLIDES_JS.write_text(
        "// Generated by build.py. Edit the SLIDES spec there, not this file.\n"
        "window.KIOSK_SLIDES = " + json.dumps(out, indent=2) + ";\n"
    )
    print(f"\nwrote {SLIDES_JS}")

    if found:
        print("\nRecorded clips in use:")
        for sid, name in found:
            print(f"  {name:<24} -> slide {sid}")
    if missing:
        print("\nMISSING recordings (slide fell back to an older clip or still):")
        for sid, name in missing:
            print(f"  {RECORDED / name}   -> slide {sid}")
        print("\nDrop them in and re-run this script to pick them up.")
    else:
        print("\nAll recordings present.")

    if MIRROR.parent.exists():
        mirror()
    return 0


def mirror() -> None:
    """Copy the whole deck into the published docs/ tree."""
    MIRROR.mkdir(parents=True, exist_ok=True)
    for name in (
        "index.html",
        "kiosk.css",
        "kiosk.js",
        "slides.js",
        "README.md",
        "NOTES.md",
    ):
        p = HERE / name
        if p.exists():
            shutil.copy2(p, MIRROR / name)
    for sub in ("reveal", "fonts", "img", "video"):
        src = HERE / sub
        if not src.exists():
            continue
        dst = MIRROR / sub
        dst.mkdir(exist_ok=True)
        for f in src.iterdir():
            if not f.is_file():
                continue
            out = dst / f.name
            stale = not out.exists() or out.stat().st_mtime < f.stat().st_mtime
            # Same trap as copy_still: a copy that ran out of disk leaves a
            # short file with a fresh mtime, which then looks up to date.
            if stale or out.stat().st_size != f.stat().st_size:
                shutil.copy2(f, out)
    print(f"mirrored into {MIRROR}")


if __name__ == "__main__":
    raise SystemExit(main())
