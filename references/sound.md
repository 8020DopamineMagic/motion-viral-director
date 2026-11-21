# Sound design, mix hierarchy and mastering

Read this for sound plans, mixing, loudness targets and playback checks.

Contents
1. Narrative audio flow: J-cuts, L-cuts, layers, silence
2. Mix hierarchy
3. Loudness normalisation and platform targets
4. Three-device translation audit
5. Writing a sound plan before a render exists

Tier key: **Craft**, **Standard**, **Platform** (dated), **Heuristic**.

---

## 1. Narrative audio flow (Craft)

Sound is what makes fabricated pictures feel physical. Most of it should be invisible.

- **J-cut: audio leads picture.** Bring the next scene's sound in 0.3-1.5 s before the visual cut. It creates anticipation and carries the viewer across a hard cut. Use it to bridge section seams in long-form instead of announcing the next section.
- **L-cut: audio trails picture.** Let dialogue or atmosphere continue over the incoming B-roll or reaction shot. It keeps emotional continuity and turns narration into montage.
- **Layered hits.** Build an impact from at least three textures: a crisp transient, a midrange body, and sub-bass below 60 Hz for weight. A single stock whoosh sounds like a stock whoosh.
- **Risers and strategic silence.** Pair a rise with a short, hard silence directly before the reveal. The contrast pulls attention back to the frame; the silence does more than the riser.

## 2. Mix hierarchy (Craft; levels are common practice, not a standard)

| Layer | Target level | EQ and dynamics | Job |
|---|---|---|---|
| 1. Dialogue / VO | Peaks around -12 dBFS (-6 to -3 dB on hot social mixes) | High-pass below 80-100 Hz; dip 200-400 Hz boxiness; gentle lift at 2.5-5 kHz for presence; de-ess 6-8 kHz | Carries the story. Sits 15-25 dB above the music bed |
| 2. Hard SFX and foley | -10 to -20 dBFS, under dialogue | Carve 1-3 kHz so hits sit beside the voice, not on it | Grounds objects, edits and motion in physical reality |
| 3. Design SFX | -12 to -25 dBFS | Full spectrum; controlled sub-bass below 60 Hz for weight | Punctuates transitions, risers, emotional shifts |
| 4. Music / score | -20 to -30 dBFS under dialogue | Notch 1-4 kHz during speech; sidechain duck 3-5 dB keyed to dialogue | Sets the emotional pulse; swells only in speech gaps |
| 5. Ambience and room tone | -30 to -40 dBFS | High-pass below 80 Hz; gentle stereo width; record or loop at least 30 s | Removes the jarring "digital black" between dialogue cuts |
| 6. Deliberate silence | Negative space | Cut music and ambience cleanly for 0.3-1.5 s before the key reveal | The strongest contrast reset available |

Mix with -6 to -3 dBFS of headroom before the final true-peak limiter.

## 3. Loudness normalisation and platform targets

**Normalisation is not compression** (Standard: ITU-R BS.1770 loudness, EBU R128). Platforms apply a static gain shift based on K-weighted perceived loudness (LUFS). That preserves dynamic range. A master that was limited hard to sound loud just gets turned down, and then sounds flat next to everything else.

| Destination | Integrated loudness | True-peak ceiling | Tier |
|---|---|---|---|
| YouTube (long-form and Shorts), Spotify | about -14 LUFS | -1.0 dBTP | Platform |
| Apple Music | -16 LUFS | -1.0 dBTP | Platform |
| Broadcast TV, Europe | -23 LUFS (EBU R128) | -1.0 dBTP | Standard |
| Broadcast TV, North America | -24 LKFS (ATSC A/85) | -2.0 dBTP | Standard |
| TikTok and Instagram Reels | **-16 LUFS, by convention** | -1.0 dBTP | Heuristic |

**The TikTok and Reels nuance.** Neither platform publishes a universal numeric loudness target, and both transcode to lossy AAC. -16 LUFS integrated sits inside the EBU R128 streaming range (-20 to -16 LUFS); the -1.0 dBTP ceiling protects against inter-sample clipping after AAC encoding; and on clips of 60 s or less, keep short-term loudness within 5 LU of the target so one loud passage does not dominate. Present this as a conservative production convention, never as a platform rule.

`scripts/audit_media.py` measures integrated loudness, true peak and short-term maximum, and prints the two-pass `loudnorm` command that would correct a failing file. It never rewrites the file itself.

## 4. Three-device translation audit (Craft)

Listen to every export on:
1. headphones;
2. laptop speakers;
3. a phone speaker at low to normal volume, which is also the mono-compatibility check.

If speech disappears on the phone speaker, revise EQ and ducking before shipping. This check needs a person and a device; until someone has done it, it is pending.

## 5. Writing a sound plan before a render exists

A sound plan is a table against the beat sheet, not a list of adjectives. For each beat give:

- the **cut type** into it (hard, J-cut with lead time, L-cut with tail time);
- **VO**, with word count and pace;
- **SFX**, naming the layers of any impact;
- **music**: in, out, ducked by how much, or silent;
- **silence**: exact start and length;
- **level targets** for the layers that are active.

Then state the master target for each deliverable (for example -14 LUFS / -1.0 dBTP for the 16:9 master and -16 LUFS / -1.0 dBTP for the 9:16 cutdown) and list the three-device audit under pending checks.

Rights belong in the plan too: where the music and SFX come from and the licence that covers this use. An unlicensed track is a blocking finding, however good the mix is.
