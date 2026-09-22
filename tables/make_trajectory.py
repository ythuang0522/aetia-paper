#!/usr/bin/env python3
"""Physiological trajectory around the mNGS specimen, from the KMUH whole-record extracts.

Reads two PHI sources that stay OUTSIDE this repository:
  COHORT_XLSX    the three-hospital registry workbook (mNGS specimen date, discharge status/date)
  PHENOTYPE_DIR  the KMUH whole-record phenotyping output, one workbook per admission, whose
                 Lab_Results sheet holds the laboratory table reconstructed from the discharge PDF

and writes two de-identified artifacts:
  figures-source/trajectory.csv           one row per (marker, window, outcome group) aggregate
  figures-source/trajectory_summary.json  the numbers quoted in Results and Discussion

Day 0 is the mNGS specimen. Windows are pre (-14..-1), d0-2, d3-7, d8-14, d15-30. For each patient
and marker the within-window median is taken first, so an admission with many blood gases counts once
per window; group values are medians of those per-patient medians. Paired comparisons (pre -> d3-7)
use the Wilcoxon signed-rank test on patients with a value in both windows.

Data quality. Every marker is gated to a physiological range and the rejection rate is recorded; all
markers except temperature reject under 1% of values. The temperature column of the reconstructed
table is damaged: the leading "3" is dropped from 31% of readings, so 37.3 C is stored as 7.3. Two
observations identify the fault and license the repair: the truncated values occupy (3.0, 10.0),
exactly the image of [33.0, 40.0) under the loss of a leading 3, and their reconstruction has the
same distribution as the intact readings (median 36.6 against 36.7 C). The repair is validated
against the nearest intact reading of the same admission within 36 h: repaired readings differ from
that neighbour by a median of 0.4 C, less than the 0.6 C between consecutive intact readings, and
imply the same fever rate (5% of readings >= 38 C in both). Readings of exactly 3.0 (19% of the
column) are a second, unrecoverable failure and are discarded, as are values outside (3.0, 10.0) and
[33.0, 42.5]. 1,344 of 1,664 readings (81%) survive. No identifier, date or per-patient value is
written out.
"""
import collections
import csv
import datetime
import glob
import json
import math
import os
import re
import statistics as st
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = Path(os.environ.get("COHORT_XLSX", ROOT.parent / "三院-final-mNGS merged file.xlsx"))
PHENO = Path(os.environ.get("PHENOTYPE_DIR", ROOT.parent / "phenotype for KMUH"))
OUT_CSV = ROOT / "figures-source" / "trajectory.csv"
OUT_JSON = ROOT / "figures-source" / "trajectory_summary.json"

# marker -> (sheet test_name, plausible range, direction in which a change is an improvement)
MARKERS = {
    "temperature": ("Temperature", (33.0, 42.5), -1),
    "platelets": ("PLT", (5, 900), +1),
    "lactate": ("Lactate", (0.2, 25), -1),
    "WBC": ("WBC", (0.1, 80), -1),
    "pO2": ("pO2", (20, 600), +1),
    "creatinine": ("Creatinine", (0.1, 20), -1),
    "procalcitonin": ("PCT", (0.0, 200), -1),
}
WINDOWS = [("pre", -14, -1), ("d0-2", 0, 2), ("d3-7", 3, 7), ("d8-14", 8, 14), ("d15-30", 15, 30)]
FEVER = 38.0


def pdate(cell):
    if isinstance(cell, datetime.datetime):
        return cell.date()
    if isinstance(cell, datetime.date):
        return cell
    m = re.match(r"\s*(\d{4})[/-](\d{1,2})[/-](\d{1,2})", str(cell or ""))
    return datetime.date(*map(int, m.groups())) if m else None


def number(cell):
    m = re.match(r"\s*[<>]?\s*(-?\d+(?:\.\d+)?)\s*$", str(cell or "").strip())
    return float(m.group(1)) if m else None


def repair_temperature(v):
    """Return the reading in Celsius, or None when the value cannot be trusted (see module docstring)."""
    if v is None:
        return None
    if 33.0 <= v <= 42.5:
        return v
    if 3.0 < v < 10.0:           # leading 3 dropped by the PDF table parser
        return v + 30.0
    return None                  # exactly 3.0, and anything else, is unrecoverable


def wilcoxon(pairs):
    """Two-sided signed-rank test on (before, after); returns (n, median change, p) or None."""
    diffs = [b - a for a, b in pairs if b != a]
    if len(diffs) < 6:
        return None
    order = sorted((abs(d), i) for i, d in enumerate(diffs))
    ranks, i = {}, 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and order[j + 1][0] == order[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k][1]] = r
        i = j + 1
    n = len(diffs)
    w_pos = sum(ranks[i] for i, d in enumerate(diffs) if d > 0)
    w = min(w_pos, n * (n + 1) / 2 - w_pos)
    mu, sd = n * (n + 1) / 4, math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (w - mu) / sd
    return n, st.median([b - a for a, b in pairs]), 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def load_anchors():
    """KMUH cases: mNGS specimen date, discharge date and in-hospital outcome."""
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    micro = {}
    it = wb["微生物診斷資料"].iter_rows(values_only=True)
    next(it)
    for row in it:
        if row[0]:
            micro[row[0]] = row
    anchors = {}
    it = wb["mNGS"].iter_rows(values_only=True)
    next(it)
    for row in it:
        code = row[0]
        if not code or not str(code).startswith("K"):
            continue
        m = micro.get(code)
        anchors[int(str(code)[1:])] = {
            "day0": pdate(row[7]),
            "died": {"死亡": 1, "存活": 0}.get(str(m[159]).strip() if m and m[159] else ""),
            "discharge": pdate(m[158]) if m else None,
        }
    return anchors


def load_series(anchors):
    """patient -> marker -> [(day relative to the specimen, value)], plus rejection counts."""
    want = {spec[0]: name for name, spec in MARKERS.items()}
    series = collections.defaultdict(lambda: collections.defaultdict(list))
    seen, usable, kept = collections.Counter(), collections.Counter(), collections.Counter()
    files = sorted(glob.glob(str(PHENO / "patient phenotype_send" / "*_phenotype.xlsx")))
    for path in files:
        num = int(re.search(r"patient (\d+)", Path(path).name).group(1))
        a = anchors.get(num)
        if not a or not a["day0"]:
            continue
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        it = wb["Lab_Results"].iter_rows(values_only=True)
        next(it)
        for row in it:
            marker = want.get(str(row[4] or "").strip())
            if not marker:
                continue
            seen[marker] += 1
            v = number(row[5])
            if marker == "temperature":
                v = repair_temperature(v)
            else:
                lo, hi = MARKERS[marker][1]
                v = v if (v is not None and lo <= v <= hi) else None
            day = pdate(row[2])
            if v is None:
                continue
            usable[marker] += 1          # passed the plausibility gate / repair
            if day is None:
                continue
            delta = (day - a["day0"]).days
            if -14 <= delta <= 30:
                series[num][marker].append((delta, v))
                kept[marker] += 1        # also inside the -14..30 day analysis window
        wb.close()
    return series, seen, usable, kept, len(files)


def window_median(series, pid, marker, lo, hi):
    xs = [v for d, v in series[pid].get(marker, []) if lo <= d <= hi]
    return st.median(xs) if xs else None


def window_max(series, pid, marker, lo, hi):
    xs = [v for d, v in series[pid].get(marker, []) if lo <= d <= hi]
    return max(xs) if xs else None


def main():
    anchors = load_anchors()
    series, seen, usable, kept, n_files = load_series(anchors)
    pats = [p for p in series if anchors[p]["died"] is not None]
    died = [p for p in pats if anchors[p]["died"] == 1]
    surv = [p for p in pats if anchors[p]["died"] == 0]
    rows, summary = [], {}

    ttd = [(anchors[p]["discharge"] - anchors[p]["day0"]).days for p in died
           if anchors[p]["discharge"] and 0 <= (anchors[p]["discharge"] - anchors[p]["day0"]).days < 400]
    summary["cohort"] = {
        "workbooks": n_files, "patients_with_series": len(pats), "died": len(died), "survived": len(surv),
        "specimen_to_death_median": st.median(ttd), "specimen_to_death_q1": st.quantiles(ttd, n=4)[0],
        "specimen_to_death_q3": st.quantiles(ttd, n=4)[2], "specimen_to_death_min": min(ttd),
        "specimen_to_death_max": max(ttd), "died_beyond_7d": sum(1 for x in ttd if x > 7),
        "died_beyond_14d": sum(1 for x in ttd if x > 14), "died_beyond_28d": sum(1 for x in ttd if x > 28),
        "deaths_with_date": len(ttd),
        # sorted intervals only, for the strip in Extended Data Fig. 3: a count of days carries no identity
        "specimen_to_death_days": sorted(ttd),
    }
    rows.append({"marker": "", "window": "", "group": "died", "metric": "days from specimen to death (median)",
                 "n": len(ttd), "value": st.median(ttd), "unit": "days"})

    # two separate attrition steps: the plausibility gate, then the -14..30 day analysis window
    summary["data_quality"] = {
        m: {"readings": seen[m], "passed_plausibility": usable[m],
            "passed_plausibility_pct": round(100 * usable[m] / seen[m], 1) if seen[m] else None,
            "in_analysis_window": kept[m]}
        for m in MARKERS}

    summary["markers"] = {}
    for marker, (_test, _rng, better) in MARKERS.items():
        entry = {"windows": {}, "paired": {}, "response": {}}
        for label, group in (("survived", surv), ("died", died)):
            for wname, lo, hi in WINDOWS:
                vals = [window_median(series, p, marker, lo, hi) for p in group]
                vals = [v for v in vals if v is not None]
                if not vals:
                    continue
                entry["windows"].setdefault(label, {})[wname] = {"n": len(vals), "median": round(st.median(vals), 2)}
                rows.append({"marker": marker, "window": wname, "group": label,
                             "metric": "median of per-patient medians", "n": len(vals),
                             "value": round(st.median(vals), 2), "unit": ""})
        for label, group in (("died", died), ("survived", surv)):
            pairs = [(window_median(series, p, marker, -14, -1), window_median(series, p, marker, 3, 7))
                     for p in group]
            pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
            res = wilcoxon(pairs)
            if res:
                n, delta, p = res
                entry["paired"][label] = {"n": len(pairs), "median_change": round(delta, 2), "p": round(p, 4)}
                rows.append({"marker": marker, "window": "pre->d3-7", "group": label,
                             "metric": "paired median change (Wilcoxon p in note)", "n": len(pairs),
                             "value": round(delta, 2), "unit": f"p={p:.3f}"})
        # did the marker improve by d3-7, and did the improvement hold?
        improved = worsened = relapsed = 0
        for p in died:
            pre = window_median(series, p, marker, -14, -1)
            mid = window_median(series, p, marker, 3, 7)
            late = window_median(series, p, marker, 8, 30)
            if pre is None or mid is None:
                continue
            change = (mid - pre) * better
            if change > 0:
                improved += 1
                if late is not None and (late - mid) * better < 0:
                    relapsed += 1
            elif change < 0:
                worsened += 1
        entry["response"] = {"decedents_assessable": improved + worsened, "improved": improved,
                             "worsened": worsened, "improved_then_worsened": relapsed}
        rows.append({"marker": marker, "window": "pre->d3-7", "group": "died",
                     "metric": "decedents improving, then worsening again", "n": improved + worsened,
                     "value": improved, "unit": f"{relapsed} relapsed"})
        summary["markers"][marker] = entry

    # one de-identified row per admission for the patient-level panel of Extended Data Fig. 3:
    # outcome, the interval to death or discharge, and the fever state of each window. Rows are
    # sorted by outcome and interval, so nothing links a row to a file, a patient or a date.
    def fever_state(pid, lo, hi):
        t = window_max(series, pid, "temperature", lo, hi)
        if t is None:
            return "na"
        return "fever" if t >= FEVER else ("raised" if t >= 37.0 else "normal")

    patient_rows = []
    for p_ in pats:
        end = anchors[p_]["discharge"]
        delta = (end - anchors[p_]["day0"]).days if end else None
        patient_rows.append({
            "outcome": "died" if anchors[p_]["died"] == 1 else "survived",
            "days_to_end": delta if (delta is not None and 0 <= delta < 400) else None,
            "windows": [fever_state(p_, lo, hi) for _w, lo, hi in WINDOWS],
        })
    patient_rows.sort(key=lambda r: (r["outcome"] != "died", r["days_to_end"] is None, r["days_to_end"] or 0))
    summary["patient_rows"] = patient_rows

    # fever, which needs a maximum rather than a median
    fever = {}
    for label, group in (("survived", surv), ("died", died)):
        per_window = {}
        for wname, lo, hi in WINDOWS:
            vals = [window_max(series, p, "temperature", lo, hi) for p in group]
            vals = [v for v in vals if v is not None]
            if vals:
                f = sum(1 for v in vals if v >= FEVER)
                per_window[wname] = {"n": len(vals), "febrile": f, "pct": round(100 * f / len(vals), 1)}
        pairs = [(window_max(series, p, "temperature", -14, -1), window_max(series, p, "temperature", 3, 7))
                 for p in group]
        pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
        febrile_before = [(a, b) for a, b in pairs if a >= FEVER]
        fever[label] = {"by_window": per_window, "febrile_before": len(febrile_before),
                        "afebrile_after": sum(1 for _a, b in febrile_before if b < FEVER)}
        for wname, d in per_window.items():
            rows.append({"marker": "temperature", "window": wname, "group": label,
                         "metric": f"patients with a maximum >= {FEVER} C", "n": d["n"],
                         "value": d["febrile"], "unit": "%.0f%%" % d["pct"]})
    summary["fever"] = fever

    OUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        fh.write("# physiological trajectory around the mNGS specimen (day 0), KMUH whole-record extracts\n")
        fh.write("# source: registry workbook + KMUH phenotyping output (PHI, outside this repository); "
                 "generated by tables/make_trajectory.py; verified=yes\n")
        w = csv.DictWriter(fh, fieldnames=["marker", "window", "group", "metric", "n", "value", "unit"])
        w.writeheader()
        w.writerows(rows)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV} ({len(rows)} aggregates) and {OUT_JSON}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
