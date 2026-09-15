# Kiosk media notes

## Editorial cut

17 feature slides, approximately 4m47s per loop. No introduction, closing card,
explanatory algorithm sequence or static whale standings. The flight-day
forecast remains part of flight analysis. A separate full-width airgram shows
the weather forecast; historical wind comparison has its own slide. Regional
figures remain marked **Coming soon**.

The deck is a recorded demo, not a live data dashboard. Do not revive rejected
takes as fallbacks if a newer source file is missing.

## Selected recordings

New recordings live beneath the `REVISED` directory in `build.py`:
`/home/simen/.claude/jobs/eeb1fb3a/tmp/kiosk-revision/`.

| Feature | Selected source | What it demonstrates |
|---|---|---|
| Thermal assist | `thermalwind/thermal-deadband.mp4` | Native north-up deadband camera and current thermal lift-trail widget |
| Wind estimation | `refinements/wind/wind-changing.mp4` | Warmed native wind changing from about 2 to 4m/s, with a visible direction change |
| Competition navigation | `refinements/navigation/navigation-extended.mp4` | Native countdown, gate opening, cylinder exit and almost 11 seconds on the next leg |
| Side view | `refinements/navigation/sideview-companions.mp4` | Wider fixed RIDGE Route profile with genuine companions |
| 3D replay | `refinements/editorial/glacier-faster.mp4` | Full original glacier orbit retimed to 1.5x |
| Group voice | `editorial/voice-simple.mp4` | Illustrated two-pilot voice exchange and its transcript |
| VHF bridge | `editorial/vhf-simple.mp4` | Illustrated radio/app exchange through one bridge |
| Historical wind | `analysisweather/weather-comparison.mp4` | Real St Hilaire du Touvet observed-versus-forecast station card |
| Weather forecast | `refinements/weather/airgram-forecast-clear.mp4` | Full-width native airgram with its day controls and legend unobscured |
| Ground contacts | `editorial/contacts-simple.mp4` | Real takeoff and landing footage with simplified example notifications |
| Analyse your flight | `analysisweather/analyse-large.mp4` | Full-width native analysis, turn direction, glides, thermals, measured air and flight-day forecast |
| Automatic activity segments | `editorial/activity-segments.mp4` | The published Instagram hike/fly/drive segmentation edit |

Tracking, the brake-line button and offline flying retain `klipp-tracking.mp4`,
`klipp-knapp.mp4` and `klipp-backcountry.mp4` from the Voss material. AreaContest
retains `coupe_whale_v8.mp4`. The regional slide uses the Europe and Alps
figures from the existing `ALGO` directory.

## Fidelity and provenance

- **Thermal:** replay flight `22cc952d-26f9-4bd9-abbb-cfac553f5b9a`.
  Actual follow mode, north-up, 250px deadband. The camera stays exactly fixed
  for the first 13.5 seconds, recenters once when the pilot reaches 256.62px,
  then stays fixed again. Terrain pixels were compared between captured
  frames. No per-frame camera driving; no legacy lift rose or duplicate ring.
- **Wind:** replay `22cc952d-26f9-4bd9-abbb-cfac553f5b9a`, flight seconds
  5975–6114 at 7x, after a 220-second native lead-in. All 240 captured frames
  have populated native readings and a map arrow. Speed ranges 2.3–4.1m/s,
  direction 132–172 degrees; the arrow label changes from 2 through 3 to 4m/s.
  Native north-up follow mode and the 250px deadband remain active.
- **Navigation:** built-in Jostedal Glacier Flight, recorded 6 June 2026, with
  the same local Jostedal Demo Race and a rebased demonstration clock.
  Coordinates and telemetry are unchanged. In the 25-second final clip the
  native gate opens at 9.05 seconds and the cylinder crossing advances to TP1
  at 14.05 seconds, leaving 10.95 seconds of genuine next-leg footage.
  The unsettled first capture second was trimmed, not frozen or looped.
- **Side view:** 19 seconds of the native Route profile aimed at fixed RIDGE,
  not the heading-following profile. Zoom 13.4 gives twice the linear map
  coverage of the previous 14.4 take; the profile spans about 3km.
  Thomas Lone and Tom Salamonsen appear on the map; Thomas, Vegard Johnsen,
  Tom and Svein H appear at their actual relative altitudes in the profile.
  The identical date-only shift was applied to all real companion recordings,
  fixing their absence when only the primary recording had been rebased.
  Waypoint distance falls from 798m to 672m while heading changes NW to SW.
- **Glacier and analysis:** Simen's Togga-Sota saeter flight,
  `c9f78e38-43f3-406f-a757-32767de7f022`, 18 August 2026. The glacier take uses
  the real Jostedalsbreen segment, not the Sogndal gaggle and not a repeated
  three-second portrait hook. The complete 18-second glacier recording is
  retimed to 12 seconds at 1.5x, without changing its telemetry or scene.
- **Analysis layout:** only presentation sizing was changed for capture:
  full-width detail, light theme, reserved header space and readable charts.
  The forecast belongs to that flight day at Tvangen. Its API model is
  `meps-archive`; the production UI labels it ICON-EU. The captured UI was left
  unchanged, and that model label is not repeated in the deck's copy.
- **Historical wind:** genuine populated `ffvl-61` station card at St Hilaire
  du Touvet. Observations and DWD forecast share the same time columns. The
  drawer was widened for recording; values were not replaced.
- **Airgram:** the same station's native forecast, ICON-EU confirmed by the
  sounding API, issued 15 September 2026 at 15:00 UTC and showing 16 September
  in Europe/Paris. The full-width chart pans through the flying day. Only
  presentation sizing changed: 102px clear above and 90px below keep the
  kiosk title and controls clear of the native chart, legend and day buttons.
- **Activities:** recovered from the actual published reel at
  <https://www.instagram.com/reel/Dci1G1DC0mM/>. The full 17.4s segmentation
  sequence remains; duplicated upper headlines were cropped away. It uses
  real track/app segment boundaries with the original edit's approximate
  terrain fill. It is not a live app screen recording.
- **Voice/VHF:** simplified illustrations, not captured conversations or real
  transmissions. **Contacts:** two different flights with example notifications,
  not one continuous flight or proof that a message was sent.

Capture evidence and contact sheets are retained beside the selected source
files. The kiosk changes did not alter pgpilot application source or production
flight/settings data.
