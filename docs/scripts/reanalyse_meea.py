"""Corrected reanalysis of the MEEA expansion-policy comparison.

Three defects in the published tables:
  D1  LocalRetro has results for 48 of 190 targets but is tabulated as a peer of
      three full-190 arms. Its 54.17% is 26/48.
  D2  Averages are taken over each policy's OWN successes. With resolution
      ranging 47-97%, the time/depth/call columns are computed on different and
      systematically different subsets -- a weak policy is timed only on the
      targets it could solve.
  D3  The per-stratum table uses the OOD_Class label, shown invalid 2026-08-06.

This recomputes: resolution over the full denominator, and every other metric on
the PAIRED set of targets solved by all compared arms. No strata.
"""
import json
import statistics
from itertools import combinations

RES = "meea_backup/results"
ARMS = ["ReactionT5", "AZF", "Chemformer", "LocalRetro"]
METRICS = ["search_times", "model_calls", "depths", "feasibility"]

data = {a: json.load(open(f"{RES}/MEEA_{a}_retro190.json")) for a in ARMS}
n = {a: len(data[a]["success_rate"]) for a in ARMS}

print("=" * 78)
print("D1 -- COVERAGE. What each arm actually ran.")
print("=" * 78)
print(f"{'policy':<14}{'targets run':>12}{'solved':>9}{'over its own n':>16}{'over 190':>11}")
for a in ARMS:
    s = sum(data[a]["success_rate"])
    own = 100.0 * s / n[a]
    full = 100.0 * s / 190
    print(f"{a:<14}{n[a]:>12}{s:>9}{own:>15.2f}%{full:>10.2f}%")
print("\nLocalRetro's published 54.17% is its rate over 48 targets. As a fraction of")
print("the benchmark all four arms are supposed to share, it solved 26/190 = 13.68%.")
print("The chunk files are named 0_48 / 48_96 / 96_144 / 144_190 and only the first")
print("merged, so the 48 are almost certainly targets 0-47 -- a contiguous prefix,")
print("not a random sample. Everything below excludes LocalRetro from the 190-target")
print("comparison and treats it separately on its own 48.")

full_arms = [a for a in ARMS if n[a] == 190]

print()
print("=" * 78)
print("D2 -- SURVIVORSHIP. Own-successes averaging vs paired.")
print("=" * 78)

succ = {a: data[a]["success_rate"] for a in full_arms}
common = [i for i in range(190) if all(succ[a][i] == 1 for a in full_arms)]
print(f"targets solved by all of {', '.join(full_arms)}: {len(common)} of 190")


def mean_over(a, key, idx):
    v = [data[a][key][i] for i in idx if data[a][key][i] != -1]
    return statistics.mean(v) if v else float("nan")


for key in METRICS:
    print(f"\n> {key}")
    print(f"  {'policy':<14}{'own successes':>16}{'paired (n=%d)' % len(common):>18}{'shift':>12}")
    for a in full_arms:
        own_idx = [i for i in range(190) if succ[a][i] == 1]
        o, p = mean_over(a, key, own_idx), mean_over(a, key, common)
        print(f"  {a:<14}{o:>16.2f}{p:>18.2f}{p - o:>+12.2f}")

print("\nPaired differences on the common set, with a sign test:")
for x, y in combinations(full_arms, 2):
    for key in ["search_times", "model_calls"]:
        d = [data[x][key][i] - data[y][key][i] for i in common
             if data[x][key][i] != -1 and data[y][key][i] != -1]
        if not d:
            continue
        wins = sum(1 for v in d if v < 0)
        print(f"  {key:<14} {x} - {y}: mean {statistics.mean(d):+8.2f}  "
              f"median {statistics.median(d):+8.2f}  {x} faster/cheaper on {wins}/{len(d)}")

print()
print("=" * 78)
print("LocalRetro, scoped to its own 48 targets, against the same 48 for the others")
print("=" * 78)
lr_idx = list(range(48))
common48 = [i for i in lr_idx if all(data[a]["success_rate"][i] == 1 for a in ARMS)]
print(f"solved by all four on targets 0-47: {len(common48)}")
print(f"{'policy':<14}{'solved/48':>12}{'rate':>9}", end="")
for key in METRICS:
    print(f"{key[:9]:>11}", end="")
print()
for a in ARMS:
    s = sum(data[a]["success_rate"][i] for i in lr_idx)
    print(f"{a:<14}{s:>12}{100.0 * s / 48:>8.1f}%", end="")
    for key in METRICS:
        print(f"{mean_over(a, key, common48):>11.2f}", end="")
    print()
