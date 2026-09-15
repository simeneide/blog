# Kiosk media notes

## Editorial cut

16 feature slides. Removed the introduction, closing card, explanatory
algorithm sequence and static whale standings. The flight-day forecast is
part of flight analysis, not a separate slide. The regional figures remain,
with only **Coming soon** beneath the title.

The deck is a recorded demo, not a live data dashboard. Do not revive rejected
takes as fallbacks if a newer source file is missing.

## Selected recordings

New recordings live beneath the `REVISED` directory in `build.py`:
`/home/simen/.claude/jobs/eeb1fb3a/tmp/kiosk-revision/`.

| Feature | Selected source | What it demonstrates |
|---|---|---|
| Thermal assist | `thermalwind/thermal-deadband.mp4` | Native north-up deadband camera and current thermal lift-trail widget |
| Wind estimation | `thermalwind/wind-visible.mp4` | Warmed native wind speed, direction and map arrow |
| Competition navigation | `navigation/navigation-real.mp4` | Actual competition task, native countdown, gate opening and counted start-cylinder exit |
| Side view | `navigation/sideview-fixed.mp4` | Native route profile aimed at a fixed RIDGE waypoint |
| 3D replay | `editorial/glacier-replay.mp4` | Landscape orbit through the real Jostedalsbreen/Jostedalen flight |
| Group voice | `editorial/voice-simple.mp4` | Illustrated two-pilot voice exchange and its transcript |
| VHF bridge | `editorial/vhf-simple.mp4` | Illustrated radio/app exchange through one bridge |
| Weather forecast | `analysisweather/weather-comparison.mp4` | Real St Hilaire du Touvet observed-versus-forecast station card |
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
- **Wind:** the same replay, with lead-in to warm the estimator. All 216
  captured frames have populated native readings and a visible map arrow.
  The recorded estimate ranges from 1.9 to 2.9m/s.
- **Navigation:** built-in Jostedal sample with a local demonstration competition
  task and a rebased demonstration clock. Coordinates and native telemetry
  are unchanged. The native gate opens at 10.05 seconds; the actual cylinder
  crossing advances to TP1 at 15.05 seconds. No countdown overlay and no manual
  navigation during the clip. The final 15.8s and 16.1s files were recovered
  from intact encoded packets after a capture deadline interrupted container
  finalization; both fully decode without errors.
- **Side view:** the app's Route profile, not its Heading profile. The target
  remains RIDGE while the pilot's heading changes; waypoint distance falls
  from 807m to 673m.
- **Glacier and analysis:** Simen's Togga-Sota saeter flight,
  `c9f78e38-43f3-406f-a757-32767de7f022`, 18 August 2026. The glacier take uses
  the real Jostedalsbreen segment, not the Sogndal gaggle and not a repeated
  three-second portrait hook.
- **Analysis layout:** only presentation sizing was changed for capture:
  full-width detail, light theme, reserved header space and readable charts.
  The forecast belongs to that flight day at Tvangen. Its API model is
  `meps-archive`; the production UI labels it ICON-EU. The captured UI was left
  unchanged, and that model label is not repeated in the deck's copy.
- **Weather:** genuine populated `ffvl-61` station card at St Hilaire du Touvet.
  Observations and DWD forecast are aligned in the same time columns. The
  drawer was widened for the recording; values were not replaced.
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
