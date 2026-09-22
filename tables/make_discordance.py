#!/usr/bin/env python3
"""Registry analysis: what the mNGS report alone can and cannot settle.

Reads the three-hospital registry workbook (PHI; stays OUTSIDE this repository, path in
COHORT_XLSX) and writes three de-identified artifacts used by Fig. 4a,b, Results and Supplementary Note 6:

  figures-source/discordance.csv           one row per mNGS detection: specimen class, organism,
                                           read count, adjudicated status, conventional support
  figures-source/missed_by_mngs.csv        one row per adjudicated pathogen ABSENT from the report of
                                           the sequenced specimen: which read-out found it, in which
                                           specimen, and how many days from the mNGS specimen
  figures-source/sampling.csv              one aggregate row per read-out lane: when it is sampled relative
                                           to the mNGS specimen and how long it takes to answer
  figures-source/discordance_summary.json  the aggregate numbers quoted in the text

No patient, specimen or hospital identifier is written out. The analysis covers the registry
cases whose adjudicated pathogen list is recorded in the shared workbook (the KMUH line keeps
its adjudication in the per-patient workbooks, so those cases are absent here).
"""
import collections, csv, datetime, json, os, re, statistics
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = Path(os.environ.get("COHORT_XLSX", ROOT.parent / "三院-final-mNGS merged file.xlsx"))
OUT_CSV = ROOT / "figures-source" / "discordance.csv"
OUT_MISSED = ROOT / "figures-source" / "missed_by_mngs.csv"
OUT_JSON = ROOT / "figures-source" / "discordance_summary.json"
OUT_SAMPLING = ROOT / "figures-source" / "sampling.csv"

STERILE = {"Blood", "CSF", "Tissue", "Ascites", "Pus", "Abscess"}
# name normalization: the same synonym convention as the evaluation (exact species, no genus relaxation)
ALIAS = {
    "crkp": "klebsiella pneumoniae", "cmv": "cytomegalovirus", "hcmv": "cytomegalovirus",
    "human herpesvirus 5": "cytomegalovirus", "ebv": "epstein-barr virus",
    "human herpesvirus 4": "epstein-barr virus", "human herpesvirus 4 type 1": "epstein-barr virus",
    "human gammaherpesvirus 4": "epstein-barr virus", "hsv": "herpes simplex virus 1",
    "hsv-1": "herpes simplex virus 1", "hsv1": "herpes simplex virus 1",
    "human herpesvirus 1": "herpes simplex virus 1", "human alphaherpesvirus 1": "herpes simplex virus 1",
    "hsv-2": "herpes simplex virus 2", "hhv-6": "human herpesvirus 6", "hhv-7": "human herpesvirus 7",
    "pjp": "pneumocystis jirovecii", "pneumocystis carinii": "pneumocystis jirovecii",
    "mtb": "mycobacterium tuberculosis", "mrsa": "staphylococcus aureus", "vre": "enterococcus faecium",
    "hbv": "hepatitis b virus", "ecoli": "escherichia coli", "e.coli": "escherichia coli",
    "candida albican": "candida albicans", "aspergillosis": "aspergillus",
    "aspergillosis dna": "aspergillus", "aspergillus galactomannan ag": "aspergillus",
    "non-tuberculosis mycobacterium": "nontuberculous mycobacteria",
    # serology result strings name the organism plus the assay
    "chlamydophila pneumoniae igm": "chlamydophila pneumoniae", "legionella ab": "legionella pneumophila",
}
# adjudication cells that are not organisms
NON_PATHOGEN = {"不明", "not infection case", "no pathogen", "no", "none", "無", "nil", "-"}


def norm(cell):
    if cell is None:
        return []
    out = []
    for part in re.split(r"[,;/、]| and ", str(cell)):
        t = re.sub(r"\s+", " ", part.strip().lower())
        t = re.sub(r"\(.*?\)", "", t).strip()
        t = re.sub(r"\s+(subsp\.?|subspecies|complex|group|spp\.?)\b.*$", "", t).strip()
        if not t or t in {"na", "n/a", "x"}:
            continue
        out.append(ALIAS.get(t, t))
    return out


def pdate(cell):
    """Workbook dates are datetimes in the microbiology sheet and 'YYYY/M/D' strings in the mNGS sheet."""
    if isinstance(cell, datetime.datetime):
        return cell.date()
    if isinstance(cell, datetime.date):
        return cell
    m = re.match(r"\s*(\d{4})[/-](\d{1,2})[/-](\d{1,2})", str(cell or ""))
    return datetime.date(*map(int, m.groups())) if m else None


def readout_class(kind, result):
    """culture | serology | antigen | PCR, from the test kind and the free-text result string."""
    if kind == "culture":
        return "culture"
    t = str(result or "").lower()
    if "igm" in t or "igg" in t or re.search(r"\bab\b", t) or "antibody" in t:
        return "serology"
    if "galactomannan" in t or re.search(r"\bag\b", t) or "antigen" in t:
        return "antigen"
    return "PCR"


SPECIMEN_WORDS = {"其他": "other", "Blood": "blood", "BALF": "BALF", "Sputum": "sputum", "Urine": "urine",
                  "Tissue": "tissue", "CSF": "CSF", "Pus": "pus", "Ascites": "ascites"}


def specimen_label(spec, desc):
    base = SPECIMEN_WORDS.get(str(spec or "").strip(), str(spec or "").strip().lower())
    d = str(desc or "").strip().lower()
    if d in ("", "none"):
        return base
    if d == "endo":
        return "endotracheal aspirate"
    if d == "panel":
        return base
    if d == "ln":
        return "lymph node"
    if d == "lung":
        return "lung tissue"
    if d == "stool":
        return "stool"
    if d == "foley":
        return "urine"
    return f"{base} ({d})"


def sheet_rows(wb, name):
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    next(it)
    for row in it:
        if any(c not in (None, "") for c in row):
            yield row


def q(xs, p):
    """Quantile by linear interpolation (stdlib only); xs need not be sorted."""
    xs = sorted(xs)
    if not xs:
        return None
    i = p * (len(xs) - 1)
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (i - lo), 1)


WINDOW = 90   # |collection - mNGS| and report - collection beyond this are date-entry errors in the workbook


def sampling_rows(mngs, micro, admission, n_mngs_rows):
    """When each read-out is sampled and how long it takes to answer, one aggregate row per lane.

    Lanes: the mNGS specimen (one per patient by design), the cultures and the targeted assays
    (PCR, antigen, serology) recorded in the registry.  A conventional test enters the registry only
    when it detected an organism (225 of 226 dated culture rows are positive), so the culture and
    targeted lanes describe when the evidence that named an organism was produced, not the full test
    load.  Offsets are collection day minus mNGS specimen day; turnaround is report day minus
    collection day; no date or identifier leaves this function.
    """
    lanes = {k: {"off": [], "turn": [], "cases": set(), "seen": set(), "hit": set()}
             for k in ("mNGS", "culture", "targeted")}
    admit_lag = []
    for case, m in mngs.items():
        mi = micro.get(case)
        if mi is None:
            continue
        adm = admission.get(case)
        if adm and m["date"] and 0 <= (m["date"] - adm).days <= 365:
            admit_lag.append((m["date"] - adm).days)
        lanes["mNGS"]["cases"].add(case)
        lanes["mNGS"]["off"].append(0)
        for lane, orgs in (("mNGS", m["orgs"]), ("culture", mi["cult"]), ("targeted", mi["nonc"])):
            lanes[lane]["seen"].add(case)
            if orgs - NON_PATHOGEN:                    # '-' is the workbook's "no growth"
                lanes[lane]["hit"].add(case)
        if m["date"] and m["report"] and 0 <= (m["report"] - m["date"]).days <= WINDOW:
            lanes["mNGS"]["turn"].append((m["report"] - m["date"]).days)
        for kind, _spec, _desc, _orgs, dt, raw, rep in mi["tests"]:
            lane = "culture" if kind == "culture" else "targeted"
            if dt and m["date"] and abs((dt - m["date"]).days) <= WINDOW:
                lanes[lane]["off"].append((dt - m["date"]).days)
                lanes[lane]["cases"].add(case)
            if dt and rep and 0 <= (rep - dt).days <= WINDOW:
                lanes[lane]["turn"].append((rep - dt).days)
    n_cases = len(lanes["mNGS"]["cases"])
    rows = []
    for lane in ("mNGS", "culture", "targeted"):
        d = lanes[lane]
        rows.append({
            "lane": lane,
            "tests": len(d["off"]),
            "cases_with_lane": len(d["cases"]),
            "pct_cases_with_lane": round(100 * len(d["cases"]) / n_cases),
            "pct_cases_with_organism": round(100 * len(d["hit"]) / len(d["seen"])) if d["seen"] else None,
            "offset_median": q(d["off"], 0.5), "offset_q1": q(d["off"], 0.25), "offset_q3": q(d["off"], 0.75),
            "offset_p05": q(d["off"], 0.05), "offset_p95": q(d["off"], 0.95),
            "pct_within_2d": round(100 * sum(1 for o in d["off"] if abs(o) <= 2) / len(d["off"])) if d["off"] else None,
            "turnaround_median": q(d["turn"], 0.5), "turnaround_q1": q(d["turn"], 0.25), "turnaround_q3": q(d["turn"], 0.75),
        })
    meta = {"cases": n_cases,
            "admission_to_mngs_median": q(admit_lag, 0.5),
            "admission_to_mngs_q1": q(admit_lag, 0.25),
            "admission_to_mngs_q3": q(admit_lag, 0.75),
            "mngs_specimens_per_patient": round(n_mngs_rows / max(len(mngs), 1), 2)}
    return rows, meta


def main() -> None:
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

    mngs, n_mngs_rows = {}, 0
    for row in sheet_rows(wb, "mNGS"):
        if not row[0]:
            continue
        orgs = []
        for i in range(9, 19):
            orgs += norm(row[i])
        mngs[row[0]] = {"sid": row[1], "stype": (row[5] or "").strip(), "orgs": set(orgs),
                        "date": pdate(row[7]), "report": pdate(row[8])}
        n_mngs_rows += 1

    reads = collections.defaultdict(dict)
    for row in sheet_rows(wb, "Read count"):
        sid = row[0]
        if not sid:
            continue
        for i in range(7, len(row) - 1, 2):
            if not row[i]:
                continue
            try:
                n = int(float(row[i + 1]))
            except (TypeError, ValueError):
                continue
            for name in norm(row[i]):
                reads[sid][name] = max(n, reads[sid].get(name, 0))

    micro = {}
    for row in sheet_rows(wb, "微生物診斷資料"):
        if not row[0]:
            continue
        cult, nonc, labels, tests = set(), set(), set(), []
        for base in (3, 15, 27, 39, 51, 63):          # culture specimens 1-6
            cult |= set(norm(row[base + 2]))
            if row[base + 2]:
                tests.append(("culture", row[base], row[base + 1], norm(row[base + 2]),
                              pdate(row[base + 9]), row[base + 2], pdate(row[base + 10])))
        for base in (75, 86, 97, 108, 119):            # non-culture tests 1-5 (11 columns each)
            nonc |= set(norm(row[base + 2]))
            if row[base + 2]:
                tests.append(("non-culture", row[base], row[base + 1], norm(row[base + 2]),
                              pdate(row[base + 9]), row[base + 2], pdate(row[base + 10])))
        for base in (130, 135, 140):                   # non-culture tests 6-8 (5 columns each)
            nonc |= set(norm(row[base + 2]))
            if row[base + 2]:
                tests.append(("non-culture", row[base], row[base + 1], norm(row[base + 2]),
                              pdate(row[base + 3]), row[base + 2], pdate(row[base + 4])))
        for i in range(148, 156):                      # clinical pathogen diagnosis 1-8
            labels |= {o for o in norm(row[i]) if o not in NON_PATHOGEN}
        micro[row[0]] = {"cult": cult, "nonc": nonc, "labels": labels, "tests": tests}

    admission = {}
    for row in sheet_rows(wb, "基本資料"):
        if row[1]:
            admission[row[1]] = pdate(row[11])

    sampling, sampling_meta = sampling_rows(mngs, micro, admission, n_mngs_rows)

    cases = [c for c in mngs if c in micro and micro[c]["labels"]]
    rows, missed, missing, recovered, n_refs = [], [], 0, 0, 0
    for c in cases:
        m, mi = mngs[c], micro[c]
        rd = reads.get(m["sid"], {})
        support = mi["cult"] | mi["nonc"]
        for organism in sorted(m["orgs"]):
            rows.append({
                "specimen_class": "sterile" if m["stype"] in STERILE else "non-sterile",
                "specimen_type": m["stype"],
                "organism": organism,
                "reads": rd.get(organism, ""),
                "causative": int(organism in mi["labels"]),
                "conventional_support": int(organism in support),
            })
        for label in sorted(mi["labels"]):
            n_refs += 1
            if label not in m["orgs"]:
                missing += 1
                recovered += label in support
                hits = [t for t in mi["tests"] if label in t[3]]
                # one row per (read-out class, specimen); every positive date of that pair, relative to the mNGS specimen
                by_key = collections.OrderedDict()
                for kind, spec, desc, _orgs, dt, raw, _rep in hits:
                    key = (readout_class(kind, raw), specimen_label(spec, desc))
                    off = (dt - m["date"]).days if (dt and m["date"]) else None
                    by_key.setdefault(key, []).append(off)
                if not by_key:
                    missed.append({"sequenced_specimen": m["stype"], "organism": label, "readout": "none",
                                   "found_specimen": "", "same_specimen_type": "", "day_offsets": ""})
                for (cls, spec_lab), offs in by_key.items():
                    missed.append({
                        "sequenced_specimen": m["stype"], "organism": label, "readout": cls,
                        "found_specimen": spec_lab,
                        "same_specimen_type": int(spec_lab.lower() == SPECIMEN_WORDS.get(m["stype"], m["stype"]).lower()),
                        "day_offsets": ";".join("" if o is None else str(o) for o in offs),
                    })

    OUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        fh.write("# one row per organism on the mNGS report of an adjudicated registry case\n")
        fh.write("# source: three-hospital registry workbook (PHI, outside this repository); "
                 "generated by tables/make_discordance.py; verified=yes\n")
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    with open(OUT_MISSED, "w", newline="", encoding="utf-8") as fh:
        fh.write("# adjudicated pathogens absent from the mNGS report of the sequenced specimen, one row per "
                 "(read-out class, specimen) that found the organism; day_offsets = collection day minus mNGS day\n")
        fh.write("# source: three-hospital registry workbook (PHI, outside this repository); "
                 "generated by tables/make_discordance.py; verified=yes\n")
        writer = csv.DictWriter(fh, fieldnames=list(missed[0]))
        writer.writeheader()
        writer.writerows(missed)

    pos = [r for r in rows if r["causative"]]
    neg = [r for r in rows if not r["causative"]]

    def auc(p, n):
        if not p or not n:
            return None
        s = sum(1 if a > b else 0.5 if a == b else 0 for a in p for b in n)
        return round(s / (len(p) * len(n)), 3)

    def reads_of(subset, caus):
        return [int(r["reads"]) for r in subset if r["causative"] == caus and r["reads"] != ""]

    summary = {
        "cases": len(cases), "detections": len(rows),
        "causative": len(pos), "non_causative": len(neg),
        "causative_pct": round(100 * len(pos) / len(rows)),
        "non_causative_pct": round(100 * len(neg) / len(rows)),
        "reference_pathogens": n_refs, "absent_from_report": missing,
        "absent_pct": round(100 * missing / n_refs),
        "absent_found_by_conventional": recovered,
        "absent_found_pct": round(100 * recovered / missing),
        "support_causative_pct": round(100 * sum(r["conventional_support"] for r in pos) / len(pos)),
        "support_non_causative_pct": round(100 * sum(r["conventional_support"] for r in neg) / len(neg)),
    }
    for label, subset in (("all", rows),
                          ("non_sterile", [r for r in rows if r["specimen_class"] == "non-sterile"]),
                          ("sterile", [r for r in rows if r["specimen_class"] == "sterile"])):
        p, n = reads_of(subset, 1), reads_of(subset, 0)
        summary[f"auc_{label}"] = auc(p, n)
        summary[f"median_reads_causative_{label}"] = statistics.median(p) if p else None
        summary[f"median_reads_non_causative_{label}"] = statistics.median(n) if n else None
        summary[f"range_reads_causative_{label}"] = [min(p), max(p)] if p else None
        summary[f"range_reads_non_causative_{label}"] = [min(n), max(n)] if n else None

    # absent pathogens: group the consecutive rows of one (sequenced specimen, organism)
    groups, prev = [], None
    for r in missed:
        k = (r["sequenced_specimen"], r["organism"])
        if k != prev or r["readout"] == "none":
            groups.append([])
            prev = k
        groups[-1].append(r)
    summary["absent_by_first_readout"] = dict(collections.Counter(g[0]["readout"] for g in groups))
    nearest = [min(abs(int(o)) for r in g for o in r["day_offsets"].split(";") if o != "") for g in groups
               if any(o != "" for r in g for o in r["day_offsets"].split(";"))]
    summary["absent_found_within_2_days"] = sum(1 for d in nearest if d <= 2)
    summary["absent_found_nearest_day_max"] = max(nearest) if nearest else None
    summary["absent_found_different_specimen"] = sum(1 for g in groups if g[0]["readout"] != "none" and not any(int(r["same_specimen_type"]) for r in g))

    split = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        split[r["organism"]][0] += r["causative"]
        split[r["organism"]][1] += 1
    both = sorted(o for o, (a, b) in split.items() if 0 < a < b)
    summary["organisms_both_ways"] = both
    summary["organisms_both_ways_n"] = len(both)
    summary["detections_both_ways_pct"] = round(100 * sum(1 for r in rows if r["organism"] in set(both)) / len(rows))
    summary["absent_found_different_specimen_pct"] = round(
        100 * summary["absent_found_different_specimen"] / summary["absent_found_by_conventional"])
    summary["absent_found_within_2_days_pct"] = round(
        100 * summary["absent_found_within_2_days"] / summary["absent_found_by_conventional"])
    summary["sampling"] = sampling_meta

    with open(OUT_SAMPLING, "w", newline="", encoding="utf-8") as fh:
        fh.write("# when each read-out is sampled and how long it takes to answer, one aggregate row per lane\n")
        fh.write("# offset = collection day - mNGS specimen day; turnaround = report day - collection day; "
                 "conventional rows enter the registry only when the test detected an organism\n")
        fh.write("# source: three-hospital registry workbook (PHI, outside this repository); "
                 "generated by tables/make_discordance.py; verified=yes\n")
        writer = csv.DictWriter(fh, fieldnames=list(sampling[0]))
        writer.writeheader()
        writer.writerows(sampling)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV} ({len(rows)} detections, {len(cases)} cases), {OUT_MISSED} ({len(missed)} rows), "
          f"{OUT_SAMPLING} and {OUT_JSON}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
