#!/usr/bin/env python3
"""Check whether two audio files likely contain the same performance.

The script decodes both files to a coarse energy envelope and searches for the
maximum normalized cross-correlation over a small lag window.
"""

from __future__ import annotations

import argparse
import array
import math
import subprocess


def envelope(path: str, sr: int = 200, seconds: int = 90) -> list[float]:
    raw = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            path,
            "-t",
            str(seconds),
            "-ac",
            "1",
            "-ar",
            "8000",
            "-f",
            "s16le",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    pcm = array.array("h")
    pcm.frombytes(raw[: len(raw) // 2 * 2])
    hop = 8000 // sr
    return [
        math.sqrt(sum(value * value for value in pcm[i : i + hop]) / hop + 1e-9)
        for i in range(0, len(pcm) - hop, hop)
    ]


def normalise(values: list[float]) -> list[float]:
    mean = sum(values) / len(values)
    denom = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)) or 1.0
    return [(value - mean) / denom for value in values]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("a")
    parser.add_argument("b")
    parser.add_argument("--max-lag", type=float, default=3.0)
    args = parser.parse_args()

    left = normalise(envelope(args.a))
    right = normalise(envelope(args.b))
    sr = 200
    best = (-2.0, 0)
    for lag in range(-int(args.max_lag * sr), int(args.max_lag * sr) + 1):
        pairs = [(left[i], right[i - lag]) for i in range(len(left)) if 0 <= i - lag < len(right)]
        if len(pairs) < sr * 10:
            continue
        score = sum(x * y for x, y in pairs) / len(pairs)
        best = max(best, (score, lag))

    score, lag = best
    print(f"peak normalized cross-correlation = {score:.3f} at lag {lag / sr:+.3f} s")
    if score > 0.85:
        print("SAME performance")
    elif score < 0.5:
        print("DIFFERENT performances")
    else:
        print("inconclusive")


if __name__ == "__main__":
    main()
