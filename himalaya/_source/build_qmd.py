"""Generate presentasjon.qmd from _source/slides.json.

One-shot generator: it produced the checked-in presentasjon.qmd. The qmd is the
thing you edit by hand afterwards (nudging a circle = editing one EMU number in
the inline <svg>). Re-running this overwrites those edits.

Geometry model: the Slides canvas is 9144000 x 5143500 EMU (16:9). Positions are
emitted as percentages of the .gslide container; the annotation layer is emitted
as an <svg viewBox="0 0 9144000 5143500"> so raw EMU numbers drop straight in.

Image crops come from _source/crops.json, fitted by matching each raw photo
against the rendered slide thumbnail (see fit_crops.py).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_source"

PW, PH = 9144000, 5143500
PT = 1.7778  # px per pt at width=1280 (1280px / 10in / 72pt)

deck = json.loads((SRC / "slides.json").read_text())
imap = json.loads((SRC / "image-map.json").read_text())
crops = json.loads((SRC / "crops.json").read_text())

# Elements hidden behind something else in the thumbnail could not be fitted;
# borrow the fit from the identical element on a sibling slide.
CROP_ALIAS = {
    "21:g39d0860f356_2_3": "20:g28ec5a56b4e_0_632",
    "28:g36cd557a9c4_0_20": "27:g355aa8fee1b_0_57",
    "49:g355aa8fee1b_0_14": "47:g355aa8fee1b_0_8",
    "50:g355aa8fee1b_0_21": "47:g355aa8fee1b_0_8",
}

# Font sizes (pt) not carried in the run styles, read off the thumbnails.
TITLE_PT = 28
BODY_PT = 18
# Keyed by element id. Slides applies these through the placeholder/list level,
# which the extraction does not carry; the values are measured off the thumbnails.
SIZE_OVERRIDE = {
    "g36cd557a9c4_0_43": 48,    # 38: the big white BONUS
    "g39d0860f356_2_5": 14,     # 21: right column, same size as the left one
    "g39d0860f356_2_10": 18.5,  # 28: right column, autofit-shrunk from 20pt
}
# The bottom-left caption box: on these slides the layout styles it with the
# heading font in orange, not the grey body font (cf. slide 38, which does not).
SLAB_BODY = {6, 7}
SLIDE_BG = {38: "#ff5722"}
TITLE_COLOR = {38: "#ffffff"}
# Second-level bullets (Slides nesting level is not in the extraction).
SUBBULLET_PREFIX = ("Middag:",)
# Extra paragraph indent (px at width=1280) that the extraction does not carry.
EXTRA_INDENT = {"g39d0860f356_2_7": 65}  # 21: the left column is indented


def pct_x(v: float) -> str:
    return f"{v / PW * 100:.4f}%"


def pct_y(v: float) -> str:
    return f"{v / PH * 100:.4f}%"


def box(e: dict) -> str:
    return (
        f"left:{pct_x(e['x'])};top:{pct_y(e['y'])};"
        f"width:{pct_x(e['w'])};height:{pct_y(e['h'])}"
    )


def paragraphs(runs: list[dict]) -> list[list[tuple[str, dict]]]:
    """Split runs into paragraphs on \\n. \\x0b is a soft break inside one."""
    paras: list[list[tuple[str, dict]]] = []
    cur: list[tuple[str, dict]] = []
    for r in runs:
        parts = r["text"].split("\n")
        for i, p in enumerate(parts):
            if p:
                cur.append((p, r.get("style", {})))
            if i < len(parts) - 1:
                paras.append(cur)
                cur = []
    if cur:
        paras.append(cur)
    return [p for p in paras if p]


def inline(seg: str, style: dict) -> str:
    # \x0b is a Slides soft line break. A trailing <br> renders no line box in
    # HTML, so pin it open with an nbsp - that blank line is what gives the
    # original its wide bullet spacing. (nbsp, not U+200B: the zero-width space
    # is outside the webfont's unicode-range and falls back to a font with
    # taller line metrics, which stretches the gap.)
    out = "<br>".join(html.escape(x) for x in seg.split("\x0b"))
    if out.endswith("<br>"):
        out += "&nbsp;"
    if style.get("bold"):
        out = f"<strong>{out}</strong>"
    if style.get("italic"):
        out = f"<em>{out}</em>"
    return out


def render_shape(n: int, e: dict) -> list[str]:
    runs = e.get("runs") or []
    paras = paragraphs(runs)
    if not paras:
        return []  # unused placeholder

    ph = e.get("placeholder") or "BODY"
    is_title = ph in ("TITLE", "CENTERED_TITLE")
    slab = is_title or n in SLAB_BODY
    size = SIZE_OVERRIDE.get(e["id"], TITLE_PT if is_title else BODY_PT)
    color = TITLE_COLOR.get(n, "#ff5722") if is_title else ("#ff5722" if n in SLAB_BODY else "#666666")
    bullets = (not is_title) and e["h"] > 1500000

    cls = ["tb", "slab" if slab else "sans", "title" if is_title else "body"]
    if ph == "CENTERED_TITLE":
        cls += ["centered", "anchor-bottom"]
    style = f"{box(e)};font-size:{size * PT:.1f}px;color:{color}"
    if e["id"] in EXTRA_INDENT:
        style += f";padding-left:{EXTRA_INDENT[e['id']] + 13}px"

    lines = [f'<div class="{" ".join(cls)}" style="{style}">']
    tag = "ul" if bullets else "div"
    lines.append(f"<{tag}>" if bullets else "")
    for p in paras:
        text = "".join(inline(seg, st) for seg, st in p)
        explicit = next((s.get("fontSize") for _, s in p if s.get("fontSize")), None)
        pt = SIZE_OVERRIDE.get(e["id"]) or (explicit and explicit["magnitude"])
        extra = f' style="font-size:{pt * PT:.1f}px"' if pt else ""
        if bullets:
            plain = "".join(seg for seg, _ in p)
            lvl = 1 if plain.startswith(SUBBULLET_PREFIX) else 0
            sub = ' class="l2"' if lvl else ""
            size_attr = extra or (' style="font-size:24.9px"' if lvl else "")
            lines.append(f"<li{sub}{size_attr}>{text}</li>")
        else:
            lines.append(f"<p{extra}>{text}</p>")
    if bullets:
        lines.append("</ul>")
    lines.append("</div>")
    return [x for x in lines if x != ""]


def render_roundrect(e: dict) -> list[str]:
    fill = e.get("fillColor") or "#bebebe"
    return [f'<div class="scrim" style="{box(e)};background:{fill}e3"></div>']


def render_image(n: int, e: dict) -> list[str]:
    f = imap[e["file"]]
    key = f"{n}:{e['id']}"
    c = crops.get(CROP_ALIAS.get(key, key), {})
    if c.get("status") == "ok":
        W, H = c["raw"]
        cx, cy, cw, ch = c["crop"]
        iw, ih = W / cw * 100, H / ch * 100
        il, it = -cx / cw * 100, -cy / ch * 100
        st = f"left:{il:.3f}%;top:{it:.3f}%;width:{iw:.3f}%;height:{ih:.3f}%"
    else:
        st = "left:0;top:0;width:100%;height:100%"
    return [
        f'<div class="fr" style="{box(e)}">',
        f'<img src="img/{f}" style="{st}">',
        "</div>",
    ]


def render_video(n: int, e: dict) -> list[str]:
    # poster: staa-bilde fra klippet. Klippene ligger utenfor git, saa paa den
    # publiserte versjonen svarer .mp4 med 404. Uten poster ble det en svart,
    # doed spiller. Med poster ser man bildet, og fallback-scriptet nederst i
    # decket fjerner kontrollene naar kilden mangler.
    return [
        f'<video class="vid" style="{box(e)}" src="video/slide{n:02d}.mp4"',
        f'       poster="img/poster-slide{n:02d}.jpg"',
        '       controls preload="metadata" playsinline></video>',
    ]


ARROW_DEFS = """<defs>
<marker id="ah{i}" viewBox="0 0 5 4" refX="4.4" refY="2" markerWidth="5" markerHeight="4"
        markerUnits="strokeWidth" orient="auto"><path d="M0,0 L5,2 L0,4 z" fill="#ff0000"/></marker>
<marker id="as{i}" viewBox="0 0 5 4" refX="0.6" refY="2" markerWidth="5" markerHeight="4"
        markerUnits="strokeWidth" orient="auto"><path d="M5,0 L0,2 L5,4 L3.8,2 z" fill="#ff0000"/></marker>
</defs>"""

# Slides stores these two lines with a flip the extraction collapsed; on slide 31
# the arrowhead sits on the (x,y) end, not on (x+w, y+h).
ARROW_AT_START = {31}


def render_annotations(n: int, group: list[dict], gi: int) -> list[str]:
    out = [
        f'<svg class="ann" viewBox="0 0 {PW} {PH}" preserveAspectRatio="none">',
        ARROW_DEFS.format(i=f"{n}_{gi}"),
    ]
    for e in group:
        col = e.get("color") or e.get("outlineColor") or "#ff0000"
        if e["kind"] == "line":
            w = e.get("weight") or 38100
            dash = ""
            cap = ""
            if e.get("dash") == "DASH":
                dash = f' stroke-dasharray="{w * 3:.0f} {w * 2:.0f}"'
            elif e.get("dash") == "DOT":
                dash = f' stroke-dasharray="1 {w * 2.5:.0f}"'
                cap = ' stroke-linecap="round"'
            if n in ARROW_AT_START:
                arrow = f' marker-start="url(#as{n}_{gi})"'
            else:
                arrow = f' marker-end="url(#ah{n}_{gi})"'
            out.append(
                f'  <line x1="{e["x"]:.0f}" y1="{e["y"]:.0f}" '
                f'x2="{e["x"] + e["w"]:.0f}" y2="{e["y"] + e["h"]:.0f}" '
                f'stroke="{col}" stroke-width="{w:.0f}"{dash}{cap}{arrow}/>'
            )
        else:
            w = e.get("outlineWeight") or 76200
            out.append(
                f'  <ellipse cx="{e["x"] + e["w"] / 2:.0f}" cy="{e["y"] + e["h"] / 2:.0f}" '
                f'rx="{e["w"] / 2:.0f}" ry="{e["h"] / 2:.0f}" '
                f'fill="none" stroke="{col}" stroke-width="{w:.0f}"/>'
            )
    out.append("</svg>")
    return out


def is_ann(e: dict) -> bool:
    return e["kind"] == "line" or (e["kind"] == "shape" and e.get("shapeType") == "ELLIPSE")


HEADER = """---
# Generert fra Google Slides-decket "Paragliding i himalaya" av
# _source/build_qmd.py. All geometri er i EMU (lerret 9144000 x 5143500).
# Annotasjonene ligger som inline <svg viewBox="0 0 9144000 5143500">, sa
# tallene er raa EMU: en sirkel flyttes ved aa endre ett tall.
title: "Paragliding i himalaya"
author: "Simen Eide"
lang: no
comments: false
html-math-method: plain
resources:
  - video/
  # poster= spores ikke av Quarto sin ressursjakt slik src= gjoer, saa
  # plakatbildene maa listes eksplisitt for aa havne i docs/.
  - img/poster-*.jpg
# Slide 1 er selve tittelsliden, sa Quarto sin auto-genererte skjules.
title-slide-attributes:
  data-visibility: hidden
format:
  revealjs:
    theme: default
    css: custom.css
    slide-number: true
    width: 1280
    height: 720
    margin: 0
    min-scale: 0.2
    max-scale: 2.0
    transition: fade
    auto-stretch: false
    controls: true
    progress: true
    hash: true
    include-after-body: video-fallback.html
---
"""


def main() -> None:
    doc: list[str] = [HEADER]
    for s in deck["slides"]:
        n = s["n"]
        bg = SLIDE_BG.get(n)
        doc.append("##" + (f' {{background-color="{bg}"}}' if bg else ""))
        doc.append("")
        # Sporingskommentaren maa ligge ETTER overskriften. Star den foer den
        # foerste `##`, lager pandoc en implisitt tom seksjon av den, og decket
        # aapner paa en blank slide.
        doc.append(f"<!-- slide {n:02d} -->")
        doc.append("")
        doc.append("```{=html}")
        doc.append(f'<div class="gslide"{f" style=background:{bg}" if bg else ""}>')

        elems = s["elements"]
        i = 0
        gi = 0
        while i < len(elems):
            e = elems[i]
            if is_ann(e):
                j = i
                while j < len(elems) and is_ann(elems[j]):
                    j += 1
                doc += render_annotations(n, elems[i:j], gi)
                gi += 1
                i = j
                continue
            if e["kind"] == "image":
                doc += render_image(n, e)
            elif e["kind"] == "video":
                doc += render_video(n, e)
            elif e.get("shapeType") == "ROUND_RECTANGLE":
                doc += render_roundrect(e)
            else:
                doc += render_shape(n, e)
            i += 1

        doc.append("</div>")
        doc.append("```")
        doc.append("")
        if s["notes"].strip():
            doc.append("::: {.notes}")
            note = s["notes"].rstrip().split("\n")
            for k, line in enumerate(note):
                if not line.strip():
                    doc.append("")
                    continue
                # trailing "\" = pandoc hard line break, so the stikkord stay one
                # per line in presenter view instead of running together
                nxt = note[k + 1].strip() if k + 1 < len(note) else ""
                doc.append(line + ("\\" if nxt else ""))
            doc.append(":::")
            doc.append("")

    (ROOT / "presentasjon.qmd").write_text("\n".join(doc) + "\n")
    print("wrote", ROOT / "presentasjon.qmd")


if __name__ == "__main__":
    main()
