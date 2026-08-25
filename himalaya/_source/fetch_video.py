"""Hent og transkod videoene som hører til foredraget.

Kildefilene ligger i Google Drive (de var innebygd i den opprinnelige
Google Slides-presentasjonen). Originalene er ~2,3 GB til sammen, så vi
skalerer ned til 1280px / CRF 28, som gir ~120 MB - bra nok for projektor.

Kjør fra himalaya/:
    python3 _source/fetch_video.py

Krever `gws` innlogget mot kontoen som eier Drive-filene.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VID = ROOT / "video"
RAW = HERE / "video-raw"

VID.mkdir(exist_ok=True)
RAW.mkdir(exist_ok=True)

slides = json.loads((HERE / "slides.json").read_text())
videos = [
    (sl["n"], el["vid"])
    for sl in slides["slides"]
    for el in sl["elements"]
    if el["kind"] == "video"
]

for n, drive_id in videos:
    out = VID / f"slide{n:02d}.mp4"
    if out.exists() and out.stat().st_size > 0:
        print("finnes allerede:", out.name)
        continue

    raw = RAW / f"{drive_id}.bin"
    if not (raw.exists() and raw.stat().st_size > 0):
        print(f"laster ned slide {n} ({drive_id})", flush=True)
        subprocess.run(
            ["gws", "drive", "files", "get", "--params",
             json.dumps({"fileId": drive_id, "alt": "media"}), "--output", str(raw)],
            capture_output=True, text=True,
        )
        if not raw.exists() or raw.stat().st_size == 0:
            print(f"  FEILET - hoppet over slide {n}", flush=True)
            continue

    print(f"transkoder slide {n} ({raw.stat().st_size / 1e6:.0f} MB)", flush=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
         "-vf", "scale='min(1280,iw)':-2",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
         "-movflags", "+faststart", "-c:a", "aac", "-b:a", "96k",
         str(out)],
        check=False,
    )
    if out.exists() and out.stat().st_size > 0:
        raw.unlink()
        print(f"  -> {out.name} ({out.stat().st_size / 1e6:.1f} MB)", flush=True)

print("ferdig")
