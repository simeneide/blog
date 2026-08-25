"""Bygg videoklippene paa nytt i full opploesning og bytt dem ut i Drive.

Foerste runde skalerte til 1280px for aa spare plass. Originalene er
2336x1080 HEVC, saa det var et reelt tap - og decket skal paa storskjerm.
Her hentes originalene paa nytt og enkodes til H.264 med full hoeyde
(taket paa 1080 rammer bare eventuelle 4K-kilder) og CRF 20.

H.264 og ikke HEVC fordi nettlesere haandterer HEVC ujevnt, og decket skal
spille bade lokalt og i Drive sin spiller.

Drive-filene oppdateres med `files update`, som beholder fil-id og dermed
delingen, saa data-embed i decket ikke maa roeres.

Kjoer fra himalaya/:  python3 _source/rebuild_hq.py
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VID = ROOT / "video"
RAW = HERE / "video-raw"
RAW.mkdir(exist_ok=True)

slides = json.loads((HERE / "slides.json").read_text())
SOURCE = {sl["n"]: el["vid"] for sl in slides["slides"] for el in sl["elements"] if el["kind"] == "video"}
DRIVE = json.loads((HERE / "drive-videos.json").read_text())
DONE = HERE / "hq-done.json"
done = json.loads(DONE.read_text()) if DONE.exists() else []


def gws(args: list[str]) -> str:
    r = subprocess.run(["gws"] + args, capture_output=True, text=True)
    return r.stdout


for n in sorted(SOURCE):
    if n in done:
        print(f"slide {n:>2} allerede ferdig")
        continue

    raw = RAW / f"src{n:02d}.bin"
    if not (raw.exists() and raw.stat().st_size > 0):
        print(f"slide {n:>2} laster ned original ...", flush=True)
        gws(["drive", "files", "get", "--params",
             json.dumps({"fileId": SOURCE[n], "alt": "media"}), "--output", str(raw)])
        if not raw.exists() or raw.stat().st_size == 0:
            print(f"slide {n:>2} NEDLASTING FEILET"); continue

    out = VID / f"slide{n:02d}.mp4"
    tmp = VID / f"slide{n:02d}.hq.mp4"
    print(f"slide {n:>2} enkoder {raw.stat().st_size / 1e6:.0f} MB ...", flush=True)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
        "-vf", "scale=-2:'min(1080,ih)'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "160k", str(tmp),
    ], check=False)
    if not (tmp.exists() and tmp.stat().st_size > 0):
        print(f"slide {n:>2} ENKODING FEILET"); continue

    tmp.replace(out)
    raw.unlink()
    print(f"slide {n:>2} -> {out.stat().st_size / 1e6:.1f} MB, laster opp ...", flush=True)

    # files update beholder fil-id og delingen
    gws(["drive", "files", "update",
         "--params", json.dumps({"fileId": DRIVE[str(n)], "fields": "id,size"}),
         "--upload", str(out), "--upload-content-type", "video/mp4"])

    done.append(n)
    DONE.write_text(json.dumps(sorted(done)))
    print(f"slide {n:>2} ferdig", flush=True)

print(f"ferdig: {len(done)} av {len(SOURCE)}")
