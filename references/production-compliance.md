# Production gates, safe zones, accessibility and disclosure

Read this for pre-production staging, the Go / No-Go gate, safe zones, WCAG motion safety, synthetic-media disclosure and rights.

Contents
1. Pre-production approval gates
2. The Go / No-Go gate
3. Safe zones and packaging
4. Accessibility and motion safety (WCAG 2.2)
5. Synthetic-media disclosure: the boundary, then each platform
6. Copyright, human authorship and rights
7. Quick decision table: does this need an AI label?

Tier key: **Craft**, **Standard**, **Platform** (dated), **Heuristic**. Everything in sections 5 and 6 is dated; check `freshness-ledger.md` and re-verify before a high-stakes decision. None of it is legal advice.

---

## 1. Pre-production approval gates (Craft)

Lock narrative, look and timing before expensive animation or generation starts. Each stage is cheap to change; the one after it is not.

| # | Stage | What gets locked | Sign-off question |
|---|---|---|---|
| 1 | Creative brief | Audience, goal, acceptance criteria, format, budget | Do we agree what success looks like? |
| 2 | Script lock | Every spoken word and beat | Would we record this as written? |
| 3 | Treatment and moodboard | Tone, references, world | Is this the right feeling? |
| 4 | 3-6 styleframes | Grid, type, palette, contrast | Do these pass the squint, grayscale and 3-second tests? |
| 5 | Storyboard | Every shot and transition | Is every beat connected by BUT or THEREFORE? |
| 6 | Timed animatic | Temp VO and rough cuts against the clock | Does it hold attention with no polish? |
| 7 | Motion system and animation | Easing tokens, the actual motion | |
| 8 | Sound mix and mastering | Levels, loudness target | |
| 9 | Technical, accessibility and compliance QA | The scorecard | Is every gate passed or consciously waived? |

For a piece under 30 seconds, stages 3-6 can collapse into one styleframe plus a timed script. For anything longer, skip them only when the person says so.

## 2. The Go / No-Go gate

A proposal stops before the first step that spends money or hours, and asks for the smallest set of decisions that unblocks it. Typical gate items:

1. **Concept and tone**: approve, or name the alternative.
2. **Runtime and deliverables**: master length and aspect, plus cutdowns.
3. **Tool stack and budget tier**: for example hybrid (code + 3D + generative APIs) or fully code-driven with no paid generation.
4. **Voice and compliance posture**: human or licensed non-cloned voice; the disclosure approach.

State what will be produced the moment the gate is passed (phase 1), so the yes is specific.

## 3. Safe zones and packaging

**Vertical safe zones** (Heuristic working defaults, sourced June 2026). On a 1080 x 1920 canvas:

| Platform | Top | Bottom | Left | Right | Safe box (x1..x2, y1..y2) | Safe area |
|---|---|---|---|---|---|---|
| TikTok in-feed | 8% (154 px) | 22% (422 px) | 6% (65 px) | 13% (140 px) | x 65..940, y 154..1498 | 875 x 1344 |
| Instagram Reels | 12% (230 px) | 32% (614 px) | 6% (65 px) | 11% (119 px) | x 65..961, y 230..1306 | 896 x 1076 |
| Instagram Stories | 13% (250 px) | 20% (384 px) | 6% (65 px) | 6% (65 px) | x 65..1015, y 250..1536 | 950 x 1286 |
| YouTube Shorts | 9% (173 px) | 20% (384 px) | 6% (65 px) | 12% (130 px) | x 65..950, y 173..1536 | 885 x 1363 |
| **Universal 3-feed** (TikTok + Reels + Shorts) | 12% (230 px) | 32% (614 px) | 6% (65 px) | 13% (140 px) | **x 65..940, y 230..1306** | **875 x 1076** |
| **Universal 4-feed** (+ Stories) | 13% (250 px) | 32% (614 px) | 6% (65 px) | 13% (140 px) | **x 65..940, y 250..1306** | **875 x 1056** |

How much to trust these: platforms do not publish one stable pixel box, the UI differs by device and changes without notice, and third-party guides published in 2026 disagree with each other by tens to hundreds of pixels. The universal zones are deliberately conservative, so content inside them is safe under most published figures. Paid placements reserve more space, especially at the bottom; get the ad spec and test it with `check_safe_zones.py --margins`. Always finish with an in-app draft preview, and list that preview under pending checks until someone has done it.

Faces and the focal subject can extend beyond the safe box; text, logos and calls to action cannot.

**Thumbnails for 16:9.** High contrast, one visual promise, legible on a phone. 1280 x 720 minimum (YouTube also accepts larger uploads). The first frame of the video must deliver exactly what the thumbnail promised.

## 4. Accessibility and motion safety (Standard: W3C WCAG 2.2)

| Criterion | Requirement |
|---|---|
| 1.4.3 Contrast (AA) | At least 4.5:1 for normal text and captions, 3.0:1 for large text |
| 1.4.1 Use of colour (A) | Never convey status, hierarchy or data by colour alone |
| 2.3.1 Three flashes (A), 2.3.2 (AAA) | No more than 3 general flashes and no more than 3 saturated-red flashes in any 1-second period |
| 2.2.2 Pause, stop, hide (A) | Auto-playing motion longer than 5 s, shown alongside other content, needs a pause or stop control |
| 2.3.3 Animation from interactions (AAA) | Honour `prefers-reduced-motion: reduce` in CSS, JS or Rive: replace large slides, zooms and parallax with a direct swap or a gentle opacity crossfade |

2.2.2 and 2.3.3 apply when the motion ships inside a web page or app. A video file uploaded to a platform inherits the platform's player controls.

For strobing, lightning or rapid-cut scenes, `scripts/screen_flashes.py` flags likely breaches, but only a PEAT or Harding analysis (ITU-R BT.1702 thresholds) clears content for broadcast or paid media.

## 5. Synthetic-media disclosure (Platform; dated)

**The boundary that holds across platforms.** Assistive use of AI is exempt: AI-drafted scripts, captions, hashtags, reframing, colour grading, audio clean-up. Disclosure applies to **realistic** synthetic or materially altered pictures or audio that a viewer could mistake for a real person, place or event. Clearly unrealistic, animated or stylised content generally needs no label.

**YouTube** (label placement updated 27 May 2026).
- Creators must disclose realistic altered or synthetic content at upload.
- Photorealistic or meaningfully altered or generated content shows a label below the player on long-form and as an overlay on Shorts. Unrealistic, animated or slightly altered content carries the disclosure in the expanded description only.
- YouTube also applies labels automatically when its systems detect significant AI generation that was not disclosed, and for content made with its own AI tools.
- Per YouTube, a disclosure label alone does not change recommendation or monetisation eligibility. Mass-produced, templated content can still fall foul of the separate inauthentic-content monetisation policy.

**TikTok.**
- Organic: turn on the AI-generated content setting for content that is fully generated or significantly edited with AI and looks realistic.
- Ads: the "This ad contains AI-generated content" disclosure in Ads Manager. TikTok tightened its ad policy on 21 July 2026 to require the label on realistic AI imagery, synthetic voices and realistic avatars.
- TikTok reads C2PA Content Credentials on uploads, applies invisible watermarks to content made with its own tools, and sits on the C2PA steering committee.
- Not allowed even with a label: likenesses of minors, non-consensual likenesses of private adults, fabricated news or crisis footage.
- Reported, not verified here: duplicating an ad campaign may reset the AI disclosure toggle. Check it on every clone.

**Meta (Instagram, Facebook, Threads).**
- Organic posts with photorealistic video or realistic-sounding audio need the AI label; Meta also labels automatically from C2PA and IPTC signals. Content that was only edited with AI has its "AI info" tucked into the post menu; fully generated content shows it openly.
- Ads: "AI info" appears in "About this ad" for ads made with Meta's AI tools, and since June 2026 third-party AI is detected from C2PA signals as well.
- From 31 August 2026 Instagram requires an "AI-generated profile" label on accounts whose featured person is AI-generated, and limits recommendation reach for accounts that do not use it. Using AI to edit photos, polish captions or make graphics does not trigger it.

**Never** strip C2PA or SynthID provenance metadata to avoid a label.

**EU AI Act, Article 50** (applies from 2 August 2026).
- Providers of generative systems must mark outputs in a machine-readable way. Systems already on the market before 2 August 2026 have until 2 December 2026 for that marking duty.
- Deployers must disclose deepfakes.
- **Article 50(4) creative exception:** for evidently artistic, creative, satirical or fictional work, the disclosure may be made in a way that does not hamper enjoyment of the work, for example in end credits or a discreet title card.
- Penalties for breaching transparency duties run up to EUR 15 million or 3% of worldwide annual turnover.

**United States, paid advertising.** State rules are appearing; New York's synthetic performer disclosure law took effect on 9 June 2026 ($1,000 first violation, $5,000 for later ones). Anyone running paid ads with synthetic performers should get legal review.

## 6. Copyright, human authorship and rights (Platform; dated)

- Per the US Copyright Office's *Part 2: Copyrightability* report (January 2025) and *Thaler v. Perlmutter* (D.C. Circuit, March 2025; Supreme Court review denied 2 March 2026), purely AI-generated output is not protected by US copyright, and a text prompt alone is not authorship.
- Protection attaches to human-authored scripts, original graphics, 3D and code, and to expressive human selection, arrangement and modification.
- When registering, more than trivial AI-generated elements must be disclosed.

**Keep a Human Authorship Log** from day one: dated drafts, version-control commits, project files, edit timelines, and notes on what was selected and changed. It is cheap to keep and impossible to reconstruct later.

**Rights clearance** is a gate, not a detail. Before publishing, confirm the licence for every music track, sound effect, font, stock clip and likeness covers this use (platform, paid or organic, territory, term). Synthetic voices should be original or licensed, never a clone of a real person without consent.

## 7. Quick decision table: does this need an AI label?

| What is in the piece | Label needed? |
|---|---|
| AI helped write the script, captions or title | No |
| AI colour grade, upscale, noise reduction, reframing | No |
| Motion graphics, UI animation, charts, abstract 3D | No (nothing realistic to mistake for real) |
| Clearly stylised or animated generative imagery | Generally no; on YouTube the disclosure sits in the description if declared |
| Photoreal generated places, objects or scenes that could be taken as real footage | **Yes** on YouTube, TikTok and Meta |
| A synthetic voice | Plain text-to-speech narration: generally no. A voice that could be taken for a real, identifiable person: **yes**, and consent is required |
| A realistic synthetic person, or a real person made to say or do something they did not | **Yes**, plus consent; prohibited outright for minors and private individuals |
| An account fronted by an AI-generated person | **Yes**: profile-level label on Instagram |
| Fictional or artistic film using photoreal generation, shown in the EU | **Yes**, and the EU disclosure can sit in the credits |

When in doubt, label. Platforms state that a label does not reduce reach; a missing one can.
