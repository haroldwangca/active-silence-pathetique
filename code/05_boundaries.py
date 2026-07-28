#!/usr/bin/env python3
"""Regenerate source-condition event boundary metadata from local audio."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import subprocess
import sys
from pathlib import Path


def load_detect_module():
    path = Path(__file__).with_name("01_detect.py")
    spec = importlib.util.spec_from_file_location("detect_module", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


detect_module = load_detect_module()
build_boundary_rows = detect_module.build_boundary_rows
detect_silences = detect_module.detect_silences
load_manifest = detect_module.load_manifest
resolve_audio_path = detect_module.resolve_audio_path
select_pause_events = detect_module.select_pause_events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", required=True, type=Path)
    parser.add_argument("--manifest", default=Path("data/manifest.csv"), type=Path)
    parser.add_argument("--output", default=Path("data/pause_boundaries_source.csv"), type=Path)
    parser.add_argument("--failures-output", default=Path("data/pause_boundaries_failures.csv"), type=Path)
    parser.add_argument("--noise-db", default=-35, type=int)
    parser.add_argument("--min-duration", default=0.10, type=float)
    args = parser.parse_args()

    rows = []
    failures = []
    for item in load_manifest(args.manifest):
        try:
            audio_path = resolve_audio_path(args.audio_dir, item["recording_id"], item["pianist"])
            duration_probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(audio_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            total_duration = float(duration_probe.stdout.strip())
            silences = detect_silences(audio_path, noise_db=args.noise_db, min_duration=args.min_duration)
            selected = select_pause_events(silences, total_duration)
        except Exception as exc:
            failures.append(
                {
                    "recording_id": item["recording_id"],
                    "pianist": item["pianist"],
                    "error": str(exc),
                }
            )
            continue
        rows.extend(build_boundary_rows(item, silences, selected, f"{args.noise_db}dB_{args.min_duration:.2f}s"))
    rows.sort(key=lambda row: (row["recording_id"], row["pause"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with args.failures_output.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["recording_id", "pianist", "error"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failures)
    print(f"Wrote {len(rows)} boundary rows to {args.output}")
    print(f"Wrote {len(failures)} boundary failures to {args.failures_output}")


if __name__ == "__main__":
    main()
