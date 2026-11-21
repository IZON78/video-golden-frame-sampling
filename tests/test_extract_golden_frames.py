import unittest
import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "skills"
    / "video-golden-frame-sampling"
    / "scripts"
    / "extract_golden_frames.py"
)
SPEC = importlib.util.spec_from_file_location("extract_golden_frames", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load extractor module from {SCRIPT_PATH}")
EXTRACTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EXTRACTOR
SPEC.loader.exec_module(EXTRACTOR)
GOLDEN_CUT = EXTRACTOR.GOLDEN_CUT
collect_samples = EXTRACTOR.collect_samples


class CollectSamplesTests(unittest.TestCase):
    def test_includes_initial_interval_golden_cut(self):
        duration = 10.0
        samples = collect_samples(duration, 0.5)

        self.assertTrue(
            any(
                sample.interval_start == 0.0
                and sample.interval_end == duration
                and abs(sample.timestamp - GOLDEN_CUT * duration) < 1e-9
                for sample in samples
            )
        )

    def test_stops_before_subdividing_short_intervals(self):
        min_span = 0.5
        samples = collect_samples(10.0, min_span)

        self.assertTrue(samples)
        self.assertTrue(
            all(sample.interval_end - sample.interval_start > min_span for sample in samples)
        )

    def test_samples_are_returned_in_chronological_order(self):
        samples = collect_samples(10.0, 0.5)

        self.assertEqual(samples, sorted(samples, key=lambda sample: sample.timestamp))

    def test_short_video_needs_no_samples(self):
        self.assertEqual(collect_samples(0.5, 0.5), [])


if __name__ == "__main__":
    unittest.main()
