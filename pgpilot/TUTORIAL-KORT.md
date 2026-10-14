# Short version: 15 minutes

`tutorial-kort.qmd` is `tutorial.qmd` cut from 38 to 14 slides (the hidden
title slide is not counted in either), for a live evening at Bir Billing. Goal:
people install the app and try it. Same order as the webinar where it matters
(install, permissions, group, talk), then one pass through a flight, then the
Bir pack as the local payoff. All act dividers are gone except the closing
one; on 15 minutes they cost more than they give, and "The Bir pack" lives on
in a slide title instead.

Reuses `voss.css`, `img/` and `voss-video/`. One new asset:
`img/qr-join-bir.png` (`https://pgpilot.app/join/bir`).

## Slide by slide

| # | Slide in tutorial.qmd | Choice | Why |
|---|---|---|---|
| 1 | Get started (hero) | keep | Opening picture, kicker changed to "Bir Billing" |
| 2 | Part 1: Introduction | cut | Act divider |
| 3 | What is pgpilot? | keep | Has to be said before asking them to install |
| 4 | Get the app | keep | The whole point of the evening |
| 5 | First time you open it | keep | Permissions and "See it in action" are where people stall |
| 6 | Join the group | keep | The group carries the rest of the talk. New QR for `bir` |
| 7 | Part 2: The flight instrument | cut | Act divider, "computed on the phone" moved to Thermals notes |
| 8 | The instrument | merge into 9 | Same screenshot as Get the app. Numbers point in Thermals notes |
| 9 | Thermals and vario | keep | The single most convincing clip |
| 10 | Plan a task | cut | Voss task, live and slow |
| 11 | After the flight | keep | Reason to open the app again. Absorbs Connect the services |
| 12 | Activity detection | cut | Answer to a webinar question, not a first-night topic |
| 13 | AreaContest | cut | Voss map, and rules take too long |
| 14 | Part 3: Live wind | cut | Act divider |
| 15 | Map over Voss | cut | Voss-specific |
| 16 | Tap Live wind | cut | Hangur East (Voss) wind meter |
| 17 | The airgram | keep | Works for any takeoff, including Billing. Moved before Thermals |
| 18 | Part 4: Comms | cut | Act divider |
| 19 | Talk together | keep | The moment the room gets it. Moved up right after Join |
| 20 | The button on the riser | cut | One line in Talk together notes |
| 21 | The KV4P radio | merge into 28 | VHF column of Three radios, two lines of notes |
| 22 | Part 5: Hardware | cut | Act divider |
| 23 | Connect your vario | cut | Bluetooth detail, not needed to try the app |
| 24 | Which varios work | cut | Reference table, nobody reads it from the back |
| 25 | Connect the services | merge into 11 | Only the "auto upload to XContest" line survives |
| 26 | The kit | cut | Gear talk, first candidate back in if there is time |
| 27 | Part 6: The Bir pack aka off grid | merge into 28 | Divider folded into the slide title; its "why" notes moved there |
| 28 | Three radios, three jobs | keep | Frame for the local part, retitled "The Bir pack: three radios" |
| 29 | FANET and FLARM | merge into 30 | Same screenshot. FANET is one bullet and one note |
| 30 | Meshtastic and Bircom | keep | Most relevant slide for this audience |
| 31 | InReach | keep | Short, and people get it wrong |
| 32 | Which LoRa board | keep | What they will buy. T-Echo listed first as the Bir standard |
| 33 | Your questions (divider) | cut | Webinar-only, built from the sign-up form |
| 34 | Flying with others | cut | Webinar Q&A |
| 35 | Seeing it in the air | cut | Webinar Q&A |
| 36 | Your flight log | cut | Webinar Q&A |
| 37 | What's coming | cut | Webinar Q&A, and no dates anyway |
| 38 | Thanks for today | keep | Retitled "Thanks", new background, call to action |

## Time budget

| # | Slide | Time |
|---|---|---|
| 1 | Get started | 0:15 |
| 2 | What is pgpilot? | 0:45 |
| 3 | Get the app | 3:00 |
| 4 | First time you open it | 1:00 |
| 5 | Join the group | 1:00 |
| 6 | Talk together | 1:30 |
| 7 | The airgram | 0:45 |
| 8 | Thermals and vario | 1:00 |
| 9 | After the flight | 0:45 |
| 10 | The Bir pack: three radios | 1:15 |
| 11 | Meshtastic, Bircom and FANET | 1:30 |
| 12 | InReach | 0:45 |
| 13 | Which LoRa board | 0:45 |
| 14 | Thanks | 0:45 |
| | **Sum** | **15:00** |

Install, permissions, group and talk (3-6) take almost half. That is on
purpose, and it is what overruns first if the mobile data on the landing is
slow. If it does, cut The airgram and InReach first.

## Webinar- and Voss-specific things to fix for Bir tonight

Already changed in the short deck:

- **Hero kicker** was "Tutorial webinar, 1 October 2026", now "Bir Billing".
- **Join the group** was `pgpilot.app/join/webinar` with `qr-join-webinar.png`.
  Now `pgpilot.app/join/bir` with a new `qr-join-bir.png`. **Create the group
  with the code `bir` when you rig, not before** (the reaper archives it after
  four silent hours). If you use another code, regenerate the QR:
  `uv run --no-project --with 'qrcode[pil]' python -c "import qrcode; qrcode.make('https://pgpilot.app/join/CODE').save('pgpilot/img/qr-join-bir.png')"`.
- **Closing slide** background was `app-areacontest.jpg` (AreaContest over
  Voss), now `b3f4fc34.jpg`, the group photo `kort.qmd` closes on. Notes no
  longer say "the webinar group stays up".
- **Webinar-only notes** removed: "tell them in the channel beforehand", "say
  whether you record", the Part 1 to 6 cross-references.

Still Norwegian on screen, change if you have time:

- **The airgram** screenshot is "VossHPK Hangur East", "Tomorrow, Saturday".
  Best fix is a fresh Billing airgram screenshot today. The notes already tell
  the audience to tap Billing on their own phone.
- **Get the app**: `app-instrument.jpg` is a flight over Sogndal.
  `app-bir-replay.jpg` exists in `img/` and may be a drop-in local swap.
- **First time you open it**: `app-ready.jpg` shows "SOGN TIA 4" in the
  airspace field. Fine, but someone may ask.
- **After the flight**: `app-flightdetails.jpg` is Togga - Sota saeter, Norway.
- Check on the spot that Bircom nodes and Billing takeoff weather actually show
  up in the app, since the notes promise both.

Cut, but flag them if anyone pulls them back in: "Map over Voss", "Tap Live
wind" (Hangur East), "Plan a task" (Bavallen, Storebrekkuna, Bjornestigen,
Rokne), "AreaContest" (Voss map), "The instrument" notes (Vegar, Svein, Tom S,
over Sogndal), and the whole "Your questions" block (from the webinar sign-up
form).
