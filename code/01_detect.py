#!/usr/bin/env python3
"""Baseline ffmpeg silencedetect extraction with fixed order constraints."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)\s+\|\s+silence_duration:\s*([0-9.]+)")
EXTENSIONS = [".wav", ".mp3", ".flac", ".m4a", ".aiff", ".aif"]
EVENTS = ["P1", "P2", "P3", "P4"]


@dataclass
class SilenceInterval:
    start: float
    end: float
    duration: float


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [
        row
        for row in rows
        if "Historical extension only" not in row["notes"] and "Deduplicated:" not in row["notes"]
    ]


def detect_silences(audio_path: Path, noise_db: int = -35, min_duration: float = 0.10) -> list[SilenceInterval]:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(audio_path),
        "-af",
        f"silencedetect=noise={noise_db}dB:d={min_duration:.2f}",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    text = (proc.stderr or "") + "\n" + (proc.stdout or "")
    starts: list[float] = []
    intervals: list[SilenceInterval] = []
    for line in text.splitlines():
        start_match = SILENCE_START_RE.search(line)
        if start_match:
            starts.append(float(start_match.group(1)))
            continue
        end_match = SILENCE_END_RE.search(line)
        if end_match and starts:
            end = float(end_match.group(1))
            duration = float(end_match.group(2))
            start = starts.pop(0)
            intervals.append(SilenceInterval(start=start, end=end, duration=duration))
    if not intervals:
        raise RuntimeError(f"No silence intervals parsed for {audio_path}")
    return intervals


def select_pause_events(silences: list[SilenceInterval], total_duration_sec: float) -> dict[str, SilenceInterval]:
    analysis_limit_sec = min(max(50.0, total_duration_sec * 0.18), 90.0)
    candidates = [s for s in silences if s.end <= analysis_limit_sec and s.duration >= 0.10]
    if len(candidates) < 4:
        raise RuntimeError("Not enough silence intervals to identify P1-P4")

    lead_in_end = 0.0
    if candidates[0].start == 0.0 and candidates[0].duration >= 2.0:
        lead_in_end = candidates[0].end

    p4 = None
    for idx, silence in enumerate(candidates):
        if silence.start < 35:
            continue
        next_start = candidates[idx + 1].start if idx + 1 < len(candidates) else analysis_limit_sec + 999
        if next_start - silence.end >= 6.0:
            p4 = silence
            break
    if p4 is None:
        for idx, silence in enumerate(candidates):
            if silence.start < 25:
                continue
            next_start = candidates[idx + 1].start if idx + 1 < len(candidates) else analysis_limit_sec + 999
            if next_start - silence.end >= 6.0:
                p4 = silence
                break
    if p4 is None:
        late = [s for s in candidates if s.start >= 25]
        if not late:
            raise RuntimeError("Could not isolate the final Grave caesura")
        p4 = max(late, key=lambda s: (s.start, s.duration))

    def early_candidates(grave_end: float) -> list[SilenceInterval]:
        early_limit = min(25.0, grave_end * 0.45)
        early = [s for s in candidates if s.start >= max(0.2, lead_in_end) and s.end <= early_limit and s.duration >= 0.20]
        if len(early) < 2:
            early = [s for s in candidates if s.start >= max(0.2, lead_in_end) and s.end <= min(28.0, grave_end * 0.55) and s.duration >= 0.12]
        return early

    grave_end = p4.end
    early = early_candidates(grave_end)
    if len(early) < 2:
        later_options = [s for s in candidates if s.start >= 35.0]
        if not later_options:
            later_options = [s for s in candidates if s.start >= 20.0]
        if later_options:
            p4 = max(later_options, key=lambda s: (s.start, s.duration))
            grave_end = p4.end
            early = early_candidates(grave_end)
    if len(early) < 2:
        early = [s for s in candidates if s.start >= max(0.2, lead_in_end) and s.start < 22.5 and s.duration >= 0.12]
    if len(early) < 2:
        raise RuntimeError("Could not isolate the two early Grave pauses")

    p1 = early[0]
    p2 = early[1]
    late_window = [s for s in candidates if s.start >= max(20.0, grave_end * 0.55) and s.end < p4.start]
    if not late_window:
        late_window = [s for s in candidates if s.end < p4.start and s.start >= 20.0]
    if not late_window:
        raise RuntimeError("Could not isolate the late Grave pause before the final caesura")
    p3 = max(late_window, key=lambda s: (s.duration, s.start))
    return {"P1": p1, "P2": p2, "P3": p3, "P4": p4}


def resolve_audio_path(audio_dir: Path, recording_id: str, pianist: str) -> Path:
    stems = [recording_id, pianist, pianist.replace(" ", "_"), pianist.replace(" ", "")]
    for stem in stems:
        for ext in EXTENSIONS:
            candidate = audio_dir / f"{stem}{ext}"
            if candidate.exists():
                return candidate
    for path in audio_dir.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in EXTENSIONS:
            continue
        stem = path.stem.lower()
        if stem == recording_id.lower() or stem == pianist.lower():
            return path
    raise FileNotFoundError(f"Could not find audio for {recording_id} / {pianist} in {audio_dir}")


def build_boundary_rows(
    manifest_row: dict[str, str],
    silences: list[SilenceInterval],
    selected: dict[str, SilenceInterval],
    threshold_setting: str,
) -> list[dict[str, str]]:
    silence_to_index = {id(s): idx for idx, s in enumerate(silences)}
    rows = []
    for event_id in EVENTS:
        silence = selected[event_id]
        idx = silence_to_index[id(silence)]
        prev_end = silences[idx - 1].end if idx > 0 else 0.0
        sound_duration = max(0.0, silence.start - prev_end)
        rows.append(
            {
                "recording_id": manifest_row["recording_id"],
                "pianist": manifest_row["pianist"],
                "pause": event_id,
                "event_start": f"{prev_end:.3f}",
                "silence_start": f"{silence.start:.3f}",
                "silence_end": f"{silence.end:.3f}",
                "event_end": f"{silence.end:.3f}",
                "d_s": f"{sound_duration:.3f}",
                "d_l": f"{silence.duration:.3f}",
                "threshold_setting": threshold_setting,
            }
        )
    return rows


def event_rows_from_boundary_rows(boundary_rows: list[dict[str, str]], condition: str = "source") -> list[dict[str, str]]:
    rows = []
    for row in boundary_rows:
        event_span = float(row["d_s"]) + float(row["d_l"])
        rows.append(
            {
                "recording_id": row["recording_id"],
                "pianist": row["pianist"],
                "pause": row["pause"],
                "d_s": row["d_s"],
                "d_l": row["d_l"],
                "T": f"{event_span:.3f}",
                "condition": condition,
                "threshold_setting": row["threshold_setting"],
            }
        )
    return rows


def build_rows(manifest_row: dict[str, str], silences: list[SilenceInterval], selected: dict[str, SilenceInterval], threshold_setting: str) -> list[dict[str, str]]:
    """Build event rows through the boundary representation.

    Boundary rows are the single source of truth for source-condition d_s/d_l.
    Keeping this projection explicit prevents the demo and paper table from
    measuring the same pause with two independent rulers.
    """
    return event_rows_from_boundary_rows(
        build_boundary_rows(manifest_row, silences, selected, threshold_setting),
        condition="source",
    )


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", required=True, type=Path)
    parser.add_argument("--manifest", default=Path("data/manifest.csv"), type=Path)
    parser.add_argument("--output", default=Path("data/events.csv"), type=Path)
    parser.add_argument("--boundaries-output", default=Path("data/pause_boundaries_source.csv"), type=Path)
    parser.add_argument("--failures-output", default=Path("data/pause_boundaries_failures.csv"), type=Path)
    parser.add_argument("--noise-db", default=-35, type=int)
    parser.add_argument("--min-duration", default=0.10, type=float)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    threshold_setting = f"{args.noise_db}dB_{args.min_duration:.2f}s"
    event_rows: list[dict[str, str]] = []
    boundary_rows: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
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
            silences = detect_silences(audio_path, noise_db=args.noise_db, min_duration=args.min_duration)
            selected = select_pause_events(silences, total_duration)
            item_boundary_rows = build_boundary_rows(item, silences, selected, threshold_setting)
        except Exception as exc:
            failures.append(
                {
                    "recording_id": item["recording_id"],
                    "pianist": item["pianist"],
                    "error": str(exc),
                }
            )
            continue
        boundary_rows.extend(item_boundary_rows)
        event_rows.extend(event_rows_from_boundary_rows(item_boundary_rows, condition="source"))
    event_rows.sort(key=lambda row: (row["recording_id"], row["pause"]))
    boundary_rows.sort(key=lambda row: (row["recording_id"], row["pause"]))
    write_rows(args.output, event_rows)
    write_rows(args.boundaries_output, boundary_rows)
    args.failures_output.parent.mkdir(parents=True, exist_ok=True)
    with args.failures_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["recording_id", "pianist", "error"])
        writer.writeheader()
        writer.writerows(failures)
    print(f"Wrote {len(event_rows)} baseline rows to {args.output}")
    print(f"Wrote {len(boundary_rows)} boundary rows to {args.boundaries_output}")
    print(f"Wrote {len(failures)} boundary failures to {args.failures_output}")


if __name__ == "__main__":
    main()
