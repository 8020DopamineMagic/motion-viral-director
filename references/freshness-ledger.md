# Freshness ledger

Every dated claim this skill relies on, when it was last checked, and how to check it again. Read this before a decision that depends on a platform rule, a tool capability, a model line-up or a price.

**Last full review: 2026-11-20** (second pass the same evening re-checked the NY law, Thaler, Cavalry, Agent Skills, Sora dates, CEP and Resolve rows). Review monthly, or whenever a claim here drives a decision.

How to use it:
- **Re-checked**: independently confirmed against current reporting or official pages on the review date. Still re-verify for high-stakes use.
- **Corrected**: the source playbook was wrong or overstated; the skill now carries the corrected version.
- **Source only**: taken from the source playbook and not independently checked. Treat as a lead, not a fact, and verify before relying on it.
- **Stable**: a published standard or long-standing convention that rarely changes.

When you verify a claim during a task, say so in the verification summary with the date. If you find a claim here is out of date, tell the person and use what you found.

## Platform ranking signals

| Claim | Status | Re-check with |
|---|---|---|
| Instagram: top three signals are watch time, likes per reach, sends per reach; likes weigh more for connected reach, sends for unconnected (Mosseri, January 2025) | Re-checked | "Mosseri ranking signals sends per reach" |
| An "October 23, 2026 Mosseri AMA" confirming the same | **Corrected: removed.** No such AMA found; that date belongs to a third-party explainer article | n/a |
| "A send is worth N likes" multipliers | **Corrected: flagged as speculation** | n/a |
| YouTube Shorts: Views count every start or loop since 31 March 2025; Engaged views reported separately | Stable since the change; consistent with general knowledge, not re-checked this review | "YouTube Shorts views engaged views" |
| YouTube Shorts: viewed versus swiped away as the first gate; satisfaction surveys | Source only | YouTube Creator Insider, Help Center |
| TikTok micro-retention checkpoints at 1 s and 3 s | Heuristic, source only | n/a |

## Safe zones

| Claim | Status | Re-check with |
|---|---|---|
| Per-platform margin percentages (TikTok 8/22/6/13, Reels 12/32/6/11, Stories 13/20/6/6, Shorts 9/20/6/12) | **Corrected: downgraded from "verified" to working defaults.** Published 2026 figures disagree widely (for example 900 x 1400 centred; TikTok top 108 px; ad specs with a 660 px bottom margin). The universal zone is conservative under most of them | An in-app draft preview; the platform's ad spec for paid placements |
| Pixel arithmetic for a 1080 x 1920 canvas | Re-checked by unit test | `pytest scripts/tests/test_safe_zones.py` |

## Loudness

| Claim | Status | Re-check with |
|---|---|---|
| YouTube about -14 LUFS; EBU R128 -23 LUFS; ATSC A/85 -24 LKFS; -1 dBTP ceiling | Stable | Platform help pages, EBU R128, ATSC A/85 |
| TikTok and Reels publish no numeric target; -16 LUFS is a convention | Stable as a convention; no platform publication found | "TikTok loudness normalization LUFS official" |

## Captions and accessibility

| Claim | Status | Re-check with |
|---|---|---|
| BBC 160-180 WPM, 37 chars; Netflix 42 chars, 20 CPS adult / 17 children, 0.83-7.0 s; DCMP 130-160 WPM | Stable | BBC Subtitle Guidelines, Netflix Timed Text Style Guide, DCMP Captioning Key |
| WCAG 2.2: 4.5:1 and 3.0:1 contrast; three flashes; reduced motion | Stable | w3.org/TR/WCAG22 |
| Contrast ratios quoted in `worked-examples.md` | Re-checked by unit test | `pytest scripts/tests/test_contrast.py` |

## Synthetic-media disclosure and law

| Claim | Status | Re-check with |
|---|---|---|
| YouTube: label below the player (long-form) or overlaid (Shorts) for photoreal content; description-only for unrealistic content; automatic labelling of undisclosed AI; disclosure does not affect recommendation or monetisation (27 May 2026) | Re-checked | YouTube Help "Disclosing use of altered or synthetic content" |
| TikTok: creator AI toggle; ad-level AI disclosure tightened 21 July 2026; C2PA reading, invisible watermarks, C2PA steering committee | Re-checked | TikTok Newsroom; Ads Manager help "ad disclaimers" |
| TikTok: duplicating an ad campaign resets the AI disclosure toggle | Source only | Test in Ads Manager |
| TikTok: "3B+ videos labelled" with AIGC labels (July 2026) | Re-checked; still not used by the skill (a vanity figure, not a rule) | TikTok Newsroom |
| TikTok: likenesses of minors, non-consensual likenesses of private adults and fabricated crisis footage are barred even when labelled | Source only; consistent with TikTok's published AIGC policy | TikTok Community Guidelines, "Edited media and AI-generated content" |
| Meta: "AI info" label; AI-edited-only moved to the post menu; third-party AI detected in ads via C2PA since June 2026 | Re-checked | Meta Newsroom, Meta Business Help |
| Instagram "AI-generated profile" label with reach limits for unlabelled accounts (31 August 2026) | Re-checked | "Instagram AI-generated profile label" |
| EU AI Act Article 50 applies from 2 August 2026; marking duty for systems already on the market extended to 2 December 2026; Article 50(4) creative exception | Re-checked | European Commission AI Act pages and transparency guidelines |
| EU fines up to EUR 15 million or 3% of turnover for transparency breaches | Consistent with the Act's penalty article; not re-checked this review | AI Act Article 99 |
| New York synthetic performer disclosure law (GBL § 396-b), signed 11 December 2025, effective 9 June 2026; conspicuous disclosure when an ad contains a synthetic performer the advertiser knows about; $1,000 first / $5,000 later violations; audio-only ads and translation-only use excluded. Hawaii passed a near-identical law (July 2026); California's was awaiting signature (September 2026) | Re-checked | "synthetic performer disclosure law" plus the state |
| US Copyright Office *Part 2: Copyrightability* (January 2025); *Thaler v. Perlmutter* (D.C. Cir. 18 March 2025; cert. denied 2 March 2026, docket 25-449) | Re-checked (Supreme Court docket) | copyright.gov/ai; supremecourt.gov docket 25-449 |

## Tools

| Claim | Status | Re-check with |
|---|---|---|
| Remotion: `npx remotion skills add`, `npx skills add remotion-dev/skills`; free for up to 3 people; $25 per seat per month company licence | Re-checked | remotion.dev/docs/cli/skills, remotion.dev/pricing |
| Remotion: "13 official skills", "$0.01 per render, $100 minimum" automators plan, WebMCP Studio control from v4.0.518 | Source only; counts and prices dropped from the skill | remotion.dev |
| Remotion licence change planned for version 5 | Seen in one secondary source | remotion.dev/docs/license |
| DaVinci Resolve 21.1: Python scripting moved to Studio; Python 2 removed; MCP server Studio-only | Re-checked (Blackmagic release notes) | Blackmagic "About DaVinci Resolve 21" readme |
| Resolve free 21.1: ".py silently ignored; Lua sandbox blocks io, os.execute, require" | **Corrected: softened.** Blackmagic labels "advanced scripting" Studio-only; Digital Production (8 Sept 2026) reports the console scripting API remains in the free edition while Workflow Integrations, UIManager and external scripting need Studio. The specific sandbox list is unverified | Run a one-line script in the free edition's console |
| Resolve API has no edit-page trim, keyframe or transition calls; `AddTransition()` and `SetEffect()` do not exist | Source only; consistent with the published scripting README | Resolve "Developer/Scripting/README.txt" |
| After Effects: UXP public beta in AE (Beta) 27.1 with UXP 9.4 (announced 17 November 2026); GA planned Q2 2027; CEP Marketplace cut-off and default disable December 2028 | Re-checked | developer.adobe.com/uxp/migration-center |
| CEP stops shipping in all flagship Adobe apps after December 2029 (Adobe developer forum, 2026) | Re-checked | Same |
| Cavalry acquired by Canva (announced 24-25 February 2026, alongside MangoAI); to be integrated with Affinity; team says product direction continues | Re-checked | canva.com newsroom |
| Material Design 3 Expressive springs (May 2025); IBM Carbon motion curves and duration tokens | Stable | m3.material.io, carbondesignsystem.com/elements/motion |
| An "August 2026 update" to Carbon motion | Source only; date dropped from the skill | Same |
| Agent Skills specification donated to the Agentic AI Foundation under the Linux Foundation (22 October 2026); existing SKILL.md files keep working | Re-checked; not used by the skill | agentskills.io |

## Generative video

| Claim | Status | Re-check with |
|---|---|---|
| OpenAI Sora discontinued (announced 24 March 2026; app reported closed 26 April 2026; Sora 2 API reported ended 24 September 2026) | Re-checked | "OpenAI Sora discontinued" |
| Line-up: Veo 3.1, Seedance 2.0 / 2.5, Kling 3.0, Runway Gen-4.5, Wan open weights | Re-checked as of November 2026 | "best AI video models" plus the current month |
| Kling 4.0 with 30 s clips and 15-asset references | **Corrected: removed.** Not found in current comparisons | Kling release notes |
| Newer entrants not in the source: MiniMax H3, Gemini Omni Flash 1.1, Wan 3.0, LTX-2.5, HappyHorse | Added as of November 2026 | Same |
| Per-model clip lengths, reference limits, resolutions | Source only; removed from the skill in favour of selection criteria | Each vendor's documentation |
| Under $40 for 12-15 short clips | Source only estimate; get a current quote | Vendor pricing pages |
