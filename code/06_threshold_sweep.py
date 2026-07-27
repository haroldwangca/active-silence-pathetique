#!/usr/bin/env python3
"""Regenerate aggregate threshold-sensitivity counts from local audio."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import subprocess
import sys
from collections import Counter, defaultdict
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
build_rows = detect_module.build_rows
detect_silences = detect_module.detect_silences
load_manifest = detect_module.load_manifest
resolve_audio_path = detect_module.resolve_audio_path
select_pause_events = detect_module.select_pause_events

SETTINGS = [(-30, 0.08), (-30, 0.10), (-30, 0.15), (-35, 0.08), (-35, 0.10), (-35, 0.15), (-40, 0.08), (-40, 0.10), (-40, 0.15)]
EVENTS = ["P1", "P2", "P3", "P4"]


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def covariance(xs: list[float], ys: list[float]) -> float:
    mx = mean(xs)
    my = mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)


def summarize(rows: list[dict[str, str]], failed_count: int, threshold_setting: str) -> dict[str, object]:
    by_pause = defaultdict(list)
    by_recording = defaultdict(dict)
    for row in rows:
        by_pause[row["pause"]].append(row)
        by_recording[row["recording_id"]][row["pause"]] = row

    silence_ratios = {
        pause: [float(row["d_l"]) / max(float(row["T"]), 1e-12) for row in by_pause[pause]]
        for pause in EVENTS
    }
    ordered = sorted(["P1", "P2", "P3"], key=lambda pause: mean(silence_ratios[pause]), reverse=True)
    peak_counts = Counter()
    strategy_counts = Counter()
    p2_gt_p1 = 0
    p3_gt_p1 = 0
    for event_map in by_recording.values():
        dl = {pause: float(event_map[pause]["d_l"]) for pause in EVENTS}
        ds = {pause: float(event_map[pause]["d_s"]) for pause in EVENTS}
        peak_counts[max(EVENTS, key=lambda pause: (dl[pause], pause))] += 1
        p2_gt_p1 += int(dl["P2"] > dl["P1"])
        p3_gt_p1 += int(dl["P3"] > dl["P1"])
        ds_values = [ds[pause] for pause in EVENTS]
        dl_values = [dl[pause] for pause in EVENTS]
        strategy_counts["compensating" if covariance(ds_values, dl_values) < 0 else "additive"] += 1

    result = {
        "threshold_setting": threshold_setting,
        "mean_order_P1_P3": " > ".join(ordered),
        "p2_gt_p1_count": p2_gt_p1,
        "p3_gt_p1_count": p3_gt_p1,
        "failed_count": failed_count,
    }
    for pause in EVENTS:
        result[f"peak_{pause}"] = peak_counts.get(pause, 0)
    result["compensating_count"] = strategy_counts.get("compensating", 0)
    result["additive_count"] = strategy_counts.get("additive", 0)
    for pause in EVENTS:
        result[f"{pause}_mean_silence_ratio"] = f"{mean(silence_ratios[pause]):.6f}"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", required=True, type=Path)
    parser.add_argument("--manifest", default=Path("data/manifest.csv"), type=Path)
    parser.add_argument("--output", default=Path("data/threshold_sweep.csv"), type=Path)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    rows = []
    for noise_db, min_duration in SETTINGS:
        setting = f"{noise_db}dB_{min_duration:.2f}s"
        setting_rows = []
        failed_count = 0
        for item in manifest:
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
                silences = detect_silences(audio_path, noise_db=noise_db, min_duration=min_duration)
                selected = select_pause_events(silences, total_duration)
                setting_rows.extend(build_rows(item, silences, selected, setting))
            except Exception:
                failed_count += 1
        rows.append(summarize(setting_rows, failed_count, setting))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} threshold settings to {args.output}")


if __name__ == "__main__":
    main()
