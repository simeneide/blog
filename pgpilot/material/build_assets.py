"""Build the square pgpilot sticker and banner print files.

Run from the blog repo root with:
    uv run --no-project --with cairosvg --with qrcode --with fonttools python pgpilot/material/build_assets.py

The SVGs and PDFs use physical dimensions. Text and logos are vector paths;
the store QR codes point directly to the app listings.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import cairosvg
import qrcode
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "pgpilot" / "material" / "files"
DESTINATIONS = (
    ROOT / "pgpilot" / "material" / "files",
    ROOT / "docs" / "pgpilot" / "material" / "files",
)
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

APPLE = "https://apps.apple.com/no/app/id6759820116"
GOOGLE = "https://play.google.com/store/apps/details?id=com.pgfly.app"
NAVY = "#0f172a"
SKY = "#38bdf8"


def embedded_logo(name: str, *, x: float, y: float, width: float, height: float) -> str:
    source = (SOURCE / name).read_text()
    view_box = re.search(r'viewBox="([^"]+)"', source)
    if not view_box:
        raise ValueError(f"Missing viewBox in {name}")
    inner = re.sub(r"^<svg\b[^>]*>", "", source, count=1)
    inner = re.sub(r"</svg>\s*$", "", inner)
    return (
        f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
        f'viewBox="{view_box.group(1)}">{inner}</svg>'
    )


def font_text(
    value: str, *, center_x: float, baseline_y: float, size: float, color: str
) -> str:
    """Return outlined DejaVu glyphs, centered at center_x."""
    font = TTFont(FONT_PATH)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    advances = font["hmtx"].metrics
    glyph_names = [cmap[ord(char)] for char in value]
    total_width = sum(advances[name][0] for name in glyph_names) * scale
    cursor = -total_width / 2
    parts = [
        f'<g fill="{color}" transform="translate({center_x} {baseline_y}) scale({scale} {-scale})">'
    ]
    for name in glyph_names:
        pen = SVGPathPen(glyph_set)
        glyph_set[name].draw(pen)
        path = pen.getCommands()
        if path:
            parts.append(
                f'<path transform="translate({cursor / scale} 0)" d="{path}"/>'
            )
        cursor += advances[name][0] * scale
    parts.append("</g>")
    font.close()
    return "".join(parts)


def qr_path(url: str, *, x: float, y: float, size: float) -> str:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    pitch = size / len(matrix)
    squares = []
    for row, cells in enumerate(matrix):
        for col, dark in enumerate(cells):
            if dark:
                squares.append(f"M{col} {row}h1v1h-1z")
    return (
        f'<g fill="{NAVY}" transform="translate({x} {y}) scale({pitch})">'
        f'<path d="{"".join(squares)}"/></g>'
    )


def sticker(name: str, size_mm: int) -> str:
    # A square cut at the requested physical size, with a generous safe margin.
    # The artwork remains transparent outside the paths.
    width, height = 657, 760
    logo = embedded_logo(name, x=(1000 - width) / 2, y=120, width=width, height=height)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_mm}mm" height="{size_mm}mm" '
        'viewBox="0 0 1000 1000">'
        f"{logo}</svg>"
    )


def banner() -> str:
    size = 3048  # 10 feet, exact, in millimetres
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}mm" height="{size}mm" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="{NAVY}"/>',
        # Use the same stacked lockup as the white transparent sticker.
        embedded_logo("stacked-white.svg", x=590, y=90, width=1868, height=2161),
        font_text(
            "All you need in one flight app",
            center_x=1524,
            baseline_y=2360,
            size=100,
            color=SKY,
        ),
    ]
    for x, label, url in (
        (340, "App Store", APPLE),
        (2308, "Google Play", GOOGLE),
    ):
        pieces.extend(
            (
                f'<rect x="{x}" y="2440" width="400" height="400" rx="18" fill="#ffffff"/>',
                qr_path(url, x=x + 30, y=2470, size=340),
                font_text(
                    label,
                    center_x=x + 200,
                    baseline_y=2925,
                    size=58,
                    color="#ffffff",
                ),
            )
        )
    pieces.append(
        font_text(
            "pgpilot.app", center_x=1524, baseline_y=2700, size=160, color="#ffffff"
        )
    )
    pieces.append("</svg>")
    return "".join(pieces)


def write_assets() -> None:
    designs = {"pgpilot-banner-10ft-square": banner()}
    for name, size_mm in (("50mm", 50), ("100mm", 100), ("1m", 1000)):
        designs[f"pgpilot-sticker-{name}-blue-navy"] = sticker(
            "stacked-sky-navy.svg", size_mm
        )
        designs[f"pgpilot-sticker-{name}-white"] = sticker("stacked-white.svg", size_mm)
    source = DESTINATIONS[0]
    source.mkdir(parents=True, exist_ok=True)
    for stem, svg in designs.items():
        (source / f"{stem}.svg").write_text(svg)
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(source / f"{stem}.pdf"))
    preview_name = "pgpilot-banner-10ft-square-preview.png"
    cairosvg.svg2png(
        bytestring=designs["pgpilot-banner-10ft-square"].encode(),
        write_to=str(source / preview_name),
        output_width=1600,
        output_height=1600,
    )
    for destination in DESTINATIONS[1:]:
        destination.mkdir(parents=True, exist_ok=True)
        for stem in designs:
            for extension in ("svg", "pdf"):
                name = f"{stem}.{extension}"
                shutil.copyfile(source / name, destination / name)
        shutil.copyfile(source / preview_name, destination / preview_name)


if __name__ == "__main__":
    write_assets()
