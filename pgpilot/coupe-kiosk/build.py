#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Build the media for the Coupe Icare kiosk deck.

Copies and re-encodes the selected clips into video/, the regional forecast
figures into img/, extracts posters and writes slides.js. Missing sources
fail the build rather than restoring a rejected recording.

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
# New captures are separate from the previous cut, so rejected takes cannot
# silently become fallbacks.
REVISED = RECORDED.parent / "kiosk-revision"
REFINEMENTS = REVISED / "refinements"
# Regional forecast figures.
ALGO = Path("/home/simen/.claude/jobs/eeb1fb3a/tmp/algo")

MAX_EDGE = 1920
CRF = "20"
PRESET = "fast"

# The mirror the blog actually publishes. Quarto is not installed on this box,
# so the built page is copied into docs/ by hand.
MIRROR = HERE.parents[1] / "docs" / "pgpilot" / "coupe-kiosk"


# --------------------------------------------------------------------------
# slide spec
# --------------------------------------------------------------------------


@dataclass
class Slide:
    """One feature and its selected recording or regional forecast figures."""

    id: str
    label: str  # short name for the hotkey strip, "" to share the one before
    title: str  # feature name, big, Bevan
    lines: list[str]
    dur: float  # seconds on screen
    key: str | None = None  # hotkey, "" for none
    layout: str = "wide"
    media: str | None = None
    images: list[str] = field(default_factory=list)
    qr: str | None = None  # extra QR on the slide itself
    corner_qr: str | bool = "top"  # "top", "low" (under a card in the clip), False
    card: str = "bottom"  # where the title card sits on a wide slide
    scrim: bool = False  # keep the app bright; the title has its own backing
    kb: str = "in"  # Ken Burns direction: in, out, pan, zoom, big
    kb_seq: list[str] = field(default_factory=list)  # per image, seq layout
    kb_origin_seq: list[str] = field(default_factory=list)


SLIDES: list[Slide] = [
    Slide(
        id="thermal",
        label="Thermal",
        key="T",
        title="Thermal assist",
        lines=[],
        dur=18,
        media=str(REVISED / "thermalwind/thermal-deadband.mp4"),
        card="header",
    ),
    Slide(
        id="wind",
        label="Wind",
        key="W",
        title="Wind estimation",
        lines=[],
        dur=20,
        media=str(REFINEMENTS / "wind/wind-changing.mp4"),
        card="header",
    ),
    Slide(
        id="nav",
        label="Nav",
        key="N",
        title="Competition navigation",
        lines=[],
        dur=25,
        media=str(REFINEMENTS / "navigation/navigation-extended.mp4"),
        card="header",
    ),
    Slide(
        id="sideview",
        label="Glide",
        key="S",
        title="Side view and glide range",
        lines=[],
        dur=19,
        media=str(REFINEMENTS / "navigation/sideview-companions.mp4"),
        card="header",
    ),
    Slide(
        id="replay",
        label="3D",
        key="3",
        title="3D replay",
        lines=[],
        dur=12,
        media=str(REFINEMENTS / "editorial/glacier-faster.mp4"),
    ),
    Slide(
        id="tracking",
        label="Track",
        key="L",
        title="Live tracking",
        lines=[
            "Every second online. Direct radio off-grid.",
            "Online: OGN, PureTrack, XContest, SafeSky.",
            "Off-grid: FLARM, FANET, Meshtastic, inReach.",
        ],
        dur=14,
        layout="phone",
        media=str(VOSS_VIDEO / "klipp-tracking.mp4"),
    ),
    Slide(
        id="comms",
        label="Voice",
        key="C",
        title="Group voice",
        lines=[],
        dur=9,
        media=str(REVISED / "editorial/voice-simple.mp4"),
        card="top",
    ),
    Slide(
        id="vhf",
        label="VHF",
        key="R",
        title="VHF bridge",
        lines=[],
        dur=9,
        media=str(REVISED / "editorial/vhf-simple.mp4"),
        card="top",
    ),
    Slide(
        id="hardware",
        label="Button",
        key="H",
        title="Button on the brake line",
        lines=["Double and triple click for zoom in/out"],
        dur=14,
        layout="phone",
        media=str(VOSS_VIDEO / "klipp-knapp.mp4"),
    ),
    Slide(
        id="wind-history",
        label="History",
        title="See historical wind and compare to actual observed wind",
        lines=[],
        dur=20,
        media=str(REVISED / "analysisweather/weather-comparison.mp4"),
        card="header",
    ),
    Slide(
        id="forecast",
        label="Weather",
        key="F",
        title="Weather forecast",
        lines=[],
        dur=20,
        media=str(REFINEMENTS / "weather/airgram-forecast-clear.mp4"),
        card="header",
    ),
    Slide(
        id="regional",
        label="Regional",
        title="Regional forecast",
        lines=["Coming soon."],
        dur=14,
        layout="seq",
        images=[
            str(ALGO / "algo-regions-europe.png"),
            str(ALGO / "algo-regions-alps.png"),
        ],
        kb_seq=["in", "in"],
        kb_origin_seq=["46% 64%", "39% 50%"],
    ),
    Slide(
        id="contacts",
        label="Contacts",
        key="G",
        title="Ground contacts",
        lines=["Makes sure people at home knows where you are"],
        dur=17.2,
        media=str(REVISED / "editorial/contacts-simple.mp4"),
        corner_qr="low",  # the notification card sits where the panel goes
    ),
    Slide(
        id="flights",
        label="Analyse",
        key="X",
        title="Analyse your flight",
        lines=[
            (
                "See thermals, glides, turn rates, temperatures, "
                "the day's weather forecast and more."
            )
        ],
        dur=24,
        media=str(REVISED / "analysisweather/analyse-large.mp4"),
        card="header",
    ),
    Slide(
        id="segments",
        label="Activities",
        key="I",
        title="Automatic activity segments",
        lines=[],
        dur=17.4,
        layout="phone",
        media=str(REVISED / "editorial/activity-segments.mp4"),
    ),
    Slide(
        id="areacontest",
        label="Area",
        key="A",
        title="AreaContest",
        lines=[],
        dur=20,
        layout="phone",
        media=str(SOCIAL / "coupe_whale_v8.mp4"),
        qr="coupe",
    ),
    Slide(
        id="offline",
        label="Offline",
        key="O",
        title="Works without coverage",
        lines=["VHF directly in app", "FANET + inReach tracking"],
        dur=14,
        layout="phone",
        media=str(VOSS_VIDEO / "klipp-backcountry.mp4"),
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

    out: list[dict] = []

    for s in SLIDES:
        print(f"[{s.id}] {s.title}")
        entry: dict = {
            "id": s.id,
            "label": s.label,
            "key": s.key,
            "layout": s.layout,
            "title": s.title,
            "lines": s.lines,
            "dur": s.dur,
            "qr": s.qr,
            "cornerQr": s.corner_qr,
            "card": s.card,
            "scrim": s.scrim,
            "kb": s.kb,
            "kbSeq": s.kb_seq,
            "kbOriginSeq": s.kb_origin_seq,
        }
        if s.media:
            entry["media"] = stage(Path(s.media))
        if s.images:
            entry["images"] = [stage(Path(p)) for p in s.images]
        out.append(entry)

    SLIDES_JS.write_text(
        "// Generated by build.py. Edit the SLIDES spec there, not this file.\n"
        "window.KIOSK_SLIDES = " + json.dumps(out, indent=2) + ";\n"
    )
    print(f"\nwrote {SLIDES_JS}")

    print(f"\n{len(SLIDES)} slides, {sum(s.dur for s in SLIDES)} seconds per loop.")

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
