#!/usr/bin/env python3
"""Pre-publish QA scorecard: one honest record of what was checked, how, and what is still open.

Every check is pass, fail, pending or na. A pass needs a method and evidence, and a measured
value that breaks its threshold fails whatever status was typed in. That is the point: the
scorecard separates checks that were executed from checks that are still pending, so a
plan or a render is never reported as more verified than it is.

Methods:  measured (a script read the file)   computed (calculated from the spec)
          inspected (looked at the output)    attested (the person confirmed it)

Usage:
  python qa_scorecard.py init --project demo --format 9:16_short --out scorecard.json
  python qa_scorecard.py set scorecard.json wcag.contrast pass --value 7.2 --method computed --evidence "check_contrast.py"
  python qa_scorecard.py report scorecard.json          # JSON
  python qa_scorecard.py report scorecard.json --md     # Markdown verification summary
  python qa_scorecard.py list                           # every check and when it applies

Formats: 9:16_short, 9:16_medium, 16:9_medium, 16:9_long, 4:5_feed, 1:1_feed
Exit codes (report): 0 READY, 1 BLOCKED, 3 NOT READY (checks pending), 2 malformed input.
"""
import argparse
import json
import sys
from pathlib import Path

FORMATS = ["9:16_short", "9:16_medium", "16:9_medium", "16:9_long", "4:5_feed", "1:1_feed"]
STATUSES = ["pass", "fail", "pending", "na"]
METHODS = ["measured", "computed", "inspected", "attested"]
VERTICAL = {"9:16_short", "9:16_medium"}
LANDSCAPE = {"16:9_medium", "16:9_long"}
FEED_FIRST = {"9:16_short", "9:16_medium", "4:5_feed", "1:1_feed"}


def _always(fmt):
    return True


# id, label, how to verify, applies(format), threshold key (or None)
CHECKS = [
    ("story.causal_chain", "Beats link by BUT or THEREFORE, never 'and then'", "read the beat sheet", _always, None),
    ("story.runtime_fit", "Speech leaves 15% or more of runtime free", "check_cadence.py", _always, "min_breathing_pct"),
    ("hook.frame0", "Frame 0 is a hard cut to a mute-readable visual (no fade, no logo bumper)",
     "extract_contact_sheet.py hook strip", lambda f: f in FEED_FIRST, None),
    ("hook.promise_match", "Opening frames confirm the thumbnail and title promise",
     "compare thumbnail with first frame", lambda f: f in LANDSCAPE, None),
    ("hook.loop_seam", "Last line flows into frame 0 for a seamless replay (mark na if no loop is intended)",
     "watch the seam twice", lambda f: f == "9:16_short", None),
    ("hierarchy.squint_blur", "Intended focal element still dominates when blurred", "squint sheet", _always, None),
    ("hierarchy.grayscale", "Hierarchy holds with colour removed", "grayscale sheet", _always, None),
    ("hierarchy.three_second", "Subject and message clear within 3 s without audio", "hook strip, sound off", _always, None),
    ("hierarchy.one_hero_mover", "One hero mover per beat; only related elements move together", "watch each beat", _always, None),
    ("captions.max_wpm", "Captions and VO at or under 180 WPM", "validate_captions.py or check_cadence.py", _always, "max_wpm"),
    ("captions.max_cps", "Captions at or under 20 chars/s", "validate_captions.py", _always, "max_cps"),
    ("captions.min_sec_per_word", "At least 0.30 s per word", "validate_captions.py", _always, "min_sec_per_word"),
    ("captions.max_chars_per_line", "Longest caption line within the format limit", "validate_captions.py", _always, "max_chars_per_line"),
    ("captions.sound_off", "Fully understandable with sound off", "watch muted", _always, None),
    ("safe_zones.inside", "All text, logos and CTAs inside the platform safe zone", "check_safe_zones.py, then in-app draft",
     lambda f: f in VERTICAL, None),
    ("audio.integrated_lufs", "Integrated loudness on target", "audit_media.py", _always, "integrated_lufs"),
    ("audio.true_peak", "True peak at or under the ceiling", "audit_media.py", _always, "max_true_peak"),
    ("audio.music_ducked", "Music ducks 3-5 dB under speech and never masks it", "listen", _always, None),
    ("audio.three_device", "Speech survives headphones, laptop speakers and a phone speaker", "listen on all three", _always, None),
    ("wcag.contrast", "Text and caption contrast at least 4.5:1 (3.0:1 large)", "check_contrast.py", _always, "min_contrast"),
    ("wcag.flashes", "No more than 3 flashes in any second", "screen_flashes.py; PEAT/Harding for broadcast", _always, "max_flashes"),
    ("wcag.reduced_motion", "Reduced-motion variant exists (set pending only if this ships inside a web or app UI)",
     "test with prefers-reduced-motion", lambda f: False, None),
    ("compliance.ai_assessed", "Decided whether any realistic synthetic or altered media is present", "review every shot and voice", _always, None),
    ("compliance.labels_configured", "Required AI disclosure set on each target platform (na if no realistic AI media)",
     "upload settings", _always, None),
    ("compliance.provenance_preserved", "C2PA / SynthID provenance metadata left intact", "export settings", _always, None),
    ("compliance.authorship_log", "Human authorship log archived (drafts, project files, edit decisions)", "repo or folder", _always, None),
    ("compliance.rights_cleared", "Music, SFX, fonts, footage and likenesses licensed for this use", "licence records", _always, None),
]
REGISTRY = {c[0]: c for c in CHECKS}


def default_targets(fmt):
    landscape = fmt in LANDSCAPE
    return {"integrated_lufs": -14.0 if landscape else -16.0, "lufs_tolerance": 1.5 if landscape else 2.0,
            "max_true_peak": -1.0, "max_wpm": 180, "max_cps": 20, "min_sec_per_word": 0.30,
            "max_chars_per_line": 42 if landscape else 25, "min_contrast": 4.5, "max_flashes": 3,
            "min_breathing_pct": 15}


def new_scorecard(project_id, fmt, platforms=None):
    if fmt not in FORMATS:
        raise ValueError(f"unknown format {fmt!r}; choose from {FORMATS}")
    checks = {}
    for cid, label, how, applies, _ in CHECKS:
        checks[cid] = {"label": label, "how": how, "status": "pending" if applies(fmt) else "na",
                       "value": None, "method": None, "evidence": ""}
    return {"project_id": project_id, "format": fmt, "platforms": platforms or [],
            "targets": default_targets(fmt), "checks": checks}


def _threshold_ok(key, value, targets):
    """True/False when the value can be judged, None when there is nothing to judge."""
    if key is None or value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, ""
    if key == "integrated_lufs":
        t, tol = targets["integrated_lufs"], targets["lufs_tolerance"]
        return abs(value - t) <= tol + 1e-9, f"{t:g} LUFS +/-{tol:g}"
    if key.startswith("min_"):
        return value >= targets[key] - 1e-9, f">= {targets[key]:g}"
    return value <= targets[key] + 1e-9, f"<= {targets[key]:g}"


def report(card):
    fmt = card.get("format")
    if fmt not in FORMATS:
        raise ValueError(f"unknown format {fmt!r}; choose from {FORMATS}")
    checks = card.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("scorecard has no 'checks' object")
    targets = {**default_targets(fmt), **(card.get("targets") or {})}
    passed, failed, pending, na, problems = [], [], [], [], []
    for cid, entry in checks.items():
        if cid not in REGISTRY:
            raise ValueError(f"unknown check id {cid!r}; run 'list' to see valid ids")
        status = entry.get("status")
        if status not in STATUSES:
            raise ValueError(f"{cid}: status must be one of {STATUSES}, got {status!r}")
        _, label, how, _, key = REGISTRY[cid]
        row = {"id": cid, "label": label, "how": how, "value": entry.get("value"),
               "method": entry.get("method"), "evidence": entry.get("evidence") or ""}
        ok, expected = _threshold_ok(key, entry.get("value"), targets)
        if expected:
            row["expected"] = expected
        if status == "na":
            na.append(row)
            continue
        if ok is False:
            if status != "fail":
                problems.append(f"{cid}: value {entry.get('value')} breaks {expected} but status was '{status}'; counted as fail")
            failed.append(row)
            continue
        if status == "fail":
            failed.append(row)
        elif status == "pass":
            if entry.get("method") not in METHODS or not row["evidence"].strip():
                problems.append(f"{cid}: marked pass without a method ({'/'.join(METHODS)}) and evidence; counted as pending")
                pending.append(row)
            else:
                passed.append(row)
        else:
            pending.append(row)
    for cid in REGISTRY:
        if cid not in checks:
            problems.append(f"{cid}: missing from the scorecard")
    if failed:
        verdict = "BLOCKED"
    elif pending or problems:
        verdict = "NOT READY: CHECKS PENDING"
    else:
        verdict = "READY"
    return {"project_id": card.get("project_id"), "format": fmt, "verdict": verdict,
            "counts": {"passed": len(passed), "failed": len(failed), "pending": len(pending), "na": len(na)},
            "failed": failed, "passed": passed, "pending": pending, "na": na, "problems": problems}


def to_markdown(rep, card=None):
    def val(r):
        v = "" if r["value"] is None else str(r["value"])
        return v + (f" (needs {r['expected']})" if r.get("expected") and v else "")

    lines = [f"# Verification summary: {rep['project_id']} ({rep['format']})", "",
             f"**Verdict: {rep['verdict']}**  ",
             f"{rep['counts']['passed']} passed, {rep['counts']['failed']} failed, "
             f"{rep['counts']['pending']} pending, {rep['counts']['na']} not applicable", ""]
    lines += ["## Checks executed", ""]
    done = [("FAIL", r) for r in rep["failed"]] + [("pass", r) for r in rep["passed"]]
    if done:
        lines += ["| Result | Check | Value | Method | Evidence |", "|---|---|---|---|---|"]
        lines += [f"| {tag} | `{r['id']}` {r['label']} | {val(r)} | {r['method'] or ''} | {r['evidence']} |" for tag, r in done]
    else:
        lines.append("None yet.")
    lines += ["", "## Checks pending", ""]
    if rep["pending"]:
        lines += ["| Check | How to verify |", "|---|---|"]
        lines += [f"| `{r['id']}` {r['label']} | {r['how']} |" for r in rep["pending"]]
    else:
        lines.append("None.")
    if rep["na"]:
        lines += ["", "## Not applicable", "", ", ".join(f"`{r['id']}`" for r in rep["na"])]
    if rep["problems"]:
        lines += ["", "## Scorecard problems", ""] + [f"- {p}" for p in rep["problems"]]
    return "\n".join(lines) + "\n"


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read scorecard {path}: {exc}") from None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="create a scorecard with every applicable check pending")
    p.add_argument("--project", required=True)
    p.add_argument("--format", required=True, choices=FORMATS)
    p.add_argument("--platforms", default="", help="comma-separated, e.g. tiktok,instagram_reels,youtube_shorts")
    p.add_argument("--lufs", type=float, help="override the loudness target, e.g. -23 for EBU broadcast")
    p.add_argument("--out", type=Path)
    p = sub.add_parser("set", help="record the result of one check")
    p.add_argument("scorecard", type=Path)
    p.add_argument("check_id")
    p.add_argument("status", choices=STATUSES)
    p.add_argument("--value")
    p.add_argument("--method", choices=METHODS)
    p.add_argument("--evidence", default="")
    p = sub.add_parser("report", help="summarise: executed, pending, verdict")
    p.add_argument("scorecard", type=Path)
    p.add_argument("--md", action="store_true", help="Markdown instead of JSON")
    sub.add_parser("list", help="list every check id")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "list":
            print(json.dumps([{"id": c[0], "label": c[1], "how": c[2],
                               "applies_to": [f for f in FORMATS if c[3](f)]} for c in CHECKS], indent=2))
            return 0
        if args.cmd == "init":
            card = new_scorecard(args.project, args.format, [s for s in args.platforms.split(",") if s])
            if args.lufs is not None:
                card["targets"]["integrated_lufs"] = args.lufs
            text = json.dumps(card, indent=2)
            if args.out:
                args.out.write_text(text + "\n", encoding="utf-8")
                print(json.dumps({"written": str(args.out), "checks": len(card["checks"])}))
            else:
                print(text)
            return 0
        card = _load(args.scorecard)
        if args.cmd == "set":
            if args.check_id not in card.get("checks", {}):
                raise ValueError(f"unknown check id {args.check_id!r}; run 'list' to see valid ids")
            entry = card["checks"][args.check_id]
            entry["status"] = args.status
            if args.value is not None:
                try:
                    entry["value"] = float(args.value)
                except ValueError:
                    entry["value"] = args.value
            if args.method:
                entry["method"] = args.method
            if args.evidence:
                entry["evidence"] = args.evidence
            args.scorecard.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"updated": args.check_id, "status": args.status}))
            return 0
        rep = report(card)
        print(to_markdown(rep, card) if args.md else json.dumps(rep, indent=2))
        return {"READY": 0, "BLOCKED": 1}.get(rep["verdict"], 3)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
