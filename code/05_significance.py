#!/usr/bin/env python3
"""Compute supplementary significance checks from shipped event features."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

EVENTS = ["P1", "P2", "P3", "P4"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def average_ranks_desc(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1], reverse=True)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and abs(indexed[j][1] - indexed[i][1]) <= 1e-9:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def kendalls_w(rank_rows: list[list[float]]) -> float:
    m = len(rank_rows)
    n = len(rank_rows[0])
    item_totals = [sum(row[j] for row in rank_rows) for j in range(n)]
    mean_total = sum(item_totals) / n
    s_val = sum((total - mean_total) ** 2 for total in item_totals)
    tie_correction = 0.0
    for row in rank_rows:
        counts = Counter(row)
        tie_correction += sum(count**3 - count for count in counts.values() if count > 1)
    denom = (m**2) * (n**3 - n) - m * tie_correction
    return 12 * s_val / denom


def chi_square_sf(x: float, df: int) -> float:
    if df == 1:
        return math.erfc(math.sqrt(x / 2.0))
    if df == 2:
        return math.exp(-x / 2.0)
    if df == 3:
        z = math.sqrt(x / 2.0)
        return math.erfc(z) + (2.0 / math.sqrt(math.pi)) * z * math.exp(-(z**2))
    raise ValueError("Only df=1,2,3 are needed for this analysis.")


def kendall_test(by_pianist: dict[str, dict[str, float]], events: list[str]) -> dict[str, float]:
    rank_rows = [average_ranks_desc([event_map[event] for event in events]) for event_map in by_pianist.values()]
    w_value = kendalls_w(rank_rows)
    n_recordings = len(rank_rows)
    df = len(events) - 1
    chi_square = n_recordings * df * w_value
    return {
        "events": ",".join(events),
        "kendalls_w": w_value,
        "chi_square": chi_square,
        "df": df,
        "p_value": chi_square_sf(chi_square, df),
    }


def kendall_permutation_p(
    by_pianist: dict[str, dict[str, float]],
    events: list[str],
    n_shuffles: int = 200_000,
    seed: int = 20260728,
) -> dict[str, float]:
    rank_rows = [average_ranks_desc([event_map[event] for event in events]) for event_map in by_pianist.values()]
    observed = kendalls_w(rank_rows)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_shuffles):
        shuffled_rows = [rng.sample(row, len(row)) for row in rank_rows]
        if kendalls_w(shuffled_rows) >= observed - 1e-12:
            extreme += 1
    return {
        "events": ",".join(events),
        "observed_w": observed,
        "n_shuffles": n_shuffles,
        "seed": seed,
        "p_value": extreme / n_shuffles,
    }


def two_sided_binomial_at_least_extreme(successes: int, n_trials: int) -> float:
    successes = max(successes, n_trials - successes)
    tail = sum(math.comb(n_trials, k) for k in range(successes, n_trials + 1)) / (2**n_trials)
    return min(1.0, 2 * tail)


def wilcoxon_p2_p3(by_pianist: dict[str, dict[str, float]]) -> dict[str, float]:
    diffs = [event_map["P2"] - event_map["P3"] for event_map in by_pianist.values()]
    abs_pairs = sorted((abs(diff), 1 if diff > 0 else -1, diff) for diff in diffs if abs(diff) > 1e-12)
    ranks = []
    i = 0
    while i < len(abs_pairs):
        j = i + 1
        while j < len(abs_pairs) and abs(abs_pairs[j][0] - abs_pairs[i][0]) <= 1e-12:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks.append((avg_rank, abs_pairs[k][1]))
        i = j
    n = len(ranks)
    w_plus = sum(rank for rank, sign in ranks if sign > 0)
    w_minus = sum(rank for rank, sign in ranks if sign < 0)
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    z_value = (w_plus - mean_w) / math.sqrt(var_w)
    normal_p = math.erfc(abs(z_value) / math.sqrt(2.0))
    rank_values = [rank for rank, _ in ranks]
    observed_min = min(w_plus, w_minus)
    total_rank_sum = sum(rank_values)
    sums = []
    for signs in product([0, 1], repeat=n):
        sums.append(sum(rank for rank, sign in zip(rank_values, signs) if sign))
    exact_p = sum(1 for value in sums if value <= observed_min or value >= total_rank_sum - observed_min) / len(sums)
    return {
        "n": n,
        "w_plus": w_plus,
        "w_minus": w_minus,
        "z_normal_approx": z_value,
        "p_normal_approx": normal_p,
        "p_exact_signed_rank": exact_p,
    }


def paired_p2_minus_p3_effect(by_pianist: dict[str, dict[str, float]]) -> dict[str, float]:
    diffs = [event_map["P2"] - event_map["P3"] for event_map in by_pianist.values()]
    n = len(diffs)
    mean_diff = sum(diffs) / n
    sd = (sum((value - mean_diff) ** 2 for value in diffs) / (n - 1)) ** 0.5
    se = sd / math.sqrt(n)
    tcrit_975_by_df = {15: 2.131, 16: 2.120}
    tcrit = tcrit_975_by_df.get(n - 1, 1.96)
    return {
        "n": n,
        "mean_seconds": round(mean_diff, 3),
        "sd": round(sd, 3),
        "ci95_low": round(mean_diff - tcrit * se, 3),
        "ci95_high": round(mean_diff + tcrit * se, 3),
        "cohens_dz": round(mean_diff / sd, 3),
    }


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    rows = [row for row in read_rows(base / "data/events.csv") if row["condition"] == "source"]
    by_pianist: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        by_pianist[row["pianist"]][row["pause"]] = float(row["d_l"])

    peak_counts = Counter(max(EVENTS, key=lambda event: (event_map[event], event)) for event_map in by_pianist.values())
    p2_p3_trials = peak_counts.get("P2", 0) + peak_counts.get("P3", 0)
    p2_p3_successes = max(peak_counts.get("P2", 0), peak_counts.get("P3", 0))
    results = {
        "peak_counts": dict(peak_counts),
        "modal_peak_binomial_p_two_sided_p2_vs_p3": two_sided_binomial_at_least_extreme(p2_p3_successes, p2_p3_trials),
        "paired_p2_minus_p3_effect": paired_p2_minus_p3_effect(by_pianist),
        "wilcoxon_p2_minus_p3": wilcoxon_p2_p3(by_pianist),
        "kendall_all_four": kendall_test(by_pianist, EVENTS),
        "kendall_all_four_permutation": kendall_permutation_p(by_pianist, EVENTS),
        "kendall_without_p4": kendall_test(by_pianist, ["P1", "P2", "P3"]),
        "kendall_p2_p3_only": kendall_test(by_pianist, ["P2", "P3"]),
        "interpretation": (
            "The shipped source-condition data cannot separate P2 and P3 reliably; "
            "the all-four Kendall W is driven mainly by P4 being shortest and P1 being long."
        ),
    }

    json_path = base / "data/significance_summary.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    with (base / "data/significance_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["test", "statistic", "df", "p_value", "note"])
        writer.writeheader()
        for key in ["kendall_all_four", "kendall_without_p4", "kendall_p2_p3_only"]:
            row = results[key]
            writer.writerow(
                {
                    "test": key,
                    "statistic": f"W={row['kendalls_w']:.6f}; chi2={row['chi_square']:.6f}",
                    "df": row["df"],
                    "p_value": f"{row['p_value']:.6f}",
                    "note": row["events"],
                }
            )
        row = results["kendall_all_four_permutation"]
        writer.writerow(
            {
                "test": "kendall_all_four_permutation",
                "statistic": f"W={row['observed_w']:.6f}",
                "df": "",
                "p_value": f"{row['p_value']:.6f}",
                "note": f"{row['n_shuffles']} within-recording shuffles; seed={row['seed']}",
            }
        )
        writer.writerow(
            {
                "test": "binomial_p2_vs_p3_modal_peak",
                "statistic": f"P2={peak_counts.get('P2', 0)}; P3={peak_counts.get('P3', 0)}",
                "df": "",
                "p_value": f"{results['modal_peak_binomial_p_two_sided_p2_vs_p3']:.6f}",
                "note": "two-sided exact binomial, p0=0.5",
            }
        )
        wilcoxon = results["wilcoxon_p2_minus_p3"]
        writer.writerow(
            {
                "test": "wilcoxon_p2_minus_p3",
                "statistic": f"z={wilcoxon['z_normal_approx']:.6f}",
                "df": "",
                "p_value": f"{wilcoxon['p_normal_approx']:.6f}",
                "note": f"exact signed-rank p={wilcoxon['p_exact_signed_rank']:.6f}",
            }
        )
        effect = results["paired_p2_minus_p3_effect"]
        writer.writerow(
            {
                "test": "paired_p2_minus_p3_effect",
                "statistic": f"mean={effect['mean_seconds']:.3f}s; sd={effect['sd']:.3f}; dz={effect['cohens_dz']:.3f}",
                "df": effect["n"] - 1,
                "p_value": "",
                "note": f"95% CI [{effect['ci95_low']:.3f}, {effect['ci95_high']:.3f}] s",
            }
        )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
