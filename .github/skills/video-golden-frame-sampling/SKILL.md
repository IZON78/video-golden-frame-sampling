---
name: video-golden-frame-sampling
description: "Use when analyzing, summarizing, transcribing, or answering questions about a video: sample frames with recursive golden-ratio timing, prioritize longer intervals, compare visual overlap/repetition, and stop subdividing when each interval is shorter than 0.5 seconds. Useful for slideshows, PPT recordings, and videos made from still images."
---

# Video Golden-Ratio Frame Sampling

Use this workflow before reasoning about video content. It creates a temporal set of representative frames so that static slides, repeated images, and scene changes can be distinguished without treating every video frame as unique.

## Procedure

1. **Check the input and tools.** Identify the actual video file, preserve the original, and check that `ffmpeg` and `ffprobe` are available. If they are missing, explain the prerequisite instead of silently substituting another sampling method.
2. **Get the video duration.** Prefer the first video stream's duration; fall back to the container duration if needed. Do not infer the duration from file size.
3. **Extract golden-ratio samples.** Run the bundled [extractor](./scripts/extract_golden_frames.py). For each interval `[start, end]`, it samples the golden cut `start + 0.618 × (end - start)`, then subdivides the two child intervals. It visits the longer child first (the short child is still processed later so the whole video is covered). It stops subdividing a branch once its interval is at most 0.5 seconds. Samples are finally listed in chronological order.
4. **Inspect repetition and changes.** Compare neighboring sampled frames in timestamp order. Group visually identical or near-identical frames as the same slide/image; note transition times and genuinely new content. For PPT/slideshow videos, report slide changes rather than describing repeated samples as new scenes. Do not claim a precise numeric overlap percentage unless an actual image-comparison measurement was run.
5. **Account for limits.** A 0.5-second stopping threshold can miss a very brief transition or flash. If that matters, rerun with a smaller `--min-span`. For a long video, check the estimated/output frame count before opening every image; inspect a contact sheet or a representative subset when available.
6. **Report evidence.** Include video duration, sampling threshold, output folder, approximate sample count, notable timestamps, and any uncertainty. Do not overwrite or redistribute the source video.

## Run the extractor

From the repository root:

```bash
python3 .github/skills/video-golden-frame-sampling/scripts/extract_golden_frames.py /path/to/video.mp4 --output /path/to/frames
```

Optional finer sampling:

```bash
python3 .github/skills/video-golden-frame-sampling/scripts/extract_golden_frames.py /path/to/video.mp4 --output /path/to/frames --min-span 0.25
```

The output folder contains numbered JPEG frames and `manifest.csv` with each sample timestamp, parent interval, and recursion depth. The script requires Python 3 and the `ffmpeg`/`ffprobe` executables; it has no Python package dependencies.

## Current limitations

- The extractor samples both child intervals recursively to cover the full duration; it does not yet switch to fixed-interval sampling when repeated frames exceed a similarity threshold.
- Similarity/overlap assessment is a visual reasoning step for the agent, not a numeric image-comparison feature in the script.
