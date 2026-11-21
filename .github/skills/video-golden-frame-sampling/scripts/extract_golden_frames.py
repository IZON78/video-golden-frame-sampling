#!/usr/bin/env python3
"""Extract recursively sampled video frames using golden-ratio cuts."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

GOLDEN_CUT = (5**0.5 - 1) / 2  # 0.618..., measured from the interval start.


@dataclass(frozen=True)
class Sample:
    timestamp: float
    interval_start: float
    interval_end: float
    depth: int


def probe_duration(video: Path) -> float:
    """Return video-stream duration, falling back to container duration."""
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,duration",
        "-of",
        "json",
        str(video),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    metadata = json.loads(result.stdout)

    for stream in metadata.get("streams", []):
        if stream.get("codec_type") == "video" and stream.get("duration"):
            duration = float(stream["duration"])
            if duration > 0:
                return duration

    duration = metadata.get("format", {}).get("duration")
    if duration:
        duration = float(duration)
        if duration > 0:
            return duration
    raise ValueError("ffprobe did not report a positive video/container duration")


def collect_samples(duration: float, min_span: float) -> list[Sample]:
    """Split every long interval, visiting the longer golden section first."""
    samples: list[Sample] = []

    def subdivide(start: float, end: float, depth: int) -> None:
        span = end - start
        if span <= min_span:
            return

        timestamp = start + GOLDEN_CUT * span
        samples.append(Sample(timestamp, start, end, depth))

        # The left child is the longer golden section (0.618 of the parent).
        cut = timestamp
        subdivide(start, cut, depth + 1)
        subdivide(cut, end, depth + 1)

    subdivide(0.0, duration, 0)
    return sorted(samples, key=lambda sample: sample.timestamp)


def extract_frame(video: Path, output_path: Path, timestamp: float) -> None:
    command = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{timestamp:.6f}",
        "-i",
        str(video),
        "-map",
        "0:v:0",
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract frames at recursive golden-ratio cuts; process the longer "
            "interval first and stop subdividing intervals at --min-span."
        )
    )
    parser.add_argument("video", type=Path, help="input video file")
    parser.add_argument("--output", type=Path, required=True, help="output directory")
    parser.add_argument(
        "--min-span",
        type=float,
        default=0.5,
        help="stop subdividing an interval at or below this many seconds (default: 0.5)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video = args.video.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not video.is_file():
        print(f"Input video not found: {video}", file=sys.stderr)
        return 2
    if args.min_span <= 0:
        print("--min-span must be greater than zero", file=sys.stderr)
        return 2
    missing_tools = [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]
    if missing_tools:
        print(f"Required executable(s) not found: {', '.join(missing_tools)}", file=sys.stderr)
        return 2

    try:
        duration = probe_duration(video)
        samples = collect_samples(duration, args.min_span)
        output.mkdir(parents=True, exist_ok=True)

        manifest_path = output / "manifest.csv"
        with manifest_path.open("w", newline="", encoding="utf-8") as manifest_file:
            writer = csv.writer(manifest_file)
            writer.writerow(
                ["frame", "timestamp_seconds", "interval_start_seconds", "interval_end_seconds", "depth"]
            )
            for index, sample in enumerate(samples, start=1):
                frame_name = f"frame_{index:05d}_{sample.timestamp:012.6f}s.jpg"
                extract_frame(video, output / frame_name, sample.timestamp)
                writer.writerow(
                    [
                        frame_name,
                        f"{sample.timestamp:.6f}",
                        f"{sample.interval_start:.6f}",
                        f"{sample.interval_end:.6f}",
                        sample.depth,
                    ]
                )
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Frame extraction failed: {error}", file=sys.stderr)
        return 1

    print(f"Video duration: {duration:.3f} seconds")
    print(f"Minimum interval: {args.min_span:.3f} seconds")
    print(f"Frames extracted: {len(samples)}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
