#!/usr/bin/env python3
"""Render waveform validation panels with detected boundary markers."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_detect_module():
    path = Path(__file__).with_name("01_detect.py")
    spec = importlib.util.spec_from_file_location("detect_module", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


detect_module = load_detect_module()
load_manifest = detect_module.load_manifest
resolve_audio_path = detect_module.resolve_audio_path

def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_wav_mono_window(path: Path, start_seconds: float, end_seconds: float) -> tuple[list[float], int, float, float]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        total_frames = handle.getnframes()
        start_frame = max(0, int(start_seconds * sample_rate))
        end_frame = min(total_frames, int(end_seconds * sample_rate))
        handle.setpos(start_frame)
        frames = handle.readframes(max(0, end_frame - start_frame))
    if sample_width != 2:
        raise ValueError(f"{path} is not 16-bit PCM WAV")
    values = []
    for i in range(0, len(frames), sample_width * channels):
        channel_values = []
        for channel in range(channels):
            start = i + channel * sample_width
            sample = int.from_bytes(frames[start : start + sample_width], byteorder="little", signed=True)
            channel_values.append(sample / 32768.0)
        values.append(sum(channel_values) / len(channel_values))
    return values, sample_rate, start_frame / sample_rate, end_frame / sample_rate


def draw_panel(audio_path: Path, row: dict[str, str], out_path: Path) -> None:
    event_start = float(row["event_start"])
    event_end = float(row["event_end"])
    silence_start = float(row["silence_start"])
    silence_end = float(row["silence_end"])
    pad = 0.75
    requested_start = max(0.0, event_start - pad)
    requested_end = event_end + pad
    segment, sample_rate, start, end = read_wav_mono_window(audio_path, requested_start, requested_end)
    width, height = 900, 260
    left, right, top, bottom = 58, 24, 42, 40
    plot_w = width - left - right
    plot_h = height - top - bottom
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((left, 12), f"{row['pianist']} {row['pause']}  d_s={row['d_s']}s  d_l={row['d_l']}s", fill=(0, 0, 0), font=font)
    baseline = top + plot_h / 2
    draw.line((left, baseline, left + plot_w, baseline), fill=(180, 180, 180), width=1)
    stride = max(1, len(segment) // plot_w)
    for x in range(plot_w):
        chunk = segment[x * stride : min(len(segment), (x + 1) * stride)]
        if not chunk:
            continue
        amp = max(abs(value) for value in chunk)
        y0 = baseline - amp * (plot_h / 2)
        y1 = baseline + amp * (plot_h / 2)
        draw.line((left + x, y0, left + x, y1), fill=(65, 65, 65), width=1)

    def x_at(time_seconds: float) -> float:
        return left + ((time_seconds - start) / max(end - start, 1e-9)) * plot_w

    markers = [
        (event_start, "event start", (55, 90, 160)),
        (silence_start, "silence start", (180, 70, 45)),
        (silence_end, "silence end", (45, 130, 75)),
    ]
    for time_seconds, label, color in markers:
        x = x_at(time_seconds)
        draw.line((x, top, x, top + plot_h), fill=color, width=3)
        draw.text((x + 4, top + 4), label, fill=color, font=font)
    draw.text((left, height - 26), f"time window {start:.2f}-{end:.2f}s; boundary metadata from {row['threshold_setting']}", fill=(0, 0, 0), font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", required=True, type=Path)
    parser.add_argument("--boundaries", default=Path("data/pause_boundaries_source.csv"), type=Path)
    parser.add_argument("--manifest", default=Path("data/manifest.csv"), type=Path)
    parser.add_argument("--out-dir", default=Path("figures/waveform_panels"), type=Path)
    parser.add_argument("--recordings", nargs="*", default=None, help="Optional recording IDs; defaults to every boundary row.")
    args = parser.parse_args()

    manifest = {row["recording_id"]: row for row in load_manifest(args.manifest)}
    boundary_rows = read_rows(args.boundaries)
    if args.recordings:
        rows = [row for row in boundary_rows if row["recording_id"] in set(args.recordings)]
    else:
        rows = boundary_rows
    for row in rows:
        manifest_row = manifest[row["recording_id"]]
        audio_path = resolve_audio_path(args.audio_dir, manifest_row["recording_id"], manifest_row["pianist"])
        safe_name = f"{row['pianist'].replace(' ', '_')}_{row['pause']}.png"
        draw_panel(audio_path, row, args.out_dir / safe_name)
    print(f"Wrote {len(rows)} waveform panels to {args.out_dir}")


if __name__ == "__main__":
    main()
