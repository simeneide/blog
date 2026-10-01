# pgpilot material

`index.html` is the source page. Copy it and `files/` to `docs/pgpilot/material/`
when publishing; GitHub Pages serves `main/docs` at `eide.ai`. Keep the two
trees identical. `/coupeicare/` redirects here for old bookmarks.

Run `build_assets.py` from the repository root to regenerate the six square
sticker variants and the 10 ft square banner:

```sh
uv run --no-project --with cairosvg --with qrcode --with fonttools python pgpilot/material/build_assets.py
```

The script writes identical output to both trees. It uses the outlined logos
in `files/` and DejaVu Sans Bold from `/usr/share/fonts/truetype/dejavu/`.
It generates physical-size SVG and PDF artwork, with text converted to paths.
The banner is exactly 3048 × 3048 mm; the sticker artboards are exactly
50 × 50 mm, 100 × 100 mm, and 1000 × 1000 mm. All files are at trim size with
no bleed. The banner has generous content margins and a full-bleed navy
background; add printer-specific bleed if a shop requires it.

The banner QR codes link directly to the pgpilot listings on
[App Store](https://apps.apple.com/no/app/pgpilot-flight-companion/id6759820116)
and [Google Play](https://play.google.com/store/apps/details?id=com.pgfly.app).
The white sticker artwork has a transparent background; printing it on clear
stock requires white ink.
