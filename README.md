# motion-viral-director

An Agent Skill that directs and QA-checks video. It covers hooks, timed AV scripts, motion and sound specs, captions, loudness, safe zones, retention fixes, AI disclosure and gated short-film proposals. It plans and verifies but does not render; pair it with a render tool (HyperFrames, Remotion, an editor).

## Install

- **Claude Code / any Agent Skills client:** `git clone https://github.com/8020DopamineMagic/motion-viral-director ~/.claude/skills/motion-viral-director`
- **claude.ai skill card:** the card saves only `SKILL.md`. Section 0 tells Claude to fetch this repo at the pinned tag when it needs the references, templates or validators.

## Contents

| Path | What |
|---|---|
| `SKILL.md` | Router, defaults, operating rules, evidence tiers, QA loop, key numbers |
| `references/` | Motion grammar, formats and retention, story and script, sound, production and compliance, software adapters, worked examples, freshness ledger |
| `assets/` | Brief, AV script, audit report and retention templates; QA scorecard schema |
| `scripts/` | Stdlib Python validators: cadence, captions (SRT/VTT), safe zones, contrast, media loudness/true peak, contact sheets, flash screen, QA scorecard |
| `scripts/tests/` | `python -m pytest -q scripts/tests` |
| `evals/` | Test cases in the `claude plugin eval` layout |

Media checks need `ffmpeg` and `ffprobe` on PATH. Platform rules and tool facts are dated; see `references/freshness-ledger.md`.

## Releases

The card version pins a tag. To release, bump `metadata.version` in `SKILL.md` and the tag in its section 0 fetch command (a test enforces they match), commit, then tag `v<version>`.
