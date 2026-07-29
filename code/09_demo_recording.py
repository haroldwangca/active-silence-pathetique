#!/usr/bin/env python3
"""Prepare the author-owned Grave recording for the public demo.

The output is intentionally separate from the 16-recording corpus. The recording
is used as a demonstration and MIDI/audio validation artifact, not as an
additional professional corpus row.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import statistics
import struct
import subprocess
import sys
import wave
from pathlib import Path


def load_module(filename: str, name: str):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


detect_module = load_module("01_detect.py", "detect_module")
waveform_module = load_module("07_waveform_panels.py", "waveform_module")

SilenceInterval = detect_module.SilenceInterval
detect_silences = detect_module.detect_silences
draw_panel = waveform_module.draw_panel


def read_vlq(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos


def parse_midi_note_times(path: Path) -> tuple[list[float], list[float]]:
    data = path.read_bytes()
    pos = 0

    def read(count: int) -> bytes:
        nonlocal pos
        chunk = data[pos : pos + count]
        pos += count
        return chunk

    if read(4) != b"MThd":
        raise ValueError(f"{path} is not a standard MIDI file")
    header_length = struct.unpack(">I", read(4))[0]
    _, track_count, division = struct.unpack(">HHH", read(header_length))
    if division & 0x8000:
        raise ValueError("SMPTE MIDI timing is not supported")

    note_events: list[tuple[int, str]] = []
    tempo_events: list[tuple[int, int]] = [(0, 500000)]
    for _ in range(track_count):
        if read(4) != b"MTrk":
            raise ValueError("Missing MIDI track header")
        track_length = struct.unpack(">I", read(4))[0]
        track_end = pos + track_length
        tick = 0
        running_status: int | None = None
        while pos < track_end:
            delta, pos = read_vlq(data, pos)
            tick += delta
            status = data[pos]
            if status < 0x80:
                if running_status is None:
                    raise ValueError("MIDI running status without prior status")
                status = running_status
            else:
                pos += 1
                if status < 0xF0:
                    running_status = status
            if status == 0xFF:
                event_type = data[pos]
                pos += 1
                length, pos = read_vlq(data, pos)
                payload = data[pos : pos + length]
                pos += length
                if event_type == 0x51 and length == 3:
                    tempo_events.append((tick, int.from_bytes(payload, "big")))
                if event_type == 0x2F:
                    break
            elif status in (0xF0, 0xF7):
                length, pos = read_vlq(data, pos)
                pos += length
            else:
                high = status & 0xF0
                data_len = 1 if high in (0xC0, 0xD0) else 2
                values = data[pos : pos + data_len]
                pos += data_len
                if high in (0x80, 0x90):
                    velocity = values[1] if data_len == 2 else 0
                    if high == 0x90 and velocity > 0:
                        note_events.append((tick, "on"))
                    else:
                        note_events.append((tick, "off"))
        pos = track_end

    tempo_events = sorted(set(tempo_events))

    def tick_to_seconds(target_tick: int) -> float:
        elapsed = 0.0
        last_tick = 0
        tempo = 500000
        for tempo_tick, tempo_us in tempo_events:
            if tempo_tick > target_tick:
                break
            elapsed += (tempo_tick - last_tick) * tempo / 1_000_000 / division
            last_tick = tempo_tick
            tempo = tempo_us
        elapsed += (target_tick - last_tick) * tempo / 1_000_000 / division
        return elapsed

    onsets = [tick_to_seconds(tick) for tick, kind in note_events if kind == "on"]
    offsets = [tick_to_seconds(tick) for tick, kind in note_events if kind == "off"]
    if not onsets or not offsets:
        raise ValueError("No MIDI note on/off events found")
    return sorted(onsets), sorted(offsets)


def probe_duration(path: Path) -> float:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(proc.stdout.strip())


def select_demo_pauses(
    silences: list[SilenceInterval],
    first_audio_onset: float,
    total_duration: float,
) -> dict[str, SilenceInterval]:
    analysis_limit = min(max(50.0, total_duration * 0.18), 90.0)
    candidates = [
        silence
        for silence in silences
        if silence.start >= first_audio_onset - 0.25
        and silence.end <= analysis_limit
        and silence.duration >= 0.10
    ]
    if len(candidates) < 4:
        raise RuntimeError("Not enough post-onset silences to identify demo P1-P4")

    p4 = None
    for idx, silence in enumerate(candidates):
        if silence.start < 35:
            continue
        next_start = candidates[idx + 1].start if idx + 1 < len(candidates) else analysis_limit + 999
        if next_start - silence.end >= 6.0:
            p4 = silence
            break
    if p4 is None:
        p4 = max([s for s in candidates if s.start >= 25.0], key=lambda s: (s.start, s.duration))

    early = [s for s in candidates if s.start < min(25.0, p4.end * 0.45) and s.duration >= 0.20]
    if len(early) < 2:
        early = [s for s in candidates if s.start < min(28.0, p4.end * 0.55) and s.duration >= 0.12]
    if len(early) < 2:
        raise RuntimeError("Could not isolate demo P1/P2")

    late_window = [s for s in candidates if s.start >= max(20.0, p4.end * 0.55) and s.end < p4.start]
    if not late_window:
        raise RuntimeError("Could not isolate demo P3")

    return {
        "P1": early[0],
        "P2": early[1],
        "P3": max(late_window, key=lambda s: (s.duration, s.start)),
        "P4": p4,
    }


def room_tone_stats(audio_path: Path, first_midi_onset: float, temp_wav: Path) -> dict[str, str]:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-i",
            str(audio_path),
            "-ac",
            "1",
            "-ar",
            "11025",
            "-sample_fmt",
            "s16",
            str(temp_wav),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    with wave.open(str(temp_wav), "rb") as handle:
        sample_rate = handle.getframerate()
        frames = handle.readframes(min(handle.getnframes(), int(first_midi_onset * sample_rate)))
    values = [
        int.from_bytes(frames[i : i + 2], byteorder="little", signed=True) / 32768.0
        for i in range(0, len(frames), 2)
    ]
    if not values:
        return {"room_tone_sec": "0.000", "room_tone_rms_dbfs": "", "room_tone_peak_dbfs": ""}
    rms = math.sqrt(statistics.mean(value * value for value in values))
    peak = max(abs(value) for value in values)

    def dbfs(value: float) -> str:
        if value <= 0:
            return "-inf"
        return f"{20 * math.log10(value):.1f}"

    return {
        "room_tone_sec": f"{first_midi_onset:.3f}",
        "room_tone_rms_dbfs": dbfs(rms),
        "room_tone_peak_dbfs": dbfs(peak),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True, type=Path)
    parser.add_argument("--midi", required=True, type=Path)
    parser.add_argument("--media-audio", default=Path("media/harold_grave.m4a"), type=Path)
    parser.add_argument("--media-midi", default=Path("media/harold_grave.mid"), type=Path)
    parser.add_argument("--events-output", default=Path("data/demo_recording_events.csv"), type=Path)
    parser.add_argument("--boundaries-output", default=Path("data/demo_recording_boundaries.csv"), type=Path)
    parser.add_argument("--midi-output", default=Path("data/demo_recording_midi_release.csv"), type=Path)
    parser.add_argument("--manifest-output", default=Path("data/demo_recording_manifest.csv"), type=Path)
    parser.add_argument("--waveform-dir", default=Path("figures/waveform_panels"), type=Path)
    parser.add_argument(
        "--midi-audio-offset-sec",
        default=4.358,
        type=float,
        help="Constant audio-minus-MIDI offset. The original files are not trimmed.",
    )
    parser.add_argument(
        "--offset-uncertainty-sec",
        default=0.030,
        type=float,
        help="Approximate uncertainty from two manually matched onset pairs.",
    )
    parser.add_argument("--noise-db", default=-35, type=int)
    parser.add_argument("--min-duration", default=0.10, type=float)
    args = parser.parse_args()

    onsets, offsets = parse_midi_note_times(args.midi)
    first_midi_onset = onsets[0]
    midi_audio_offset = args.midi_audio_offset_sec
    offset_uncertainty = args.offset_uncertainty_sec
    first_audio_onset = first_midi_onset + midi_audio_offset
    aligned_offsets = [value + midi_audio_offset for value in offsets]
    total_duration = probe_duration(args.audio)
    silences = detect_silences(args.audio, noise_db=args.noise_db, min_duration=args.min_duration)
    selected = select_demo_pauses(silences, first_audio_onset, total_duration)
    threshold_setting = f"{args.noise_db}dB_{args.min_duration:.2f}s"

    manifest_row = {
        "recording_id": "HW_GRAVE_DEMO",
        "pianist": "Harold Wang",
        "notes": "author-owned demo recording; excluded from corpus statistics",
    }

    boundary_rows: list[dict[str, str]] = []
    event_rows: list[dict[str, str]] = []
    midi_rows: list[dict[str, str]] = []
    previous_end = first_audio_onset
    for pause in ["P1", "P2", "P3", "P4"]:
        silence = selected[pause]
        event_start = max(first_audio_onset, previous_end)
        d_s = max(0.0, silence.start - event_start)
        boundary_row = {
            "recording_id": manifest_row["recording_id"],
            "pianist": manifest_row["pianist"],
            "pause": pause,
            "event_start": f"{event_start:.3f}",
            "silence_start": f"{silence.start:.3f}",
            "silence_end": f"{silence.end:.3f}",
            "event_end": f"{silence.end:.3f}",
            "d_s": f"{d_s:.3f}",
            "d_l": f"{silence.duration:.3f}",
            "threshold_setting": threshold_setting,
        }
        boundary_rows.append(boundary_row)
        event_rows.append(
            {
                "recording_id": manifest_row["recording_id"],
                "pianist": manifest_row["pianist"],
                "pause": pause,
                "d_s": boundary_row["d_s"],
                "d_l": boundary_row["d_l"],
                "T": f"{d_s + silence.duration:.3f}",
                "condition": "demo_recording",
                "threshold_setting": threshold_setting,
            }
        )
        local_offsets = [
            (raw, aligned)
            for raw, aligned in zip(offsets, aligned_offsets)
            if event_start <= aligned <= silence.start
        ]
        release_pair = max(local_offsets, key=lambda pair: pair[1]) if local_offsets else None
        raw_release = release_pair[0] if release_pair else ""
        aligned_release = release_pair[1] if release_pair else ""
        midi_rows.append(
            {
                "recording_id": manifest_row["recording_id"],
                "pause": pause,
                "midi_last_note_off_sec": f"{raw_release:.3f}" if raw_release != "" else "",
                "midi_audio_offset_sec": f"{midi_audio_offset:.3f}",
                "offset_uncertainty_sec": f"{offset_uncertainty:.3f}",
                "aligned_midi_last_note_off_sec": f"{aligned_release:.3f}" if aligned_release != "" else "",
                "audio_silence_start_sec": f"{silence.start:.3f}",
                "audio_minus_midi_release_sec": f"{silence.start - aligned_release:.3f}" if aligned_release != "" else "",
                "interpretation": "positive values mean the fixed audio threshold crossed after the aligned MIDI note-off"
                if aligned_release != ""
                else "no MIDI note-off found in local event window",
            }
        )
        previous_end = silence.end

    room_row = {
        "recording_id": manifest_row["recording_id"],
        "pause": "ROOM_TONE",
        "midi_last_note_off_sec": "",
        "midi_audio_offset_sec": f"{midi_audio_offset:.3f}",
        "offset_uncertainty_sec": f"{offset_uncertainty:.3f}",
        "aligned_midi_last_note_off_sec": "",
        "audio_silence_start_sec": "",
        "audio_minus_midi_release_sec": "",
        "interpretation": "pre-performance room tone measured before the aligned first MIDI onset",
    }
    temp_dir = Path("tmp")
    temp_dir.mkdir(exist_ok=True)
    temp_wav = temp_dir / "harold_grave_demo_11025.wav"
    room_row.update(room_tone_stats(args.audio, first_audio_onset, temp_wav))
    midi_rows.insert(0, room_row)

    write_csv(args.events_output, event_rows)
    write_csv(args.boundaries_output, boundary_rows)
    write_csv(args.midi_output, midi_rows)
    write_csv(
        args.manifest_output,
        [
            {
                "recording_id": manifest_row["recording_id"],
                "pianist": manifest_row["pianist"],
                "audio_file": str(args.media_audio),
                "midi_file": str(args.media_midi),
                "audio_format": "M4A/AAC, 48 kHz mono",
                "duration_sec": f"{total_duration:.3f}",
                "first_midi_onset_sec": f"{first_midi_onset:.3f}",
                "midi_audio_offset_sec": f"{midi_audio_offset:.3f}",
                "offset_uncertainty_sec": f"{offset_uncertainty:.3f}",
                "first_audio_onset_sec": f"{first_audio_onset:.3f}",
                "offset_method": "manual onset matching; MIDI 7.181s -> audio 11.539s and MIDI 10.727s -> audio 15.102s",
                "status": "author-owned demo recording; excluded from corpus statistics",
                "notes": "Used for hosted playback and MIDI/audio boundary illustration only.",
            }
        ],
    )

    args.media_audio.parent.mkdir(parents=True, exist_ok=True)
    args.media_audio.write_bytes(args.audio.read_bytes())
    args.media_midi.write_bytes(args.midi.read_bytes())

    for row in boundary_rows:
        safe_name = f"{row['pianist'].replace(' ', '_')}_{row['pause']}.png"
        draw_panel(temp_wav, row, args.waveform_dir / safe_name)

    print(f"Wrote {len(event_rows)} demo event rows to {args.events_output}")
    print(f"Wrote {len(boundary_rows)} demo boundary rows to {args.boundaries_output}")
    print(f"Wrote {len(midi_rows)} MIDI/audio comparison rows to {args.midi_output}")
    print(f"Wrote demo manifest to {args.manifest_output}")
    print(f"Copied owned audio to {args.media_audio}")
    print(f"Copied MIDI to {args.media_midi}")


if __name__ == "__main__":
    main()
