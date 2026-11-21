# Video Golden-Ratio Frame Sampling

A GitHub Copilot Agent Skill and small Python utility for sampling representative frames from videos. It uses recursive golden-ratio cuts, then helps an agent compare sampled frames to identify repeated slides, static images, and scene changes.

> 当前版本说明 / Current status: the extractor recursively samples both parts of each interval to cover the full video. It does **not** yet calculate a numeric visual-similarity ratio or switch to fixed-interval sampling when repeated frames exceed a configurable threshold.

## Repository contents

- `.github/skills/video-golden-frame-sampling/SKILL.md` — the Agent Skill instructions.
- `.github/skills/video-golden-frame-sampling/scripts/extract_golden_frames.py` — the frame extractor.

## Requirements

- Python 3.10 or later (uses built-in type syntax and dataclasses).
- `ffmpeg` and `ffprobe` installed and available on `PATH`.
- No third-party Python packages.

## Use the extractor

From this repository root, run:

```bash
python3 .github/skills/video-golden-frame-sampling/scripts/extract_golden_frames.py /path/to/video.mp4 --output /path/to/frames
```

To stop subdividing at a different interval length, pass `--min-span`, for example `--min-span 0.25`. The default is 0.5 seconds. Frames are JPEGs; `manifest.csv` records the timestamp, interval, and recursion depth for each sample.

The output path is created if needed. Existing files with the same names are overwritten; use a new output directory to avoid that.

## Install the skill in another workspace

Copy the `video-golden-frame-sampling` folder from `.github/skills/` into the target workspace's `.github/skills/` directory. The resulting path should be:

`.github/skills/video-golden-frame-sampling/SKILL.md`

The bundled script is referenced relative to `SKILL.md` and should be copied with it.

## Sampling method and limitations

For an interval `[start, end]`, the extractor samples at `start + 0.618 × (end - start)`, then recursively processes both child intervals, visiting the longer child first. A branch stops when its interval is at most `--min-span`. Samples are output in chronological order.

Because both child intervals are explored, long videos can generate many frames. A 10-minute video can produce roughly 1,600 frames with the default setting. A 0.5-second threshold may miss brief flashes or transitions. The script extracts frames only; visual repetition assessment is performed by the agent and is not a numeric similarity calculation yet.

## Tests

Run the standard-library tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

## License

No license has been selected yet. Add a license before inviting reuse or contributions, and choose one that matches how you want others to use the project.
