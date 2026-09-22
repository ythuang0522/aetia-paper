#!/usr/bin/env python3
"""Registry analysis: what the sequencing report already does to treatment, and how long it is.

Reads the three-hospital registry workbook (PHI; stays OUTSIDE this repository, path in
COHORT_XLSX) and writes two de-identified artifacts used by Results and Discussion:

  figures-source/impact.csv           one row per aggregate: group, metric, n, denominator, value
  figures-source/impact_summary.json  the same numbers keyed for quoting in the text

Four analyses, none of which needs the adjudicated labels except the fourth:

  1. Clinical impact      treatment change, its direction, its attribution to mNGS, in-hospital
                          outcome and ventilation, over all 105 registry specimens.
  2. Organism burden      organisms per mNGS report by specimen type, and the same stratified by
                          ward, pneumonia category, corticosteroids and ARDS both overall and
                          WITHIN bronchoalveolar lavage.  The within-BALF strata are the control:
                          they show the burden difference is carried by the specimen compartment
                          and not by how sick the patient is.
  3. Culture concordance  organism-level agreement between the mNGS report and the cultures of the
                          same admission, over all 105 specimens, cross-checked against the
                          workbook's own pre-computed tally in the sheet 'Lab vs.mNGS'.
  4. No-pathogen cases    the registry specimens whose adjudication records no causative pathogen,
                          separated into explicit negatives and the dash convention of one hospital,
                          with what mNGS reported for them.

Also the class composition (bacteria / viruses / fungi / mycobacteria) of what was reported against
what was adjudicated.  No patient, specimen or hospital identifier is written out.

Name normalization, the alias table and the non-pathogen adjudication strings are imported from
make_discordance.py so that the two analyses cannot drift apart.
"""
import collections
import csv
import json
import math
import os
import re
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_discordance import NON_PATHOGEN, STERILE, norm, q, sheet_rows  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
XLSX = Path(os.environ.get("COHORT_XLSX", ROOT.parent / "三院-final-mNGS merged file.xlsx"))
OUT_CSV = ROOT / "figures-source" / "impact.csv"
OUT_JSON = ROOT / "figures-source" / "impact_summary.json"

YES, NO = {"是", "有"}, {"否", "無"}
AIRWAY = {"BALF", "Sputum"}
# adjudication cells that positively state "no causative pathogen", as against the bare dash, which
# one hospital uses for every one of its unlabelled rows and which may equally mean "not recorded".
EXPLICIT_NEG = {"不明", "not infection case", "no pathogen", "無", "nil", "none", "no"}

VIRUS_WORDS = ("virus", "viral", "hsv", "hhv", "ebv", "cmv", "covid")
FUNGUS_WORDS = ("candida", "aspergill", "pneumocystis", "cryptococc", "mucor", "rhizopus",
                "trichosporon", "fusarium", "yeast", "malassezia", "talaromyces", "scedosporium",
                "histoplasma", "blastomyces")


def organism_class(name):
    s = name.lower()
    if "mycobacter" in s:
        return "mycobacterium"
    if any(w in s for w in FUNGUS_WORDS):
        return "fungus"
    if any(w in s for w in VIRUS_WORDS) or s in {"epstein-barr virus", "cytomegalovirus"}:
        return "virus"
    return "bacterium"



# ---- inferential tests, stdlib only (no scipy in this environment) ----------

def fisher_or(a, b, c, d):
    """Odds ratio with a Haldane-Anscombe 0.5 correction, its 95% CI, and the two-sided exact p."""
    def lf(n):
        return math.lgamma(n + 1)

    n = a + b + c + d

    def hyper(a_):
        b_, c_, d_ = a + b - a_, a + c - a_, d - (a - a_)
        if min(b_, c_, d_) < 0:
            return 0.0
        return math.exp(lf(a + b) + lf(c + d) + lf(a + c) + lf(b + d)
                        - lf(n) - lf(a_) - lf(b_) - lf(c_) - lf(d_))

    p_obs = hyper(a)
    p_two = sum(pi for a_ in range(max(0, a - d), min(a + b, a + c) + 1)
                if (pi := hyper(a_)) <= p_obs * (1 + 1e-7))
    or_ = ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
    se = math.sqrt(1 / (a + 0.5) + 1 / (b + 0.5) + 1 / (c + 0.5) + 1 / (d + 0.5))
    return {"odds_ratio": round(or_, 2), "ci_low": round(math.exp(math.log(or_) - 1.96 * se), 2),
            "ci_high": round(math.exp(math.log(or_) + 1.96 * se), 2), "p": round(min(p_two, 1.0), 3)}


def _solve(mat, rhs_cols):
    """Gauss-Jordan on an augmented matrix; returns None if singular."""
    k = len(mat)
    m = [row[:] + rhs[:] for row, rhs in zip(mat, rhs_cols)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            return None
        m[col], m[piv] = m[piv], m[col]
        pv = m[col][col]
        m[col] = [x / pv for x in m[col]]
        for r in range(k):
            if r != col and m[r][col]:
                f = m[r][col]
                m[r] = [x - f * y for x, y in zip(m[r], m[col])]
    return [row[k:] for row in m]


def logistic_or(X, y, names, iters=80):
    """Newton-Raphson logistic regression; returns an odds ratio with 95% CI and Wald p per term."""
    k = len(X[0])
    beta = [0.0] * k
    for _ in range(iters):
        grad = [0.0] * k
        hess = [[0.0] * k for _ in range(k)]
        for xi, yi in zip(X, y):
            z = max(-30.0, min(30.0, sum(b * x for b, x in zip(beta, xi))))
            pr = 1 / (1 + math.exp(-z))
            w = pr * (1 - pr)
            for a in range(k):
                grad[a] += (yi - pr) * xi[a]
                for b2 in range(k):
                    hess[a][b2] += w * xi[a] * xi[b2]
        step = _solve(hess, [[g] for g in grad])
        if step is None:
            return None
        delta = [r[0] for r in step]
        beta = [b + dl for b, dl in zip(beta, delta)]
        if max(abs(dl) for dl in delta) < 1e-9:
            break
    hess = [[0.0] * k for _ in range(k)]
    for xi in X:
        z = max(-30.0, min(30.0, sum(b * x for b, x in zip(beta, xi))))
        pr = 1 / (1 + math.exp(-z))
        w = pr * (1 - pr)
        for a in range(k):
            for b2 in range(k):
                hess[a][b2] += w * xi[a] * xi[b2]
    inv = _solve(hess, [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)])
    if inv is None:
        return None
    out = {}
    for i, (nm, b) in enumerate(zip(names, beta)):
        se = math.sqrt(max(inv[i][i], 0.0))
        z = b / se if se else 0.0
        out[nm] = {"odds_ratio": round(math.exp(b), 2),
                   "ci_low": round(math.exp(b - 1.96 * se), 2),
                   "ci_high": round(math.exp(b + 1.96 * se), 2),
                   "p": round(2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))), 3)}
    return out

def cell(row, i):
    return str(row[i]).strip() if i < len(row) and row[i] is not None else ""


def yesno(value):
    return "yes" if value in YES else ("no" if value in NO else "")


def load(wb):
    """Per registry case: specimen type, reported organisms, cultures, adjudication, course."""
    mngs = {}
    for row in sheet_rows(wb, "mNGS"):
        if not row[0]:
            continue
        orgs = []
        for i in range(9, 19):
            orgs += norm(row[i])
        mngs[row[0]] = {"stype": cell(row, 5), "orgs": set(orgs), "n_reported": sum(1 for i in range(9, 19) if cell(row, i))}

    micro = {}
    for row in sheet_rows(wb, "微生物診斷資料"):
        if not row[0]:
            continue
        cult = set()
        for base in (3, 15, 27, 39, 51, 63):
            cult |= set(norm(row[base + 2]))
        raw_labels = [cell(row, i) for i in range(148, 156) if cell(row, i)]
        labels = {o for i in range(148, 156) for o in norm(row[i]) if o not in NON_PATHOGEN}
        micro[row[0]] = {
            "cult": cult - NON_PATHOGEN,
            "labels": labels,
            "raw_labels": raw_labels,
            "changed": yesno(cell(row, 145)),
            "direction": {"升階": "escalation", "降階": "de-escalation", "無定論": "inconclusive"}.get(cell(row, 146), ""),
            "attributed": {"有影響": "yes", "無影響": "no"}.get(cell(row, 147), ""),
            "ventilated": yesno(cell(row, 156)),
            "died": {"死亡": "yes", "存活": "no"}.get(cell(row, 159), ""),
        }

    basic = {}
    for row in sheet_rows(wb, "基本資料"):
        if not row[1]:
            continue
        basic[row[1]] = {"ward": "ICU" if cell(row, 10) == "ICU" else ("general ward" if cell(row, 10) else ""),
                         "pneumonia": cell(row, 24), "steroid": yesno(cell(row, 22)),
                         "ards": yesno(cell(row, 23)), "malignancy": yesno(cell(row, 17)),
                         "age": row[5] if isinstance(row[5], (int, float)) else None}
    return mngs, micro, basic


def adjudication_group(raw_labels):
    """pathogen | explicit negative | dash only | not recorded."""
    if not raw_labels:
        return "not recorded"
    lowered = [s.lower() for s in raw_labels]
    if any(s not in EXPLICIT_NEG and s != "-" for s in lowered):
        return "pathogen"
    return "dash only" if set(lowered) == {"-"} else "explicit negative"


def add(rows, group, metric, n=None, denom=None, value=None, unit="", note=""):
    rows.append({"group": group, "metric": metric, "n": n, "denominator": denom,
                 "value": value if value is not None else (round(100 * n / denom, 1) if denom else None),
                 "unit": unit or ("%" if denom else ""), "note": note})


def burden_strata(codes, mngs, basic, label, rows, summary):
    """Organisms per report by a patient-level stratum; reported for the given case set."""
    out = {}
    for key, getter in (("ward", "ward"), ("pneumonia", "pneumonia"), ("steroid", "steroid"), ("ards", "ards")):
        groups = collections.defaultdict(list)
        for c in codes:
            stratum = basic.get(c, {}).get(getter, "")
            if stratum:
                groups[stratum].append(mngs[c]["n_reported"])
        for stratum, burden in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            out[f"{key}:{stratum}"] = {"n": len(burden), "median": q(burden, 0.5),
                                       "mean": round(sum(burden) / len(burden), 2)}
            add(rows, label, f"organisms per report, {key} = {stratum}", n=len(burden),
                value=q(burden, 0.5), unit="organisms (median)")
    summary[f"burden_strata_{label.replace(' ', '_')}"] = out


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    mngs, micro, basic = load(wb)
    codes = [c for c in mngs if c in micro]
    n = len(codes)
    rows, summary = [], {"specimens": n}

    # ---- 1. clinical impact -------------------------------------------------
    changed = [c for c in codes if micro[c]["changed"] == "yes"]
    attributed = [c for c in codes if micro[c]["attributed"] == "yes"]
    not_attributed = [c for c in codes if micro[c]["attributed"] == "no"]
    recorded = attributed + not_attributed
    direction = collections.Counter(micro[c]["direction"] for c in attributed)
    all_direction = collections.Counter(micro[c]["direction"] for c in codes)
    died = [c for c in codes if micro[c]["died"] == "yes"]
    vent = [c for c in codes if micro[c]["ventilated"] == "yes"]
    vent_rec = [c for c in codes if micro[c]["ventilated"] in ("yes", "no")]

    add(rows, "clinical impact", "antimicrobial therapy changed", len(changed), n)
    add(rows, "clinical impact", "change attributed to mNGS", len(attributed), n)
    add(rows, "clinical impact", "change attributed to mNGS, of those with attribution recorded",
        len(attributed), len(recorded))
    for key in ("escalation", "de-escalation", "inconclusive"):
        add(rows, "clinical impact", f"mNGS-attributed change: {key}", direction[key], len(attributed))
        add(rows, "clinical impact", f"{key}s that were mNGS-attributed", direction[key], all_direction[key])
    add(rows, "clinical impact", "in-hospital death", len(died), n)
    add(rows, "clinical impact", "mechanical ventilation within 3 days of sampling", len(vent), len(vent_rec))
    for label, group in (("attributed", attributed), ("not attributed", not_attributed)):
        burden = [mngs[c]["n_reported"] for c in group]
        deaths = sum(1 for c in group if micro[c]["died"] == "yes")
        add(rows, "clinical impact", f"organisms per report, change {label} to mNGS", len(group),
            value=q(burden, 0.5), unit="organisms (median)")
        add(rows, "clinical impact", f"in-hospital death, change {label} to mNGS", deaths, len(group))
    summary["impact"] = {
        "changed": len(changed), "changed_pct": round(100 * len(changed) / n, 1),
        "attributed": len(attributed), "attributed_pct": round(100 * len(attributed) / n, 1),
        "attribution_recorded": len(recorded),
        "attributed_pct_of_recorded": round(100 * len(attributed) / len(recorded), 1),
        "attributed_escalation": direction["escalation"], "attributed_deescalation": direction["de-escalation"],
        "attributed_inconclusive": direction["inconclusive"],
        "deescalations_total": all_direction["de-escalation"],
        "escalations_total": all_direction["escalation"],
        "deaths": len(died), "deaths_pct": round(100 * len(died) / n, 1),
        "ventilated": len(vent), "ventilated_denom": len(vent_rec),
        "ventilated_pct": round(100 * len(vent) / len(vent_rec), 1),
        "burden_median_attributed": q([mngs[c]["n_reported"] for c in attributed], 0.5),
        "burden_median_not_attributed": q([mngs[c]["n_reported"] for c in not_attributed], 0.5),
        "death_pct_attributed": round(100 * sum(1 for c in attributed if micro[c]["died"] == "yes") / len(attributed), 1),
        "death_pct_not_attributed": round(100 * sum(1 for c in not_attributed if micro[c]["died"] == "yes") / len(not_attributed), 1),
    }

    # ---- 2. organism burden by specimen, with the within-BALF control -------
    by_type = collections.defaultdict(list)
    for c in codes:
        by_type[mngs[c]["stype"]].append(mngs[c]["n_reported"])
    spec_summary = {}
    for stype, burden in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        spec_summary[stype] = {"n": len(burden), "median": q(burden, 0.5),
                               "mean": round(sum(burden) / len(burden), 2),
                               "zero": sum(1 for b in burden if b == 0)}
        add(rows, "organism burden", f"organisms per report, {stype}", n=len(burden),
            value=q(burden, 0.5), unit="organisms (median)")
    airway = [mngs[c]["n_reported"] for c in codes if mngs[c]["stype"] in AIRWAY]
    sterile = [mngs[c]["n_reported"] for c in codes if mngs[c]["stype"] in STERILE]
    add(rows, "organism burden", "organisms per report, airway specimen", n=len(airway),
        value=q(airway, 0.5), unit="organisms (median)")
    add(rows, "organism burden", "organisms per report, sterile-site specimen", n=len(sterile),
        value=q(sterile, 0.5), unit="organisms (median)")
    summary["burden_by_specimen"] = spec_summary
    summary["burden_airway"] = {"n": len(airway), "median": q(airway, 0.5), "q1": q(airway, 0.25), "q3": q(airway, 0.75)}
    summary["burden_sterile"] = {"n": len(sterile), "median": q(sterile, 0.5), "q1": q(sterile, 0.25), "q3": q(sterile, 0.75)}
    burden_strata(codes, mngs, basic, "all specimens", rows, summary)
    burden_strata([c for c in codes if mngs[c]["stype"] == "BALF"], mngs, basic, "BALF only", rows, summary)

    # ---- 3. culture concordance over all 105 --------------------------------
    reported = confirmed = cult_total = cult_missed = 0
    for c in codes:
        orgs, cult = mngs[c]["orgs"], micro[c]["cult"]
        reported += len(orgs)
        confirmed += len(orgs & cult)
        cult_total += len(cult)
        cult_missed += len(cult - orgs)
    add(rows, "culture concordance", "mNGS organisms with a same-species culture in the admission",
        confirmed, reported)
    add(rows, "culture concordance", "culture organisms absent from the mNGS report", cult_missed, cult_total)
    summary["concordance"] = {"mngs_organisms": reported, "culture_confirmed": confirmed,
                              "culture_confirmed_pct": round(100 * confirmed / reported, 1),
                              "culture_organisms": cult_total, "culture_absent_from_report": cult_missed,
                              "culture_absent_pct": round(100 * cult_missed / cult_total, 1)}
    # cross-check against the workbook's own pre-computed comparison sheet
    tally = collections.Counter()
    ws = wb["Lab vs.mNGS"]
    header = [str(c).strip() if c is not None else "" for c in next(ws.iter_rows(values_only=True))]
    cols = {name: i for i, name in enumerate(header)
            if name in ("NGS+ Cx-", "Matched", "Partial match", "Mismatch", "NGS- Cx +", "NGS- Cx-")}
    for row in ws.iter_rows(min_row=2, values_only=True):
        for name, i in cols.items():
            try:
                tally[name] += int(row[i] or 0)
            except (TypeError, ValueError):
                pass
    total = sum(tally.values())
    for name, count in tally.items():
        add(rows, "culture concordance (workbook tally)", name, count, total)
    summary["workbook_concordance"] = {"comparisons": total,
                                       **{k: {"n": v, "pct": round(100 * v / total, 1)} for k, v in tally.items()}}

    # ---- 4. cases with no adjudicated pathogen ------------------------------
    groups = collections.defaultdict(list)
    for c in codes:
        groups[adjudication_group(micro[c]["raw_labels"])].append(c)
    adj_summary = {}
    for g, members in groups.items():
        burden = [mngs[c]["n_reported"] for c in members]
        adj_summary[g] = {
            "n": len(members), "median_organisms": q(burden, 0.5),
            "mean_organisms": round(sum(burden) / len(burden), 2),
            "with_no_organism": sum(1 for b in burden if b == 0),
            "therapy_changed": sum(1 for c in members if micro[c]["changed"] == "yes"),
            "attributed": sum(1 for c in members if micro[c]["attributed"] == "yes"),
            "died": sum(1 for c in members if micro[c]["died"] == "yes"),
            "specimens": dict(collections.Counter(mngs[c]["stype"] for c in members).most_common()),
        }
        add(rows, "adjudication", f"specimens, {g}", len(members), n)
        add(rows, "adjudication", f"organisms per report, {g}", n=len(members),
            value=q(burden, 0.5), unit="organisms (median)")
    no_pathogen = groups["explicit negative"] + groups["dash only"]
    reported_here = sum(mngs[c]["n_reported"] for c in no_pathogen)
    add(rows, "adjudication", "specimens with no adjudicated pathogen", len(no_pathogen), n)
    add(rows, "adjudication", "organisms reported for them", n=reported_here, unit="organisms")
    add(rows, "adjudication", "of those specimens, at least one organism reported",
        sum(1 for c in no_pathogen if mngs[c]["n_reported"]), len(no_pathogen))
    summary["adjudication"] = adj_summary
    summary["no_pathogen"] = {
        "specimens": len(no_pathogen),
        "pct": round(100 * len(no_pathogen) / n, 1),
        "explicit": len(groups["explicit negative"]),
        "dash_only": len(groups["dash only"]),
        "organisms_reported": reported_here,
        "with_at_least_one_organism": sum(1 for c in no_pathogen if mngs[c]["n_reported"]),
        "median_organisms": q([mngs[c]["n_reported"] for c in no_pathogen], 0.5),
        "max_organisms": max(mngs[c]["n_reported"] for c in no_pathogen),
    }

    # ---- 5. outcome: is acting on the report associated with survival? ------
    # Every registry patient was sequenced, so the only contrast the registry supports is between
    # patients whose treatment change the team credited to mNGS and patients whose change it did not.
    # There is no unsequenced comparator, the exposure is the team's own retrospective judgement, and
    # treatment is recorded only as escalation or de-escalation, so no appropriateness of therapy and
    # no time to appropriate therapy can be derived. The test below is reported as a null, not as
    # evidence of absent benefit.
    cohort = []
    for c in codes:
        m, b = micro[c], basic.get(c, {})
        if m["died"] not in ("yes", "no"):
            continue
        cohort.append({"died": 1 if m["died"] == "yes" else 0,
                       "attributed": {"yes": 1, "no": 0}.get(m["attributed"]),
                       "changed": {"yes": 1, "no": 0}.get(m["changed"]),
                       "icu": 1 if b.get("ward") == "ICU" else 0,
                       "ards": 1 if b.get("ards") == "yes" else 0,
                       "malignancy": 1 if b.get("malignancy") == "yes" else 0,
                       "steroid": 1 if b.get("steroid") == "yes" else 0,
                       "age": b.get("age")})

    def two_by_two(exposure):
        e1 = [r for r in cohort if r[exposure] == 1]
        e0 = [r for r in cohort if r[exposure] == 0]
        a, c_ = sum(r["died"] for r in e1), sum(r["died"] for r in e0)
        return e1, e0, a, len(e1) - a, c_, len(e0) - c_

    e1, e0, a, b_, c_, d_ = two_by_two("attributed")
    attributed_death = {
        "exposed_deaths": a, "exposed_n": len(e1), "exposed_pct": round(100 * a / len(e1), 1),
        "unexposed_deaths": c_, "unexposed_n": len(e0), "unexposed_pct": round(100 * c_ / len(e0), 1),
        **fisher_or(a, b_, c_, d_)}
    # baseline balance of the exposure, which is what makes this contrast interpretable
    attributed_death["baseline"] = {
        k: {"exposed_pct": round(100 * sum(r[k] for r in e1) / len(e1), 1),
            "unexposed_pct": round(100 * sum(r[k] for r in e0) / len(e0), 1)}
        for k in ("icu", "ards", "malignancy", "steroid")}
    adj = [r for r in cohort if r["attributed"] is not None and r["age"] is not None]
    model = logistic_or(
        [[1, r["attributed"], r["icu"], r["ards"], r["malignancy"], r["steroid"], (r["age"] - 70) / 10]
         for r in adj], [r["died"] for r in adj],
        ["intercept", "attributed", "icu", "ards", "malignancy", "steroid", "age_per_10y"])
    attributed_death["adjusted"] = {"n": len(adj), "deaths": sum(r["died"] for r in adj), "terms": model}
    summary["outcome_attributed"] = attributed_death
    add(rows, "outcome", "in-hospital death, change attributed to mNGS", a, len(e1))
    add(rows, "outcome", "in-hospital death, change not attributed", c_, len(e0))
    add(rows, "outcome", "unadjusted odds ratio, attributed vs not", value=attributed_death["odds_ratio"],
        unit="OR", note=f"95% CI {attributed_death['ci_low']}-{attributed_death['ci_high']}, "
                        f"Fisher exact p={attributed_death['p']}")
    if model:
        t = model["attributed"]
        add(rows, "outcome", "adjusted odds ratio, attributed vs not", value=t["odds_ratio"], unit="OR",
            note=f"95% CI {t['ci_low']}-{t['ci_high']}, p={t['p']}; adjusted for intensive care, ARDS, "
                 f"malignancy, corticosteroids and age; n={len(adj)}")

    # the same test on "any treatment change" is confounded by indication and is recorded here only so
    # that the imbalance is on the record; it is not reported as a finding.
    e1, e0, a, b_, c_, d_ = two_by_two("changed")
    changed_death = {"exposed_deaths": a, "exposed_n": len(e1), "unexposed_deaths": c_, "unexposed_n": len(e0),
                     **fisher_or(a, b_, c_, d_),
                     "baseline": {k: {"exposed_pct": round(100 * sum(r[k] for r in e1) / len(e1), 1),
                                      "unexposed_pct": round(100 * sum(r[k] for r in e0) / len(e0), 1)}
                                  for k in ("icu", "ards", "malignancy", "steroid")},
                     "interpretation": "confounded by indication: the exposed group is sicker at baseline"}
    summary["outcome_changed_confounded"] = changed_death
    add(rows, "outcome (confounded, not reported as a finding)",
        "in-hospital death, any treatment change vs none", a, len(e1),
        note="the changed group has more ARDS and corticosteroid use at baseline; see outcome_changed_confounded")

    # ---- class composition, reported against adjudicated --------------------
    rep_cls = collections.Counter()
    adj_cls = collections.Counter()
    virus_species = collections.Counter()
    for c in codes:
        for o in mngs[c]["orgs"]:
            rep_cls[organism_class(o)] += 1
            if organism_class(o) == "virus":
                virus_species[o] += 1
        for o in micro[c]["labels"]:
            adj_cls[organism_class(o)] += 1
    rt, at = sum(rep_cls.values()), sum(adj_cls.values())
    for k in ("bacterium", "virus", "fungus", "mycobacterium"):
        add(rows, "class composition", f"reported on mNGS: {k}", rep_cls[k], rt)
        add(rows, "class composition", f"adjudicated causative: {k}", adj_cls[k], at)
    herpes = sum(v for k, v in virus_species.items()
                 if any(w in k for w in ("herpes", "epstein", "cytomegalo", "human herpesvirus")))
    add(rows, "class composition", "herpesviruses among reported viruses", herpes, rep_cls["virus"])
    summary["class_composition"] = {
        "reported_total": rt, "adjudicated_total": at,
        "reported": {k: {"n": rep_cls[k], "pct": round(100 * rep_cls[k] / rt, 1)} for k in rep_cls},
        "adjudicated": {k: {"n": adj_cls[k], "pct": round(100 * adj_cls[k] / at, 1)} for k in adj_cls},
        "herpesviruses": herpes, "herpesvirus_pct_of_viruses": round(100 * herpes / rep_cls["virus"], 1),
    }

    # ---- data-quality note --------------------------------------------------
    orphans = sum(1 for row in sheet_rows(wb, "微生物診斷資料") if row[0] and row[0] not in mngs)
    summary["microbiology_rows_without_a_registry_specimen"] = orphans
    add(rows, "data quality", "microbiology rows whose case code is absent from the mNGS sheet", n=orphans)

    OUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        fh.write("# registry aggregates on treatment impact, organism burden, culture concordance and adjudication\n")
        fh.write("# source: three-hospital registry workbook (PHI, outside this repository); "
                 "generated by tables/make_impact.py; verified=yes\n")
        writer = csv.DictWriter(fh, fieldnames=["group", "metric", "n", "denominator", "value", "unit", "note"])
        writer.writeheader()
        writer.writerows(rows)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV} ({len(rows)} aggregates over {n} specimens) and {OUT_JSON}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
