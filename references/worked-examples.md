# Worked examples

Read this to see how far a finished deliverable should go. The first three are compact decision records for the three formats. The fourth is a full gated short-film proposal with an annotated opening, and is the quality bar for the Short film and Script modes.

Contents
1. 45 s vertical motion-led explainer
2. 12-minute YouTube video essay
3. 2-minute hybrid atmospheric short film (summary)
4. Full example: "3:14", a gated short-film proposal

Every number in section 4 was produced by the scripts in this skill and is covered by its tests.

---

## 1. 45 s, 9:16 motion-led explainer (TikTok, Reels, Shorts)

**Raw brief:** "Announce our new AI invoice matcher to small business owners; make it go viral."

**Decisions**
- *Engine and hook:* Proof first plus an open loop, But / Therefore between beats. 0.0-0.5 s: hard cut to a red "$14,200 overpaid" invoice tearing in half, readable on mute, inside x 65-940, y 230-1306. 0.5-1.5 s VO: "Your spreadsheet missed $14,200 last quarter." 1.5-3.0 s: "Here is the 3-second rule that catches it."
- *Motion and colour:* 60% matte charcoal `#11151C`, 30% off-white cards, 10% emerald accent for matched rows only. Productive easing `cubic-bezier(0.2, 0, 0.38, 0.9)` for spreadsheet snaps. Matched rows sweep together (Common Fate); unmatched rows do not move. Built in code from CSV data so variations are cheap.
- *Sound and loop:* three-layer paper rip on frame 0; mechanical clicks carved at 1-3 kHz around the VO; music ducked 4 dB; master -16 LUFS / -1.0 dBTP. Final line "...which is why, every quarter," runs into the opening "your spreadsheet missed $14,200."
- *Compliance:* screen UI and motion graphics only, no realistic synthetic people, so no AI label; captions at 25 chars a line.
- *Word budget:* 45 s at 140 WPM holds 89 words at most; target 75-80.

## 2. 12-minute, 16:9 YouTube video essay

**Raw brief:** "Break down why modern skyscrapers sway and how tuned mass dampers save them."

**Decisions**
- *Engine and opening (0-30 s):* Story Circle applied to an engineering crisis (Citicorp Center, 1978), with nested open loops. Frame 0 confirms the thumbnail (wind-bent tower diagram plus a 400-ton block) under a storm-wind J-cut. Macro loop open by 0:22: "One phone call from a student prevented a collapse in Manhattan."
- *Pacing and seams:* 3D cross-sections intercut with archival stills. No "moving on" lines: wind-tunnel audio fades in 1.2 s before act 2 appears. A 2.5 s quiet visual pause before the damper maths is revealed.
- *Audio and QA:* master -14 LUFS / -1.0 dBTP; captions 42 chars a line; VO at 145 WPM. Grayscale contact sheet to confirm the force arrows, not the building wireframe, dominate each diagram.
- *Facts:* historical claims in an essay are checked against sources before script lock, and the sources go in the description.

## 3. 2-minute hybrid atmospheric short film, with a 9:16 cutdown (summary)

**Raw brief:** "Create an emotional 2-minute film about memory and craft with zero live-action budget."

**Decisions**
- *Pipeline fit:* no talking heads, so no lip-sync risk. Narration over real 3D macro hardware, plus generated atmospheric exteriors guided by static keyframes, assembled in an editor.
- *Craft:* a Kishōtenketsu turn recontextualises the central object at 1:25, after 1.2 s of silence.
- *Compliance:* keep provenance metadata, turn on realistic-AI disclosure on each platform, add an Article 50(4) notice in the end credits, commit scripts and scene files to version control as the authorship record.

Section 4 is this brief, fully worked.

---

## 4. Full example: "3:14" (gated proposal, pre-production only)

### Working assumptions

No inputs were supplied, so these defaults apply and are open to correction: design-literate general audience; 16:9 master for YouTube plus a 9:16 cutdown for TikTok, Reels and Shorts; free and local tooling with optional generative APIs; under $150 a month all-in; solo or team of up to three.

### Concept

- **Title:** *3:14*
- **Logline:** When a winter gale kills the power across a coastal harbour at 3:14 a.m., an estranged granddaughter returns to liquidate her late grandfather's watch shop, and finds his unfinished brass marine chronometer running backward.
- **Deliverables:** 16:9 master, 24 fps, **120 s**. 9:16 loopable cutdown, **35 s**, framed inside the universal safe zone (x 65-940, y 230-1306), its last line "...which is how the harbour finally learned why," running into the opening "At 3:14, every clock in the harbour stopped."
- **Engine:** Kishōtenketsu overall, But / Therefore between beats, a small Story Circle for the granddaughter.
- **Why it lands:** the twist is human, not supernatural. Behind the backplate is an engraved gear diagram: the grandfather built a reverse countdown calibrated to the days since she left, winding down to the dawn ferry home. Craft stands in for an apology never spoken. Voiceover, macro hardware, hands and schematic type carry the feeling with no synthetic faces.

### Visual and sonic direction

Palette (ratios from `check_contrast.py`):

| Role | Swatch | Meaning | Contrast |
|---|---|---|---|
| 60% dominant | Abyssal Slate `#0E131B` | Winter night, estrangement, stillness | ground |
| 30% secondary, mid | Fog Slate `#253040` | Wet steel, storm cloud, blueprint plates | supporting plane |
| 30% secondary, light | Warm Parchment `#EDE6D6` | Engraved dials, schematics, his notes | 14.98:1 on `#0E131B` |
| 10% accent | Signal Amber `#F29F3D` | Brass teeth, lamp warmth, lighthouse sweep | 8.69:1 on `#0E131B`; 6.22:1 on `#253040` |
| Captions | Pure Ivory `#F7F4EC` on `#0A0E14` scrim | Legible over rain and waves | 17.60:1 |

- **Type and motion:** a geometric sans for timecode ticks and schematic callouts; an engraved serif for the journal inscriptions. Gear snaps and blueprint overlays use Carbon productive curves (`cubic-bezier(0.2, 0, 0.38, 0.9)`, 150-240 ms). Amber light, fog and memory move on damped springs and slow arcs. Circles (dials, wheels, the lighthouse beam) mean memory and return; diagonals (rain, cracked glass) mean rupture.
- **Sound:** a sub-60 Hz foghorn bed; a three-layer brass tick (metal click, workbench resonance, air tail); two hard silences, at 0:06.6 when the second hand snaps backward and at 1:24 when the backplate opens. Cello only in speech gaps, ducked 4 dB under VO. Masters: -14 LUFS / -1.0 dBTP for 16:9; -16 LUFS / -1.0 dBTP for the cutdown.

### Beat sheet, 0:00-2:00

| Time | Act and connector | Picture and motion | Sound and silence | Shift |
|---|---|---|---|---|
| 0:00-0:15 | **Ki** (hook) | Harbour clocks frozen at 3:14; macro chronometer ticks in reverse; blueprint overlay snaps in | Hard metal tick, J-cut rain, silence, reverse ratchet | Intrigue |
| 0:15-0:35 | **Shō**, THEREFORE | Packing tape over shelves; ledger marked "LIQUIDATE"; a gloved hand stops over a brass box | Tape rip, low room tone, distant foghorn | Cold duty |
| 0:35-0:58 | **Shō**, BUT | She tries to stop the balance wheel; schematics bloom around the gears; each tick lifts raindrops upward | Reversed water foley; sparse pizzicato ducked 4 dB | Friction becomes curiosity |
| 0:58-1:22 | **Shō to pre-Ten**, THEREFORE | Memory montage under L-cut narration: a door slammed years ago, a cracked barometer, an untouched ferry timetable | Door slam into thunder; muted strings rising | Regret, the cost (*Take*) |
| 1:22-1:42 | **Ten**, BUT | 1.2 s silence. A loupe opens the backplate; amber light on engraved countdown gears and a note: "For when the tide turns: 4,112 days." | Silence, then solo cello, soft amber hum | Anger becomes grief and love |
| 1:42-2:00 | **Ketsu**, THEREFORE | Bare fingers wind the crown clockwise; the hand ticks forward past 3:15; the lighthouse sweeps amber across dark water; title holds 2.5 s | Forward tick, cello resolves, foghorn fades into gulls | Release and forward motion |

### Annotated opening, 00:00.0-00:15.0

Pacing from `check_cadence.py`: **33 words over 12.7 s of speech, 2.3 s without speech (15.3%), 155.9 WPM overall.** Every beat is at or under 180 WPM and 20 chars/s and at least 0.34 s per word. The overall pace sits just above the 130-150 conversational range, which is acceptable for a hook.

| Timecode | Picture, motion, hierarchy | Sound, with the cut priority it serves |
|---|---|---|
| 00:00.0-00:00.5 | **Hard cut on frame 0.** Extreme macro of the dial frozen at 3:14, parchment numerals on slate. Mute-readable stamp "03:14" in the upper safe zone. *Hook layer 1; staging: one hero dial.* | **SFX:** one dry brass tick plus a sub-60 Hz hull thud. J-cut: rain fades in at 00:00.3. *Rhythm.* |
| 00:00.5-00:03.2 | Three-shot match cut: clocktower, wheelhouse gauge, shop wall clock, all at 3:14. Rain streaks fall the same way in every shot (Common Fate). Crosshair ticks lock onto each dial, productive easing. *Hook layer 2; eye-trace keeps the dial centred.* | **VO (8 words, 177.8 WPM, 15.9 CPS):** "At 3:14, every clock in the harbour stopped" **SFX:** three stop-clicks on the cuts. *Story and rhythm.* |
| 00:03.2-00:06.6 | L-cut into a dim workbench; slow dolly on a 3D camera path to an open walnut case holding the amber chronometer; dust in the beam. *Hook layer 3, context lock; the 10% accent pulls the eye.* | **VO (9 words, 158.8 WPM, 17.1 CPS):** "except the brass chronometer nobody wound for forty years." **Music:** cello drone in at -26 dBFS, ducked 4 dB. *Emotion.* |
| 00:06.6-00:08.4 | **Pattern interrupt.** Camera holds on the second hand. 0.8 s of total stillness, then the hand snaps one notch counter-clockwise with a small damped recoil; a parchment arc traces "-01s". *Anticipation, exaggeration, contrast.* | **00:06.6-00:07.6: silence.** Rain and drone cut hard. **00:07.6:** reverse ratchet click plus a faint gear groan. *Contrast snaps attention back.* |
| 00:08.4-00:11.8 | J-cut into a blueprint overlay blooming over dark gale footage; lines draw in staggered order (follow-through). *Subtext: craft against the storm.* | **VO (9 words, 158.8 WPM, 14.4 CPS):** "My grandfather built it to outlive a winter gale." **SFX:** foghorn swell; wind carved out at 1-4 kHz. *Emotion and story.* |
| 00:11.8-00:15.0 | Her reflection fractured across the crystal as the hand ticks back three times; focus pulls to the amber gears beneath. *Macro loop locked; eye-trace lands on the centre.* | **VO (7 words, 131.3 WPM, 15.6 CPS):** "Tonight, its second hand started running backward." **SFX:** three reverse ticks, L-cut into scene 2. *Emotion over literal geography.* |

### Pipeline and risk controls

**Can be produced as soon as the gate is passed:** locked AV script; code for titles, blueprint overlays, caption tracks and safe-zone layouts in both aspects; 3D scripts for the chronometer rig, gear animation and camera blockouts; storyboard prompts; validator runs; the authorship log.

**Needs outside tools or people:**
1. *Static anchors:* generate and approve four keyframe stills (harbour clock, workbench macro, storm breakwater, engraved backplate) before any video generation.
2. *Atmospheric video:* generated harbour, rain and lighthouse shots guided by the 3D camera blockouts; a local open-weight model if nothing may leave the machine. Current model line-up and prices to be confirmed at the time.
3. *Voice and finishing:* a human voice actor or a licensed, original synthetic voice; edit, EQ, ducking and colour in an editor or with FFmpeg; a person listens on headphones, laptop and phone.

**Risks and controls**
- *Prop drift and mechanical physics:* gears are rendered in 3D, never generated. People appear only as hands, silhouettes and reflections, trimmed to the cleanest 2-3 s.
- *Lip-sync:* designed out; all speech is off-screen.
- *Budget and retries:* stills and the timed animatic are approved before any per-second API. Spend ceiling to be set at the gate.
- *Disclosure and copyright:* provenance metadata preserved; realistic-AI labels on YouTube, TikTok and Meta for the photoreal exteriors; Article 50(4) notice in the credits; script, code, scene files and selection notes archived.

### Go / No-Go gate (production stops here)

To start phase 1 (script lock, four styleframe specifications, timed animatic plan), confirm or change:

1. **Concept and tone:** *3:14*, or another theme.
2. **Runtime and deliverables:** 120 s 16:9 master plus 35 s 9:16 loop, or other lengths and platforms.
3. **Tool stack and budget:** hybrid (code, 3D, generative, editor) within the stated ceiling, or fully code-driven with no generative APIs.
4. **Voice and compliance:** human or original non-cloned voice, with platform labels and the EU credit notice.

### Verification summary

**Checks executed**
- Contrast for all five palette pairings: computed with `check_contrast.py`; all pass AA, four pass AAA.
- Opening VO pacing: computed with `check_cadence.py`; all six beats pass.
- Cutdown overlay position: inside the universal 3-feed box by construction.

**Checks pending** (need a render, a device or a person)
- Loudness and true peak on the exported masters (`audit_media.py`).
- Squint, grayscale and first-3-seconds sheets on rendered styleframes (`extract_contact_sheet.py`).
- Flash screening of the lightning shots (`screen_flashes.py`, then PEAT if anything is flagged).
- Three-device listening test.
- In-app safe-zone preview for the cutdown.
- Legal review before any paid placement or copyright registration.
