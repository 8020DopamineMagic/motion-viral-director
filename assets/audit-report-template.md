# Pre-publish audit: [TITLE]

Mode: Audit. Format: [...]. Target platforms: [...].

**Verdict: [READY | NOT READY: CHECKS PENDING | BLOCKED]**
[One sentence: the single most important thing to fix, or why it is ready.]

## Working assumptions
- [Anything assumed because it was not supplied: platforms, profile, audience.]

## Blocking (fix before publishing)
| # | Where | Finding | Measured | Limit | Fix |
|---|---|---|---|---|---|
| 1 | [timecode, cue number or line] | [what is wrong] | [value] | [threshold and its source] | [the specific change, with the corrected value or position] |

## Should fix
| # | Where | Finding | Fix |
|---|---|---|---|

## Polish
- [...]

## What is working
- [Two or three things to keep. An audit that only lists faults invites over-correction.]

## Verification summary

**Checks executed**
| Check | Method | Result |
|---|---|---|
| [Caption reading speed] | [validate_captions.py on captions.srt] | [3 errors, 1 warning] |

**Checks pending**
| Check | Needs |
|---|---|
| [Three-device listening test] | [a person with headphones, a laptop and a phone] |
| [In-app safe-zone preview] | [a draft upload on each target platform] |

[If the scorecard was used, paste `qa_scorecard.py report --md` here instead of the two tables.]
