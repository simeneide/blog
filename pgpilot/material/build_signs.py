"""Build the A4 direction signs: the pgpilot logo over one large arrow.

Run from the blog repo root with:
    uv run --no-project --with cairosvg python pgpilot/material/build_signs.py

No text besides the logo, so the signs need no font and work for any event.
"""

from __future__ import annotations

import re
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "pgpilot" / "material" / "files"
DESTINATIONS = (
    ROOT / "pgpilot" / "material" / "files",
    ROOT / "docs" / "pgpilot" / "material" / "files",
)
BLUE = "#0284c7"
ROTATIONS = {"right": 0, "up": -90, "left": 180}


def sign(rotation: int) -> str:
    logo = (SOURCE / "pgpilot-horizontal-sky-navy.svg").read_text()
    view_box = re.search(r'viewBox="([^"]+)"', logo).group(1)
    inner = re.sub(r"^<svg\b[^>]*>|</svg>\s*$", "", logo.strip())
    # A right-pointing arrow centred on the origin, 170 mm long, 150 mm high.
    arrow = "-85,-25 10,-25 10,-75 85,0 10,75 10,25 -85,25"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'
        '<rect width="210" height="297" fill="#ffffff"/>'
        f'<svg x="30" y="22" width="150" height="51.4" viewBox="{view_box}">{inner}</svg>'
        f'<polygon transform="translate(105 188) rotate({rotation})" points="{arrow}" '
        f'fill="{BLUE}" stroke="{BLUE}" stroke-width="8" stroke-linejoin="round"/>'
        "</svg>"
    )


for direction, rotation in ROTATIONS.items():
    svg = sign(rotation)
    stem = f"pgpilot-sign-A4-{direction}"
    for out in DESTINATIONS:
        (out / f"{stem}.svg").write_text(svg)
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(out / f"{stem}.pdf"))
        cairosvg.svg2png(
            bytestring=svg.encode(),
            write_to=str(out / f"{stem}.png"),
            output_width=1240,
        )
