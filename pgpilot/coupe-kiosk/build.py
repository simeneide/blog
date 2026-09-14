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
    label: str  # short name for the hotkey strip
    title: str  # feature name, big, Bevan
    lines: list[str]
    dur: int  # seconds on screen
    key: str | None = None  # hotkey, "" for none
    wide: str | None = None  # filename expected in RECORDED
    fallback: dict = field(default_factory=dict)
    layout: str | None = None  # forced layout, otherwise "wide"
    media: str | None = None  # forced media source path
    images: list[str] = field(default_factory=list)
    qr: str | None = None  # extra QR on the slide itself
    footnote: str | None = None
    corner_qr: bool = True
    dim: bool = False  # push a light still back behind the words
    card: str = "bottom"  # where the title card sits on a wide slide


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
            "Glide to goal on the map.",
        ],
        dur=18,
        wide="navigation.mp4",
        fallback={"layout": "wide", "media": str(VOSS_VIDEO / "hvor-er-bir.mp4")},
    ),
    Slide(
        id="sideview",
        label="Side view",
        key="S",
        title="Side view and glide range",
        lines=[
            "Will you clear that ridge?",
            "Glide rays and range contours say so before you commit.",
        ],
        dur=20,
        wide="sideview-glide.mp4",
        card="top",
        fallback={"layout": "phone", "media": str(VOSS_VIDEO / "klipp-sideview.mp4")},
    ),
    Slide(
        id="replay",
        label="3D",
        key="3",
        title="3D replay",
        lines=[
            "Fly it again in 3D.",
            "Every flight, every thermal, every glide.",
        ],
        dur=22,
        # The Instagram whale reel's 3D opening (the same shot without the
        # text cards) in the phone, the landscape chase recording behind it.
        layout="phone",
        media="/home/simen/.claude/jobs/eeb1fb3a/tmp/kiosk-clips/replay-3d-phone.mp4",
        wide="replay-3d.mp4",
        fallback={},
    ),
    Slide(
        id="tracking",
        label="Tracking",
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
            "Hold the button on the brake line, hands stay on the brakes.",
        ],
        dur=20,
        wide="voice-groups.mp4",
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
        fallback={"layout": "phone", "media": str(VOSS_IMG / "app-hardware.png")},
    ),
    Slide(
        id="hardware",
        label="Hardware",
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
        fallback={
            "layout": "duo",
            "images": [
                str(VOSS_IMG / "app-bavallen-vind.jpg"),
                str(VOSS_IMG / "app-bavallen-airgram.jpg"),
            ],
        },
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
        label="Flights",
        key="X",
        title="Your flights, synced",
        lines=[
            "XContest and Flightlog sync, IGC export,",
            "segments split automatically.",
        ],
        dur=18,
        layout="wide",
        media=str(VOSS_IMG / "app-flightdetails.jpg"),
        dim=True,
    ),
    Slide(
        id="areacontest",
        label="AreaContest",
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


def copy_still(src: Path, dst: Path) -> None:
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        print(f"  still  {dst.name:<28} up to date")
        return
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
            if f.is_file() and (
                not (dst / f.name).exists()
                or (dst / f.name).stat().st_mtime < f.stat().st_mtime
            ):
                shutil.copy2(f, dst / f.name)
    print(f"mirrored into {MIRROR}")


if __name__ == "__main__":
    raise SystemExit(main())
