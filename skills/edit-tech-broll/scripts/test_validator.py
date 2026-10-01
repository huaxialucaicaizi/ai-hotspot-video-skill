#!/usr/bin/env python3
"""Offline contract tests using temporary files, never user media."""
import copy
import tempfile
import unittest
from pathlib import Path
from validate_manifest import validate


BASE = {
    "schema_version": 1,
    "source": {"path": "source.mp4", "duration_s": 12, "fps": 30, "width": 682, "height": 512,
               "audio_policy": "stream_copy", "burned_captions": True},
    "output": {"width": 1080, "height": 1920, "fps": 30},
    "assets": [{"id": "graph", "path": "graph.svg", "type": "vector", "source_url": "",
                "verification": "illustration", "status": "ready", "editable_source": "graph.svg", "origin": "self_made"}],
    "segments": [
        {"id": "s1", "start": 0, "end": 4, "trigger_phrase": "练习观点", "visual_type": "presenter",
         "asset": None, "claim_status": "author_analysis", "sources": [], "layout": "presenter", "presenter_visible": True},
        {"id": "s2", "start": 4, "end": 12, "trigger_phrase": "练习解释", "visual_type": "relationship_graph",
         "asset": "graph", "claim_status": "author_analysis", "sources": [], "layout": "split", "presenter_visible": True}
    ]
}

MOTION = {"id": "m1", "segment_id": "s2", "layer": "broll", "target": "flow.arrow",
          "action": "draw_path", "trigger_phrase": "练习解释", "start": 4.5, "end": 5.2,
          "duration_s": 0.7, "state_from": {"draw_fraction": 0}, "state_to": {"draw_fraction": 1},
          "easing": "ease_out", "attention_objective": "沿箭头理解处理顺序"}


class ManifestTests(unittest.TestCase):
    def run_case(self, change=None, files=False):
        data = copy.deepcopy(BASE)
        if change:
            change(data)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # Existence-only fixtures; these are intentionally not media decode tests.
            (root / "source.mp4").write_bytes(b"test fixture")
            (root / "graph.svg").write_text("<svg/>", encoding="utf-8")
            return validate(data, root, files)

    def test_valid(self):
        self.assertEqual(self.run_case(files=True), ([], []))

    def test_gap(self):
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(start=5))[0])

    def test_overlap(self):
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(start=3))[0])

    def test_end_duration(self):
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(end=11))[0])

    def test_nan_and_bool(self):
        self.assertTrue(self.run_case(lambda d: d["source"].update(duration_s=float("nan")))[0])
        self.assertTrue(self.run_case(lambda d: d["output"].update(fps=True))[0])

    def test_path_traversal(self):
        self.assertTrue(self.run_case(lambda d: d["source"].update(path="../secret.mp4"))[0])

    def test_unknown_asset(self):
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(asset="missing"))[0])

    def test_fake_ui(self):
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(visual_type="real_ui"))[0])

    def test_missing_asset(self):
        errors, warnings = self.run_case(lambda d: d["assets"][0].update(status="missing"))
        self.assertFalse(errors)
        self.assertTrue(warnings)

    def test_bad_shapes(self):
        self.assertTrue(validate([], ".")[0])
        self.assertTrue(self.run_case(lambda d: d.update(assets=[None], segments=[None]))[0])
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(visual_type=[], claim_status=[]))[0])

    def test_generated_evidence(self):
        self.assertTrue(self.run_case(lambda d: d["assets"][0].update(origin="generated", verification="verified"))[0])

    def test_missing_file(self):
        self.assertTrue(self.run_case(lambda d: d["source"].update(path="absent.mp4"), True)[0])

    def test_three_layouts(self):
        self.assertEqual(self.run_case(lambda d: d["segments"][0].update(layout="presenter_full")), ([], []))
        self.assertEqual(self.run_case(lambda d: d["segments"][1].update(layout="broll_full_circle")), ([], []))
        self.assertTrue(self.run_case(lambda d: d["segments"][1].update(layout="broll_full_circle", presenter_visible=False))[0])

    def test_progress_bar(self):
        self.assertEqual(self.run_case(lambda d: d.update(progress_bar={"enabled": True, "mode": "whole_video", "placement": "fixed_canvas", "anchor": "top"})), ([], []))
        self.assertTrue(self.run_case(lambda d: d.update(progress_bar={"enabled": True, "mode": "per_clip", "placement": "fixed_canvas", "anchor": "top"}))[0])
        self.assertTrue(self.run_case(lambda d: d.update(progress_bar={"enabled": True, "mode": "whole_video", "placement": "layout_adaptive"}))[0])

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            root = Path(folder)
            (root / "source.mp4").symlink_to(Path(outside) / "source.mp4")
            self.assertTrue(validate(copy.deepcopy(BASE), root)[0])

    def test_motion_valid(self):
        self.assertEqual(self.run_case(lambda d: d.update(motion_requirement="semantic", motions=[copy.deepcopy(MOTION)])), ([], []))

    def test_semantic_motion_missing(self):
        self.assertTrue(self.run_case(lambda d: d.update(motion_requirement="semantic"))[1])

    def test_progress_motion_not_broll(self):
        self.assertTrue(self.run_case(lambda d: d.update(motion_requirement="semantic", motions=[{**MOTION, "layer": "progress"}]))[1])

    def test_motion_timing(self):
        self.assertTrue(self.run_case(lambda d: d.update(motions=[{**MOTION, "start": 3.5, "end": 4.2}]))[0])
        self.assertTrue(self.run_case(lambda d: d.update(motions=[{**MOTION, "duration_s": 2}]))[0])

    def test_motion_missing_state(self):
        self.assertTrue(self.run_case(lambda d: d.update(motions=[{**MOTION, "state_to": {}}]))[0])

    def test_motion_unknown_segment(self):
        self.assertTrue(self.run_case(lambda d: d.update(motions=[{**MOTION, "segment_id": "unknown"}]))[0])

    def test_intentional_stillness(self):
        def change(d):
            d["motion_requirement"] = "semantic"
            d["segments"][1]["hold_reason"] = "保持已出现的证据供观众读完"
        self.assertEqual(self.run_case(change), ([], []))

    def test_bad_motion_shapes(self):
        self.assertTrue(self.run_case(lambda d: d.update(motions=[None]))[0])
        self.assertTrue(self.run_case(lambda d: d.update(motions="bad"))[0])


if __name__ == "__main__":
    unittest.main()
