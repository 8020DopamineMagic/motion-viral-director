# Story engines and the AV script

Read this for narrative structure, emotional craft, scriptwriting and pacing arithmetic.

Contents
1. Choosing a narrative engine
2. The three engines
3. Nested open loops
4. What makes a piece emotionally magnetic
5. The two-column AV script standard
6. Pacing arithmetic
7. Common script failures and their fixes

Tier key: **Craft**, **Standard**, **Platform** (dated), **Heuristic**.

---

## 1. Choosing a narrative engine (Heuristic)

| The piece is... | Use | Because |
|---|---|---|
| A character or customer who changes: short film, case study, founder story, long-form essay with a protagonist | **Story Circle** | Transformation needs a cost, and the circle forces one |
| An argument, explainer, tutorial, product pitch, anything driven by reasons | **But / Therefore** | Causality is what keeps reasoning watchable |
| A 30-150 s motion piece, visual allegory or mood film where wonder matters more than conflict | **Kishōtenketsu** | The twist recontextualises instead of defeating a villain |
| Long-form (8 min+) that wants a Kishōtenketsu shape | Kishōtenketsu **plus** an active question or stake opened early | On its own it risks slow mid-act retention |

Engines combine. A common hybrid: Kishōtenketsu for the overall shape, But / Therefore between every beat, and a small Story Circle for the character inside it. Name the engine in the script header so the choice can be challenged.

## 2. The three engines (Craft)

**Dan Harmon's Story Circle (8 stages).**
1. *You*: a character in a comfort zone.
2. *Need*: they want or lack something.
3. *Go*: they enter an unfamiliar situation.
4. *Search*: they adapt.
5. *Find*: they get what they sought.
6. *Take*: they pay a real price for it.
7. *Return*: back to the familiar world.
8. *Change*: transformation shown through action, not stated.

Stage 6 is where most branded stories go soft. If nothing was paid, nothing was earned.

**Stone and Parker's But / Therefore.** Audit every transition. Delete each flat "and then" and replace it with **Therefore** (a consequence the audience could have reasoned out) or **But** (an earned reversal). If neither fits, the two beats are not connected and one of them should go.

**Kishōtenketsu (four parts).**
- *Ki*: introduction.
- *Shō*: development.
- *Ten*: an unexpected shift in perspective, the twist.
- *Ketsu*: a crisp resolution that does not linger.

The *Ten* works best when it is human, not supernatural: new information that changes what everything before it meant.

## 3. Nested open loops (Heuristic)

- Open one macro mystery in seconds 0-5.
- Close a micro-loop every 15-45 s. Each closure is a reward for staying.
- Withhold the final answer until the emotional climax.

A loop is a promise. Count the loops you open and confirm each one closes; an unclosed loop reads as bait and shows up as a late dip.

## 4. What makes a piece emotionally magnetic (Craft)

- **Specific human stakes.** A named amount, a named person, a time on a clock. Never a vague abstraction.
- **Cost and vulnerability.** The *Take* stage: something was risked or lost.
- **Visual subtext.** Let the picture contradict or deepen the voiceover. If the picture only illustrates the words, one of them is redundant.
- **Contrast.** Quiet restraint before impact. Silence before sound.

## 5. The two-column AV script standard (Craft)

Write directly into a grid that keeps picture and sound in step. Minimum columns:

| Timecode | Beat and connector | Visual, motion logic, focal point, cut type, safe zone | Spoken copy, SFX, music, silence |
|---|---|---|---|

Rules:
- **Timecodes to a tenth of a second** for the first 15 seconds, where every frame is doing hook work; whole seconds after that are fine.
- **One hero mover per row.** If a row needs two, split the row.
- **Give the pace of every spoken line** (words, WPM, chars/s). The validator output can be pasted in.
- **Name the connector** (BUT / THEREFORE) on each row after the first.
- **Annotate key cuts** with the Rule of Six criterion they serve, and key motion with the principle in play.
- **Put on-screen text in the visual column in quotes**, with its position if the format is vertical.
- **Mark silence as an event** with start and length. It is a sound-design decision, not an absence.

Header fields: title; format, aspect and target runtime; narrative engine; loudness target; AI disclosure status (exempt, assistive only / required, realistic AI visuals or audio).

A blank version is in `assets/av-script-template.md`. A fully annotated example is in `worked-examples.md`.

## 6. Pacing arithmetic

Narration baseline: **130-150 WPM**, conversational. That stays well under the 180 WPM and 20 chars/s caption ceilings and leaves **15-25% of runtime** free for pictures, SFX and silence.

- Words per minute = `words / seconds x 60`.
- Characters per second = `characters including spaces / seconds`.
- Word budget = `runtime seconds x speech fraction x WPM / 60`.

| Runtime | Max words (85% speech, 140 WPM) | Comfortable (75% speech) |
|---|---|---|
| 15 s | 29 | 26 |
| 30 s | 59 | 52 |
| 45 s | 89 | 78 |
| 60 s | 119 | 105 |
| 90 s | 178 | 157 |
| 2 min | 238 | 210 |

A hook line may run fast (up to 180 WPM) for urgency; a whole piece at that pace is tiring. `scripts/check_cadence.py` checks each beat and the totals, and `--runtime` tells you whether a draft fits before you time it.

When a line is over the limit, cut words before you add time. The first cut is usually the opening clause.

## 7. Common script failures and their fixes

| Failure | How it shows | Fix |
|---|---|---|
| Preamble | "Hey guys, today we're going to..." | Delete it. Start on the result, the question or the contradiction |
| Narrating the picture | VO describes what is visibly on screen | Make one of them carry different information |
| "And then" chain | Beats could be reordered without anyone noticing | Rewrite the connectors as BUT / THEREFORE; cut what will not connect |
| Announced sections | "Next, let's look at..." | Bridge with the next beat's picture or sound under the current sentence |
| Vague stakes | "Businesses lose money" | A number, a name, a moment |
| Buried payoff | The best line is in the last quarter | Tease it in the cold open, deliver it at the climax |
| Outro wind-down | "That's it, thanks for watching" | End on the payoff or the loop line |
| Wall of VO | No row without speech | Give the picture a beat to itself; add the silence |
