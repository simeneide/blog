"""Estimate, for every image element in the deck, which sub-rectangle of the raw
source image is actually shown, by matching the raw image against the rendered
slide thumbnail (the visual fasit)."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path("/home/simen/blog/himalaya")
PW, PH = 9144000, 5143500
TW, TH = 1600, 900

deck = json.loads((ROOT / "_source/slides.json").read_text())
imap = json.loads((ROOT / "_source/image-map.json").read_text())

out = {}

for s in deck["slides"]:
    n = s["n"]
    thumb = cv2.imread(str(ROOT / f"_source/thumbs/slide{n:02d}.png"), cv2.IMREAD_GRAYSCALE)
    elems = s["elements"]
    for idx, e in enumerate(elems):
        if e["kind"] != "image":
            continue
        key = f"{n}:{e['id']}"
        f = imap[e["file"]]
        raw = cv2.imread(str(ROOT / "img" / f), cv2.IMREAD_GRAYSCALE)
        H, W = raw.shape

        # element frame in thumb pixels
        fx = e["x"] / PW * TW
        fy = e["y"] / PH * TH
        fw = e["w"] / PW * TW
        fh = e["h"] / PH * TH
        # visible part of frame inside the canvas
        vx0, vy0 = max(0, int(round(fx))), max(0, int(round(fy)))
        vx1, vy1 = min(TW, int(round(fx + fw))), min(TH, int(round(fy + fh)))
        if vx1 - vx0 < 40 or vy1 - vy0 < 40:
            out[key] = {"status": "too-small"}
            continue
        region = thumb[vy0:vy1, vx0:vx1]

        # ORB match raw -> region
        orb = cv2.ORB_create(nfeatures=6000)
        k1, d1 = orb.detectAndCompute(raw, None)
        k2, d2 = orb.detectAndCompute(region, None)
        if d1 is None or d2 is None or len(k1) < 10 or len(k2) < 10:
            out[key] = {"status": "no-features"}
            continue
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        raw_m = bf.knnMatch(d1, d2, k=2)
        good = [m for m, nn in raw_m if m.distance < 0.75 * nn.distance]
        if len(good) < 12:
            out[key] = {"status": f"few-matches({len(good)})"}
            continue
        src = np.float32([k1[m.queryIdx].pt for m in good])
        dst = np.float32([k2[m.trainIdx].pt for m in good])

        # fit dst = [sx 0; 0 sy] src + [tx; ty] with RANSAC on a diagonal model
        best, best_inl = None, -1
        rng = np.random.default_rng(0)
        for _ in range(3000):
            i, j = rng.choice(len(src), 2, replace=False)
            dx = src[j, 0] - src[i, 0]
            dy = src[j, 1] - src[i, 1]
            if abs(dx) < 20 or abs(dy) < 20:
                continue
            sx = (dst[j, 0] - dst[i, 0]) / dx
            sy = (dst[j, 1] - dst[i, 1]) / dy
            if not (0.05 < sx < 20 and 0.05 < sy < 20):
                continue
            tx = dst[i, 0] - sx * src[i, 0]
            ty = dst[i, 1] - sy * src[i, 1]
            pred = np.stack([sx * src[:, 0] + tx, sy * src[:, 1] + ty], 1)
            err = np.linalg.norm(pred - dst, axis=1)
            inl = int((err < 3.0).sum())
            if inl > best_inl:
                best_inl, best = inl, (sx, sy, tx, ty, err < 3.0)
        if best is None or best_inl < 10:
            out[key] = {"status": f"ransac-fail({best_inl})"}
            continue
        mask = best[4]
        S, D = src[mask], dst[mask]
        # least squares refine
        sx, tx = np.polyfit(S[:, 0], D[:, 0], 1)
        sy, ty = np.polyfit(S[:, 1], D[:, 1], 1)
        # region coords -> full-frame coords
        # dst_frame = dst_region + (vx0 - fx, vy0 - fy)
        # want: raw px -> frame-local px (0..fw, 0..fh)
        tx_f = tx + vx0 - fx
        ty_f = ty + vy0 - fy
        # crop rect in raw px that maps to [0,fw]x[0,fh]
        cx0 = -tx_f / sx
        cx1 = (fw - tx_f) / sx
        cy0 = -ty_f / sy
        cy1 = (fh - ty_f) / sy
        out[key] = {
            "status": "ok",
            "inliers": int(mask.sum()),
            "raw": [W, H],
            "crop": [round(cx0, 1), round(cy0, 1), round(cx1 - cx0, 1), round(cy1 - cy0, 1)],
            "crop_frac": [
                round(cx0 / W, 4),
                round(cy0 / H, 4),
                round((cx1 - cx0) / W, 4),
                round((cy1 - cy0) / H, 4),
            ],
        }

Path(__file__).resolve().parent / "crops.json".write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(k, v.get("status"), v.get("crop_frac"), v.get("inliers"))
