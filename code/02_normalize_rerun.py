#!/usr/bin/env python3
"""Peak-normalize local audio to -1 dBFS and append the rerun rows to events.csv."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import importlib.util as _importlib_util


def _load_baseline_module():
    here = Path(__file__).resolve().parent
    target = here / "01_detect.py"
    spec = _importlib_util.spec_from_file_location("hb_detect", target)
    module = _importlib_util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load_baseline_module()
MAX_VOLUME_RE = re.compile(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB")
TARGET_PEAK_DBFS = -1.0


def probe_max_volume(audio_path: Path) -> float:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(audio_path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    text = (proc.stderr or "") + "\n" + (proc.stdout or "")
    match = MAX_VOLUME_RE.search(text)
    if not match:
        raise RuntimeError(f"Could not read max_volume for {audio_path}")
    return float(match.group(1))


def normalize_peak(audio_path: Path, output_path: Path, gain_db: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-i", str(audio_path), "-af", f"volume={gain_db:.3f}dB", str(output_path)],
        capture_output=True,
        text=True,
        check=True,
    )


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", required=True, type=Path)
    parser.add_argument("--manifest", default=Path("data/manifest.csv"), type=Path)
    parser.add_argument("--events", default=Path("data/events.csv"), type=Path)
    args = parser.parse_args()

    source_rows = [row for row in read_rows(args.events) if row["condition"] == "source"]
    manifest = BASE.load_manifest(args.manifest)
    rows = list(source_rows)

    with tempfile.TemporaryDirectory(prefix="active-silence-peaknorm-") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for item in manifest:
            audio_path = BASE.resolve_audio_path(args.audio_dir, item["recording_id"], item["pianist"])
            total_duration = float(
                subprocess.run(
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
                ).stdout.strip()
            )
            max_volume = probe_max_volume(audio_path)
            gain_db = TARGET_PEAK_DBFS - max_volume
            normalized_path = tmp_dir / f"{item['recording_id']}.wav"
            normalize_peak(audio_path, normalized_path, gain_db)
            silences = BASE.detect_silences(normalized_path, noise_db=-35, min_duration=0.10)
            selected = BASE.select_pause_events(silences, total_duration)
            rerun_rows = BASE.build_rows(item, silences, selected, "-35dB_0.10s")
            for row in rerun_rows:
                row["condition"] = "peaknorm"
            rows.extend(rerun_rows)

    rows.sort(key=lambda row: (row["recording_id"], row["condition"], row["pause"]))
    write_rows(args.events, rows)
    print(f"Wrote {len(rows)} combined source/peaknorm rows to {args.events}")


if __name__ == "__main__":
    main()
