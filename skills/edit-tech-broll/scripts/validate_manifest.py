#!/usr/bin/env python3
"""Validate this skill's portable edit manifest; never writes an editor draft."""
import argparse
import json
import math
import sys
from pathlib import Path


def validate(data, root, check_files=False):
    errors, warnings = [], []
    root = Path(root).resolve()

    def err(label, message):
        errors.append(f"{label}: {message}")

    def num(value, label, positive=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            err(label, "must be a finite number")
            return None
        if value < 0 or (positive and value == 0):
            err(label, "must be positive" if positive else "must be non-negative")
            return None
        return value

    def path(value, label, optional=False):
        if optional and value in (None, ""):
            return
        if not isinstance(value, str) or not value.strip():
            err(label, "must be a non-empty project-relative path")
            return
        p = Path(value)
        if p.is_absolute() or ".." in p.parts or "\\" in value or ":" in value:
            err(label, "absolute, parent-traversal, or platform-specific path is not portable")
            return
        candidate = (root / p).resolve()
        if not candidate.is_relative_to(root):
            err(label, "path or symlink escapes project directory")
        elif check_files and not candidate.is_file():
            err(label, f"file not found: {value}")

    def choice(value, allowed, label):
        if not isinstance(value, str) or value not in allowed:
            err(label, "expected one of " + ", ".join(sorted(allowed)))

    def boolean(value, label):
        if not isinstance(value, bool):
            err(label, "must be true or false")

    if not isinstance(data, dict):
        return ["root must be an object"], []
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        err("schema_version", "expected 1")
    source, output = data.get("source"), data.get("output")
    if not isinstance(source, dict) or not isinstance(output, dict):
        return errors + ["source and output must be objects"], warnings
    path(source.get("path"), "source.path")
    duration = num(source.get("duration_s"), "source.duration_s", True)
    for label, obj in [("source", source), ("output", output)]:
        num(obj.get("fps"), label + ".fps", True)
        for key in ("width", "height"):
            value = obj.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                err(label + "." + key, "must be a positive integer")
    fps = output.get("fps")
    tolerance = 1 / fps + 0.000001 if isinstance(fps, (int, float)) and not isinstance(fps, bool) and math.isfinite(fps) and fps > 0 else 0.000001
    choice(source.get("audio_policy"), {"stream_copy", "preserve_timing"}, "source.audio_policy")
    boolean(source.get("burned_captions"), "source.burned_captions")
    if source.get("burned_captions") and output.get("add_caption_overlay"):
        warnings.append("source has burned captions; verify a second subtitle layer is intentional")

    raw_assets = data.get("assets")
    if not isinstance(raw_assets, list):
        err("assets", "must be an array")
        raw_assets = []
    assets, paths = {}, {}
    for i, asset in enumerate(raw_assets):
        label = f"assets[{i}]"
        if not isinstance(asset, dict):
            err(label, "must be an object")
            continue
        aid, apath = asset.get("id"), asset.get("path")
        if not isinstance(aid, str) or not aid.strip():
            err(label + ".id", "must be non-empty")
        elif aid in assets:
            err(label + ".id", "duplicate asset ID")
        else:
            assets[aid] = asset
        if isinstance(apath, str):
            if apath in paths:
                err(label + ".path", "duplicate asset path")
            paths[apath] = asset
        path(apath, label + ".path")
        path(asset.get("editable_source"), label + ".editable_source", True)
        choice(asset.get("type"), {"image", "video", "vector"}, label + ".type")
        choice(asset.get("verification"), {"verified", "illustration", "unverified"}, label + ".verification")
        choice(asset.get("status"), {"ready", "missing", "excluded"}, label + ".status")
        if asset.get("status") == "missing":
            warnings.append(label + " is missing")
        if asset.get("verification") == "unverified":
            warnings.append(label + " is unverified")
        if asset.get("origin") == "generated" and asset.get("verification") != "illustration":
            err(label, "generated media must be marked illustration")
        if "duration_s" in asset:
            num(asset["duration_s"], label + ".duration_s", True)

    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        return errors + ["segments must be a non-empty array"], warnings
    previous, ids = 0, set()
    progress = data.get("progress_bar")
    if progress is not None:
        if not isinstance(progress, dict):
            err("progress_bar", "must be an object")
        else:
            boolean(progress.get("enabled"), "progress_bar.enabled")
            if progress.get("enabled"):
                choice(progress.get("mode"), {"whole_video"}, "progress_bar.mode")
                choice(progress.get("placement"), {"fixed_canvas"}, "progress_bar.placement")
                choice(progress.get("anchor"), {"top", "bottom"}, "progress_bar.anchor")
    for i, segment in enumerate(segments):
        label = f"segments[{i}]"
        if not isinstance(segment, dict):
            err(label, "must be an object")
            continue
        sid = segment.get("id")
        if not isinstance(sid, str) or not sid.strip():
            err(label + ".id", "must be non-empty")
        elif sid in ids:
            err(label + ".id", "duplicate segment ID")
        else:
            ids.add(sid)
        start, end = num(segment.get("start"), label + ".start"), num(segment.get("end"), label + ".end")
        if start is not None and end is not None:
            if end <= start:
                err(label, "end must be greater than start")
            if abs(start - previous) > tolerance:
                err(label, "gap or overlap in composition timeline")
            if duration is not None and end > duration + tolerance:
                err(label, "end exceeds source duration")
            previous = end
        choice(segment.get("visual_type"), {"presenter", "real_ui", "official_source", "relationship_graph", "concrete_scene"}, label + ".visual_type")
        choice(segment.get("claim_status"), {"verified_fact", "official_claim", "author_analysis", "unverified", "not_applicable"}, label + ".claim_status")
        choice(segment.get("layout"), {"presenter_full", "broll_full_circle", "split", "presenter", "fullscreen"}, label + ".layout")
        boolean(segment.get("presenter_visible"), label + ".presenter_visible")
        if not isinstance(segment.get("trigger_phrase"), str) or not segment["trigger_phrase"].strip():
            err(label + ".trigger_phrase", "must contain aligned narration trigger text")
        sources = segment.get("sources")
        if not isinstance(sources, list) or any(not isinstance(x, str) or not x.strip() for x in sources):
            err(label + ".sources", "must be an array of non-empty provenance strings")
        if segment.get("claim_status") == "unverified":
            warnings.append(label + " contains an unverified claim")
        claim = segment.get("claim_status") if isinstance(segment.get("claim_status"), str) else None
        visual = segment.get("visual_type") if isinstance(segment.get("visual_type"), str) else None
        if claim in {"verified_fact", "official_claim"} and not sources:
            warnings.append(label + " needs claim provenance")
        ref = segment.get("asset")
        asset = assets.get(ref, paths.get(ref)) if isinstance(ref, str) else None
        if segment.get("visual_type") != "presenter" and asset is None:
            err(label + ".asset", "must reference an existing asset ID or path")
        if ref not in (None, "") and asset is None:
            err(label + ".asset", "unknown asset reference")
        if asset:
            if asset.get("status") != "ready":
                warnings.append(label + " references an asset that is not ready")
            if visual in {"real_ui", "official_source"} and asset.get("verification") != "verified":
                err(label, "UI or official-source evidence requires a verified asset")
            if "asset_in" in segment or "asset_out" in segment:
                ai, ao = num(segment.get("asset_in"), label + ".asset_in"), num(segment.get("asset_out"), label + ".asset_out")
                if asset.get("type") != "video":
                    err(label, "asset_in/out are for video only")
                if ai is not None and ao is not None:
                    if ao <= ai:
                        err(label, "asset_out must exceed asset_in")
                    if start is not None and end is not None and abs((ao - ai) - (end - start)) > tolerance:
                        err(label, "asset duration differs from segment; retiming needs an explicit separate workflow")
                    ad = asset.get("duration_s")
                    if isinstance(ad, (int, float)) and not isinstance(ad, bool) and math.isfinite(ad) and ao > ad + tolerance:
                        err(label, "asset_out exceeds asset duration")
        layout = segment.get("layout") if isinstance(segment.get("layout"), str) else None
        if layout in {"split", "presenter_full", "broll_full_circle", "presenter"} and segment.get("presenter_visible") is False:
            err(label, "selected layout requires visible presenter")
        if layout == "fullscreen" and segment.get("presenter_visible") is False:
            warnings.append(label + " hides presenter; document project-specific reason")
    if duration is not None and abs(previous - duration) > tolerance:
        err("segments", "final end does not match source duration")

    # Motion events are a planning contract. Real rendered motion requires playback QA.
    motion_requirement = data.get("motion_requirement")
    if motion_requirement is not None:
        choice(motion_requirement, {"semantic", "not_requested"}, "motion_requirement")
    motions = data.get("motions", [])
    if not isinstance(motions, list):
        err("motions", "must be an array")
        motions = []
    segment_map = {s["id"]: s for s in segments if isinstance(s, dict) and isinstance(s.get("id"), str)}
    motion_ids, internal_motion_segments = set(), set()
    for i, motion in enumerate(motions):
        label = f"motions[{i}]"
        if not isinstance(motion, dict):
            err(label, "must be an object")
            continue
        mid = motion.get("id")
        if not isinstance(mid, str) or not mid.strip():
            err(label + ".id", "must be non-empty")
        elif mid in motion_ids:
            err(label + ".id", "duplicate motion ID")
        else:
            motion_ids.add(mid)
        sid = motion.get("segment_id")
        segment = segment_map.get(sid) if isinstance(sid, str) else None
        if segment is None:
            err(label + ".segment_id", "must reference an existing segment")
        choice(motion.get("layer"), {"broll", "a_roll", "progress", "captions", "transition"}, label + ".layer")
        for field in ("target", "action", "trigger_phrase", "easing", "attention_objective"):
            if not isinstance(motion.get(field), str) or not motion[field].strip():
                err(label + "." + field, "must be a non-empty string")
        for field in ("state_from", "state_to"):
            state = motion.get(field)
            if not isinstance(state, (str, dict)) or not state or (isinstance(state, str) and not state.strip()):
                err(label + "." + field, "must describe a non-empty state")
        ms, me = num(motion.get("start"), label + ".start"), num(motion.get("end"), label + ".end")
        md = num(motion.get("duration_s"), label + ".duration_s", True)
        if ms is not None and me is not None:
            if me <= ms:
                err(label, "end must be greater than start")
            if md is not None and abs(me - ms - md) > tolerance:
                err(label, "duration_s must match end minus start")
            if segment:
                ss, se = segment.get("start"), segment.get("end")
                if all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (ss, se)):
                    if ms < ss - tolerance or me > se + tolerance:
                        err(label, "motion lies outside its segment")
        action = motion.get("action") if isinstance(motion.get("action"), str) else None
        if segment and motion.get("layer") == "broll" and action not in {None, "hold", "transition"}:
            internal_motion_segments.add(sid)
    if motion_requirement == "semantic":
        for sid, segment in segment_map.items():
            reason = segment.get("hold_reason")
            if segment.get("visual_type") != "presenter" and sid not in internal_motion_segments and not (isinstance(reason, str) and reason.strip()):
                warnings.append(f"segment {sid} needs internal B-roll motion or a reason for intentional stillness; presenter/progress/transition do not substitute")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--check-files", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        errors, warnings = validate(data, args.manifest.parent, args.check_files)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 1
    for message in errors:
        print("ERROR: " + message)
    for message in warnings:
        print("WARNING: " + message)
    failed = bool(errors or (args.strict and warnings))
    print(f"{'FAILED' if failed else 'PASSED'}: {len(errors)} errors, {len(warnings)} warnings. Not an editor compatibility or content-quality test.")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
