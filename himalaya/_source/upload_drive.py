"""Last videoklippene opp til eide.ai-kontoen sin Drive og gjoer dem offentlige.

Klippene ligger utenfor git (~120 MB), saa den publiserte versjonen av decket
maa hente dem et annet sted. De originale filene laa i Drive, men under
simeneide@gmail.com og dagfinngra@gmail.com, som denne kontoen bare har
lesetilgang til. Her lastes de nedskalerte kopiene opp paa nytt under
simen@eide.ai, der vi faktisk kan styre delingen.

Skriver _source/drive-videos.json: {slidenummer: fil-id}.
Kjoer fra himalaya/:  python3 _source/upload_drive.py
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FOLDER = "1BoeJeNZv9mjlVd5gLZDw9UqO9akfgcq9"
OUT = HERE / "drive-videos.json"

# Originalnavnene, saa filene er gjenkjennelige i Drive.
NAMES = {
    9: "volbiv", 17: "paa toppen av foerste bak", 22: "foelge ryggen over til manali",
    32: "shikah beh", 33: "fly ut mellom skyene", 39: "volbiv opp fra foerste rygg bak",
    40: "start mot shikah beh", 41: "regn", 42: "oern flyr rett forbi",
    43: "over shikah beh", 44: "over til bara bhangal", 45: "ettermiddagsskyer",
    48: "kjoere mot sky", 50: "tandoori",
}


def gws(args: list[str]) -> dict:
    r = subprocess.run(["gws"] + args, capture_output=True, text=True)
    out = r.stdout
    if out.startswith("Using keyring"):
        out = out.split("\n", 1)[-1]
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise SystemExit(f"gws feilet: {out[:300]} {r.stderr[:300]}")


ids: dict[str, str] = json.loads(OUT.read_text()) if OUT.exists() else {}

for n, label in sorted(NAMES.items()):
    key = str(n)
    if key in ids:
        print(f"slide {n:>2} finnes allerede: {ids[key]}")
        continue
    src = ROOT / "video" / f"slide{n:02d}.mp4"
    if not src.exists():
        print(f"slide {n:>2} MANGLER lokalt - hopper over")
        continue

    print(f"slide {n:>2} laster opp {src.stat().st_size / 1e6:.1f} MB ...", flush=True)
    created = gws([
        "drive", "files", "create",
        "--upload", str(src), "--upload-content-type", "video/mp4",
        "--json", json.dumps({"name": f"slide{n:02d} - {label}.mp4", "parents": [FOLDER]}),
        "--params", json.dumps({"fields": "id,name,size"}),
    ])
    fid = created["id"]

    gws([
        "drive", "permissions", "create",
        "--params", json.dumps({"fileId": fid, "fields": "id,type,role"}),
        "--json", json.dumps({"role": "reader", "type": "anyone"}),
    ])

    ids[key] = fid
    OUT.write_text(json.dumps(ids, indent=1, sort_keys=True))
    print(f"          -> {fid} (offentlig)", flush=True)

print(f"ferdig: {len(ids)} av {len(NAMES)} klipp i Drive")
