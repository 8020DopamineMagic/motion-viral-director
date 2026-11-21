# Motion grammar: design, semiotics, easing, kinetic type

Read this for visual design, animation physics, grids, motion systems or caption legibility.

Contents
1. Twelve principles, translated to motion design
2. What visual choices communicate
3. Gestalt in motion and Common Fate
4. Grid discipline
5. Three hierarchy audits (do these before animating)
6. Motion systems: springs versus cubic-beziers
7. Kinetic typography and caption legibility

Tier key: **Craft** = long-standing practice. **Standard** = published specification. **Platform** = dated statement. **Heuristic** = practitioner experience.

---

## 1. Twelve principles, translated to motion design (Craft)

From Johnston and Thomas, *The Illusion of Life*. Applied to shapes and type, they make abstract elements read as physical.

| Principle | Use in motion design | What it tells the viewer | The trade |
|---|---|---|---|
| Squash and stretch | Small, volume-preserving deformation on morphs and impacts | Mass, elasticity, life | Overuse makes serious content look like a cartoon |
| Anticipation | A brief opposite wind-up, or an eye-line cue before a cut or move | Prepares the eye, softens the shock of change | Too long and the hook slows down |
| Staging | Clear the background; isolate one hero mover per beat | Where to look, with no effort | Dense infographics need staggered reveals instead |
| Pose to pose | Lock the key compositions first, then fill the in-betweens | Protects grid, hierarchy and silhouette | Straight-ahead animation risks layout drift |
| Follow-through and overlap | Secondary elements trail the primary by 2-6 frames | Readable order, organic settling | Everything stopping on the same frame feels robotic |
| Slow in, slow out | Accelerate out of rest, decelerate into landing | Momentum and friction | Linear suits only mechanical loops and telemetry |
| Arcs | Route spatial moves along curves | Natural, graceful | Straight axial moves signal utilitarian UI precision; sometimes that is what you want |
| Secondary action | Micro-reactions (shadow shift, underline sweep) that support the hero | Polish and depth | Competing motion splits attention |
| Timing | Frame spacing sets perceived weight and the beat of a joke or a blow | Fast = light or urgent; slow = heavy | Uniform timing is monotonous |
| Exaggeration | Push silhouettes and scale on accent beats | Clarity on a small phone screen | Too much bounce erodes credibility |
| Solid form | Consistent light, depth planes and perspective | Flat vectors belong to one world | One inconsistent shadow breaks it |
| Appeal | Cohesive proportion, rhythm and silhouette | Abstract ideas become memorable | Polish cannot rescue a weak story |

## 2. What visual choices communicate (Craft)

**Shape.** Circles and smooth curves: warmth, safety, wholeness, continuity. Squares and rectangles: stability, structure, institutional trust. Triangles and sharp diagonals: tension, speed, conflict, direction.

**Colour and value.** High saturation against a muted ground isolates the focal point. Use **60-30-10**: 60% a dominant low-chroma ground that sets the mood, 30% a secondary that carries structure (type, cards), 10% a high-salience accent reserved for focal peaks and calls to action. If the accent appears everywhere, nothing is the focal point.

**Space.** Generous negative space signals authority and calm. Tight framing signals claustrophobia or urgency.

## 3. Gestalt in motion and Common Fate (Craft)

Figure-ground, proximity, similarity, continuity and closure all carry over from static design. Motion adds **Common Fate**: elements that move in the same direction at the same speed are perceived as one group at once, overriding differences in colour or shape.

Two rules follow:
- Synchronise elements that belong together (a data series, a UI group).
- Never animate unrelated items together. Shared motion implies they are related, or that one caused the other.

## 4. Grid discipline (Craft)

Use a modular grid (Müller-Brockmann's 8 to 32 field systems are the reference) to anchor margins, alignment axes and type scale so they hold across cuts. Treat it as an aid, not a formula: the point is that a headline that sits on an axis in shot 1 sits on the same axis in shot 7.

## 5. Three hierarchy audits (Craft)

Run these on styleframes before any animation. Motion amplifies a composition; it does not repair one.

1. **Squint or blur test.** Blur until detail vanishes. If the wrong thing dominates (texture over headline), fix the composition.
2. **Grayscale test.** Remove colour. If the hierarchy collapses, hue was doing work that size, weight and luminance contrast must do on their own.
3. **Three-second test.** Could a first-time viewer name the subject and the message within 3 seconds, with no audio?

With a rendered file, `scripts/extract_contact_sheet.py` exports the blurred, grayscale and first-3-seconds sheets. Open them and judge.

## 6. Motion systems: springs versus cubic-beziers

**Material Design 3 Expressive** (Platform: announced May 2025). Replaces duration-and-easing pairs with physics springs set by stiffness (speed), damping (bounce; a damping ratio of 1 removes overshoot) and initial velocity. It splits motion into *Expressive* (overshoots, for hero moments) and *Standard* (utilitarian, minimal bounce), and into *Spatial* tokens (position, scale, rotation: overshoot allowed) and *Effects* tokens (opacity, colour: no overshoot), each in fast, default and slow.

**IBM Carbon motion** (Standard: published design-system values). Separates *Productive* motion (fast, focused, for task efficiency) from *Expressive* motion (occasional, dramatic, for moments that matter).

| Curve | Productive | Expressive |
|---|---|---|
| Standard (visible start to end) | `cubic-bezier(0.2, 0, 0.38, 0.9)` | `cubic-bezier(0.4, 0.14, 0.3, 1)` |
| Entrance | `cubic-bezier(0, 0, 0.38, 0.9)` | `cubic-bezier(0, 0, 0.3, 1)` |
| Exit | `cubic-bezier(0.2, 0, 1, 0.9)` | `cubic-bezier(0.4, 0.14, 1, 1)` |

Duration tokens: fast-01 70 ms, fast-02 110 ms, moderate-01 150 ms, moderate-02 240 ms, slow-01 400 ms, slow-02 700 ms. Scale the token to the distance and size of the move: a small toggle takes 70-110 ms, a full-panel move 240-400 ms.

**Choosing.**
- Springs: interactive state machines (Rive, web) and programmatic motion (Remotion's `spring()`), where natural momentum or re-targeting mid-flight matters.
- Cubic-beziers: rendered timelines where a frame must land exactly on a musical downbeat or a voice transient. A spring's settle time is emergent; a bezier's end frame is known.
- Either way: opacity and colour never overshoot, and linear is for mechanical loops only.

A quick mapping: data snaps, UI state changes, list reorders use productive curves at 150-240 ms. Hero reveals, emotional turns and title cards use expressive curves or damped springs at 400-700 ms.

## 7. Kinetic typography and caption legibility

Kinetic type *performs* the meaning of the sentence instead of fading it in. Highlight one hero word per beat and hold everything else still long enough to read. If every word moves, none of them is emphasised.

**Reading-time standards** (Standard)

| Source | Speed | Line length | Lines | Duration |
|---|---|---|---|---|
| BBC subtitle guidelines | 160-180 WPM (0.30-0.375 s per word minimum hold) | 37 chars in 16:9; about 25 in 9:16 | 2 landscape, up to 3 vertical | n/a |
| Netflix English | 20 chars/s adult, 17 children | 42 chars | 2 | 0.83 s minimum (20 frames at 24 fps), 7.0 s maximum |
| DCMP Captioning Key | 130-160 WPM | n/a | n/a | 40 frames minimum (about 1.33 s at 30 fps), 6.0 s maximum |

The validators use the strictest sensible combination: 180 WPM, 0.30 s/word, 20 CPS, 0.83-7.0 s, 25 chars vertical, 42 landscape (`--standard bbc` for 37).

**Rules that numbers cannot check**
- Break lines at phrase or punctuation boundaries. Never split an article from its noun, or a first name from a last name.
- Use a heavy-stroke sans-serif over moving footage.
- Over a moving background, put text on a dark translucent scrim and test the worst case with `check_contrast.py --scrim`.
- Watch the whole piece with the audio muted. If it does not make sense, the captions are not finished.
- Word-by-word "pop" captions on vertical video may run shorter than 0.83 s per cue; the 0.30 s per word floor still applies.
