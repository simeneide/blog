# Source material for an "algorithms" segment

Simen wants the stand kiosk to carry an animated segment on what runs under
the hood (thermal centre, wind estimator, point forecast, regional forecast,
activity segmentation), with a different take than the dropped A0 poster
"Algorithms of pgpilot".

Everything for it is in the pgpilot repo on `main`:

    brand/coupe-icare-2026/poster-air/HANDOFF.md   what exists, what it may claim, how to make more
    brand/coupe-icare-2026/poster-air/README.md    the poster build, and where every number comes from
    brand/coupe-icare-2026/poster-air/shots/       real app captures (raw PNG, phone and wide)
    brand/coupe-icare-2026/poster-air/regional/    the regional-forecast figures
    brand/coupe-icare-2026/poster-air/hodograph.*  the velocity circle, with per-second points to animate

The kiosk already expects `thermal-assist.mp4` and `wind-estimation.mp4`
as landscape recordings (NOTES.md); the capture recipe in HANDOFF.md
produces both from a replay of a real flight.
