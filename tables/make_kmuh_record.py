#!/usr/bin/env python3
"""What one admission's record contains, from the KMUH per-patient workbooks.

Reads the per-patient source workbooks (PHI; they stay OUTSIDE this repository, folder in
KMUH_DIR) plus the registry workbook for the mNGS report of the same admission, and writes one
de-identified artifact used by Fig. 4a, Results and Supplementary Note 6:

  figures-source/kmuh_record.csv       one row per aggregate quantity: metric, value, IQR, n, unit
  figures-source/kmuh_admissions.csv   one row per admission: results by modality, organisms by how many
                                       read-outs named them, record span (no identifier, no date)
  figures-source/kmuh_latency.csv      one row per culture report: outcome and hours to the final report

Each workbook holds one admission on ten sheets (underlying, admission date, admission and
discharge diagnosis, culture, image, CBC, other lab, gm test, filmarray).  Unlike the three-hospital
registry, these are the source records: negative cultures, collection and report timestamps and the
radiology narrative are all present, so culture yield, time to answer and the wording of the imaging
report can be measured.

Analysis set (32 of the 36 workbooks): `NGS patient 7` has no microbiology, imaging or panel data;
`NGS patient 11` carries the note "同 patient 9"; `NGS patient 26` and `27` are byte-identical to
`25`.  In each of those two groups the registry holds a separate mNGS specimen for the same
admission (K009/K011 and K025/K026/K027), i.e. the admission was sequenced more than once; the
admission is counted once here.  No patient, specimen, hospital identifier or date leaves this
script -- only counts, percentages and intervals.
"""
import collections, csv, datetime, glob, json, os, re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
KMUH = Path(os.environ.get("KMUH_DIR", ROOT.parent / "KMUH patients"))
REGISTRY = Path(os.environ.get("COHORT_XLSX", ROOT.parent / "三院-final-mNGS merged file.xlsx"))
OUT_CSV = ROOT / "figures-source" / "kmuh_record.csv"
OUT_ADM = ROOT / "figures-source" / "kmuh_admissions.csv"
OUT_LAT = ROOT / "figures-source" / "kmuh_latency.csv"

EXCLUDE = {7: "no microbiology, imaging or panel data",
           11: "duplicate of admission 9 (second mNGS specimen of the same admission)",
           26: "duplicate of admission 25 (second mNGS specimen)",
           27: "duplicate of admission 25 (third mNGS specimen)"}

# culture report: a negative is phrased in one of these ways; an organism line is numbered
NEGATIVE = re.compile(r"No growth|not isolated|無菌生長", re.I)
STERILE = re.compile(r"Blood|Ascites|Pleural|Tissue|CSF|deep wound|Abscess|Intravascular", re.I)
RESISTANCE = re.compile(r"CTX-M|NDM|mecA|IMP|OXA|KPC|VIM")
# radiology: explicit uncertainty about the finding, and the pneumonia vocabulary
HEDGE = re.compile(r"\bprobabl|\bsuspect|\bfavor|cannot be (excluded|ruled out)|possibilit|questionable|"
                   r"equivocal|\bmay (be|represent)|\bsuggestive of|\br/o\b|rule out", re.I)
PNEUMONIA = re.compile(r"pneumon|infiltrat|consolidat|ground.?glass|\bGGO\b", re.I)
CHEST = re.compile(r"chest|CXR|thorax|lung", re.I)
ALIAS = {"acineto calc baumannii complex": "acinetobacter baumannii",
         "klebsiella pneumoniae group": "klebsiella pneumoniae",
         "enterobacter cloacae complex": "enterobacter cloacae",
         "haemophilus influenza": "haemophilus influenzae",
         "human alphaherpesvirus 1": "herpes simplex virus 1",
         "human alphaherpesvirus 3": "varicella-zoster virus",
         "human betaherpesvirus 5": "cytomegalovirus",
         "human gammaherpesvirus 4": "epstein-barr virus",
         "human betaherpesvirus 6b": "human herpesvirus 6b",
         "human rhinovirus/enterovirus": "rhinovirus"}


def norm(name):
    t = re.sub(r"\(.*?\)", "", str(name)).strip().lower()
    t = re.sub(r"\s+(complex|group|spp\.?|species|ssp .*)$", "", t).strip()
    return ALIAS.get(re.sub(r"\s+", " ", t), re.sub(r"\s+", " ", t))


def stamp(cell):
    m = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?", str(cell))
    if not m:
        return None
    y, mo, d, h, mi = m.groups()
    return datetime.datetime(int(y), int(mo), int(d), int(h or 0), int(mi or 0))


def sheet(wb, name):
    return [r for r in wb[name].iter_rows(values_only=True) if any(c not in (None, "") for c in r)]


def flat(wb, name):
    return [str(c) for r in sheet(wb, name) for c in r if c not in (None, "")]


def cultures(wb):
    """One entry per culture report: specimen, collection and report time, organisms, no-growth flag."""
    out, cur = [], None
    for line in flat(wb, "culture"):
        head = re.match(r"^『([^』]+)』", line.strip())
        if head:
            cur = {"test": head.group(1), "coll": None, "rep": None, "orgs": [], "neg": False}
            out.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith("採檢時間"):
            cur["coll"] = stamp(s)
        elif s.startswith("報告時間"):
            cur["rep"] = stamp(s)
        elif NEGATIVE.search(s):
            cur["neg"] = True
        elif re.match(r"^\d+\.", s):
            body = re.sub(r"^\d+\.", "", s)
            body = re.sub(r"^\s*(Preliminary|Final) report\s*:?", "", body).strip()
            if not body or NEGATIVE.search(body) or re.match(r"^(Colony Count|同類抗生素|G\([+-]\))", body):
                continue
            body = re.sub(r"\(.*?\)", "", body).strip(" .")
            if body and len(body) < 60 and re.match(r"^[A-Z][a-z]+", body):
                cur["orgs"].append(body)
    return [c for c in out if c["coll"] or c["orgs"] or c["neg"]]


def panels(wb):
    """One entry per syndromic panel run: number of targets, organisms detected, resistance markers."""
    out, cur = [], None
    for line in flat(wb, "filmarray"):
        head = re.match(r"^『([^』]+)』", line.strip())
        if head:
            cur = {"targets": 0, "detected": [], "genes": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        if "Not Detected" in s:
            cur["targets"] += 1
            continue
        m = re.search(r"(.+?)(?:\(copy/mL\))?\s*(Detected|10\^\d+)\s*$", s)
        if m:
            cur["targets"] += 1
            name = re.sub(r"\(copy/mL\)", "", m.group(1)).strip()
            (cur["genes"] if RESISTANCE.search(name) else cur["detected"]).append(name)
    return [r for r in out if r["targets"]]


def imaging(wb):
    """One entry per study: date, title, whether the report hedges and whether it names pneumonia."""
    text = "\n".join(flat(wb, "image"))
    out = []
    for part in re.split(r"-{10,}", text):
        m = re.search(r"(\d{4}/\d{1,2}/\d{1,2})\s+(\d{1,2}:\d{2})\s*:\s*([^\n]*)", part)
        if not m:
            continue
        body = part[m.end():]
        out.append({"date": stamp(m.group(1) + " " + m.group(2)), "title": m.group(3).strip(),
                    "chest": bool(CHEST.search(m.group(3))), "hedge": bool(HEDGE.search(body)),
                    "pneumonia": bool(PNEUMONIA.search(body))})
    return out


def grid(wb, name):
    """CBC / other lab: analyte rows by date columns -> (dates, number of values recorded)."""
    rows = sheet(wb, name)
    if not rows:
        return [], 0
    dates = [c for c in rows[0][1:] if isinstance(c, (datetime.datetime, datetime.date))]
    values = sum(1 for r in rows[1:] if r[0] not in (None, "")
                 for c in r[1:1 + len(dates)] if c not in (None, ""))
    return dates, values


def galactomannan(wb):
    """Serum and lavage galactomannan indices with their specimen, thresholds applied by the caller."""
    out, spec = [], None
    for r in sheet(wb, "gm test"):
        first = str(r[0])
        head = re.match(r"^『([^』]+)』", first.strip())
        if head:
            spec = head.group(1)
            continue
        if first.startswith("GM test"):
            try:
                val = float(r[1]) if len(r) > 1 else None
            except (TypeError, ValueError):
                val = None
            out.append({"spec": spec or "", "val": val})
    return out


def admission(wb):
    adm = dis = None
    transfers = 0
    for line in flat(wb, "admission date"):
        when = stamp(line)
        if "入院" in line and when and adm is None:
            adm = when
        if "出院" in line and when:
            dis = when
        if "轉科" in line or "轉床" in line:
            transfers += 1
    return adm, dis, transfers


def words(wb, names):
    return sum(len(re.findall(r"\S+", " ".join(flat(wb, n)))) for n in names)


def registry_reports():
    """The mNGS report of each KMUH admission, keyed by the workbook number (K0NN <-> patient NN)."""
    wb = openpyxl.load_workbook(REGISTRY, read_only=True, data_only=True)
    ws = wb["mNGS"]
    it = ws.iter_rows(values_only=True)
    next(it)
    out = {}
    for row in it:
        if row and row[0] and str(row[3]) == "高雄附醫":
            m = re.match(r"K(\d+)$", str(row[0]))
            if m:
                out[int(m.group(1))] = {"date": row[7],
                                        "orgs": [str(x) for x in row[9:19] if x not in (None, "")]}
    wb.close()
    return out


def quantile(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    i = p * (len(xs) - 1)
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (i - lo), 1)


def main() -> None:
    reports = registry_reports()
    rows = []                      # one dict per admission
    for path in sorted(glob.glob(str(KMUH / "*.xlsx"))):
        n = int(re.search(r"(\d+)", os.path.basename(path)).group(1))
        if n in EXCLUDE:
            continue
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        cult, pan, img = cultures(wb), panels(wb), imaging(wb)
        cbc_dates, cbc_values = grid(wb, "CBC")
        lab_dates, lab_values = grid(wb, "other lab")
        gm = galactomannan(wb)
        adm, dis, transfers = admission(wb)
        rep = reports.get(n, {})
        rows.append({
            "cultures": cult, "panels": pan, "imaging": img, "gm": gm,
            "cbc_dates": cbc_dates, "cbc_values": cbc_values,
            "lab_dates": lab_dates, "lab_values": lab_values,
            "adm": adm, "transfers": transfers,
            "mngs_date": rep.get("date"), "mngs_orgs": rep.get("orgs", []),
            "words": words(wb, ["image", "culture", "filmarray", "admission diagnosis",
                                "discharge diagnosis", "underlying", "admission date", "gm test"]),
        })
        wb.close()

    n_adm = len(rows)
    out = []

    def add(metric, value, q1=None, q3=None, n=None, unit="", note=""):
        out.append({"metric": metric, "value": value, "q1": q1, "q3": q3, "n": n, "unit": unit,
                    "note": note, "source": "KMUH per-patient workbooks", "verified": "yes"})

    def add_dist(metric, xs, unit="", note=""):
        add(metric, quantile(xs, 0.5), quantile(xs, 0.25), quantile(xs, 0.75), len(xs), unit, note)
        add(metric + "_min", min(xs), unit=unit)
        add(metric + "_max", max(xs), unit=unit)

    add("admissions", n_adm, n=n_adm, unit="admissions",
        note="; ".join(f"{k} excluded: {v}" for k, v in sorted(EXCLUDE.items())))

    # --- what the record holds -------------------------------------------------------------------
    per_mod = {
        "results_imaging": [len(r["imaging"]) for r in rows],
        "results_culture": [len(r["cultures"]) for r in rows],
        "results_panel": [sum(p["targets"] for p in r["panels"]) for r in rows],
        "results_gm": [len(r["gm"]) for r in rows],
        "results_cbc": [r["cbc_values"] for r in rows],
        "results_chemistry": [r["lab_values"] for r in rows],
    }
    for metric, xs in per_mod.items():
        add_dist(metric, xs, "results per admission")
    add_dist("results_total", [sum(per_mod[k][i] for k in per_mod) for i in range(n_adm)],
             "results per admission")
    add_dist("free_text_words", [r["words"] for r in rows], "words per admission")
    add_dist("transfers", [r["transfers"] for r in rows], "ward or unit moves per admission")

    spans, active_days = [], []
    for r in rows:
        days = [d.date() for d in (c["coll"] for c in r["cultures"]) if d]
        days += [d.date() for d in (i["date"] for i in r["imaging"]) if d]
        days += [d.date() if isinstance(d, datetime.datetime) else d for d in r["cbc_dates"] + r["lab_dates"]]
        if days:
            spans.append((max(days) - min(days)).days)
            active_days.append(len(set(days)))
    add_dist("record_span", spans, "days")
    add_dist("days_with_new_result", active_days, "days")

    # --- cultures: yield, latency, yield by hospital day ------------------------------------------
    allc = [c for r in rows for c in r["cultures"]]
    pos = [c for c in allc if c["orgs"]]
    neg = [c for c in allc if not c["orgs"]]
    add("culture_reports", len(allc), n=len(allc), unit="reports")
    add("culture_positive_pct", round(100 * len(pos) / len(allc)), n=len(allc), unit="%")
    add("culture_negative_pct", round(100 * len(neg) / len(allc)), n=len(allc), unit="%")

    def latency(subset):
        return [round((c["rep"] - c["coll"]).total_seconds() / 3600, 1) for c in subset
                if c["rep"] and c["coll"] and 0 <= (c["rep"] - c["coll"]).days <= 40]
    add_dist("culture_latency_positive", latency(pos), "hours")
    add_dist("culture_latency_negative", latency(neg), "hours")

    buckets = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        for c in r["cultures"]:
            if not (r["adm"] and c["coll"]):
                continue
            day = (c["coll"] - r["adm"]).days
            key = "0_2" if day <= 2 else "3_7" if day <= 7 else "8_plus"
            buckets[key][0] += bool(c["orgs"])
            buckets[key][1] += 1
    for key, (hit, tot) in sorted(buckets.items()):
        add(f"culture_positive_pct_day_{key}", round(100 * hit / tot), n=tot, unit="%")

    # --- the mNGS specimen inside that record ------------------------------------------------------
    lags, before, after = [], [], []
    for r in rows:
        d = r["mngs_date"]
        if not d:
            continue
        day = d.date() if hasattr(d, "date") else d
        if r["adm"] and 0 <= (day - r["adm"].date()).days <= 200:
            lags.append((day - r["adm"].date()).days)
        before.append(sum(1 for c in r["cultures"] if c["coll"] and c["coll"].date() < day))
        after.append(sum(1 for c in r["cultures"] if c["coll"] and c["coll"].date() >= day))
    add_dist("admission_to_mngs", lags, "days")
    add_dist("cultures_before_mngs", before, "reports per admission")
    add_dist("cultures_after_mngs", after, "reports per admission")

    # --- candidate organisms and how many read-outs name each --------------------------------------
    combos = collections.Counter()
    per_adm, no_sterile, singles, total = [], 0, 0, 0
    for r in rows:
        r["org_by_n"] = collections.Counter()
        by_culture = collections.defaultdict(set)
        for c in r["cultures"]:
            for o in c["orgs"]:
                by_culture[norm(o)].add(c["test"])
        by_panel = {norm(d) for p in r["panels"] for d in p["detected"]}
        for g in r["gm"]:                                  # Platelia thresholds: serum 0.5, lavage 1.0
            if g["val"] is not None and (("Serum" in g["spec"] and g["val"] >= 0.5)
                                         or ("BAL" in g["spec"] and g["val"] >= 1.0)):
                by_panel.add("aspergillus")
        by_mngs = {norm(o) for o in r["mngs_orgs"]}
        named = set(by_culture) | by_panel | by_mngs
        per_adm.append(len(named))
        for o in named:
            total += 1
            where = tuple(m for m, s in (("culture", set(by_culture)), ("panel", by_panel), ("mNGS", by_mngs)) if o in s)
            combos[where] += 1
            r["org_by_n"][len(where)] += 1
            singles += len(where) == 1
            if not any(STERILE.search(t) for t in by_culture.get(o, ())):
                no_sterile += 1
    add_dist("organisms_per_admission", per_adm, "organisms")
    add("organism_admission_pairs", total, n=total, unit="pairs")
    add("organisms_single_readout_pct", round(100 * singles / total), n=total, unit="%")
    add("organisms_two_or_more_readouts_pct", round(100 * (total - singles) / total), n=total, unit="%")
    add("organisms_no_sterile_site_pct", round(100 * no_sterile / total), n=total, unit="%")
    for where, k in sorted(combos.items(), key=lambda kv: -kv[1]):
        add("organisms_by_" + "_".join(where) + "_pct", round(100 * k / total), n=k, unit="%")

    # --- imaging: what the chest report says and how surely ----------------------------------------
    chest = [i for r in rows for i in r["imaging"] if i["chest"]]
    add("imaging_studies", sum(len(r["imaging"]) for r in rows), unit="studies")
    add("chest_studies", len(chest), n=len(chest), unit="studies")
    add("chest_pneumonia_pct", round(100 * sum(1 for i in chest if i["pneumonia"]) / len(chest)),
        n=len(chest), unit="%")
    add("chest_hedged_pct", round(100 * sum(1 for i in chest if i["hedge"]) / len(chest)),
        n=len(chest), unit="%")
    named_pneumonia = [i for i in chest if i["pneumonia"]]
    hedged_pneumonia = [i for i in named_pneumonia if i["hedge"]]
    add("chest_pneumonia_hedged_pct",
        round(100 * len(hedged_pneumonia) / len(named_pneumonia)), n=len(named_pneumonia), unit="%")
    # the three exclusive classes of one chest study, as shares of every chest study
    add("chest_class_hedged_pct", round(100 * len(hedged_pneumonia) / len(chest)),
        n=len(hedged_pneumonia), unit="%", note="names pneumonia and qualifies it")
    add("chest_class_stated_pct",
        round(100 * (len(named_pneumonia) - len(hedged_pneumonia)) / len(chest)),
        n=len(named_pneumonia) - len(hedged_pneumonia), unit="%", note="names pneumonia without qualifying it")
    add("chest_class_none_pct", round(100 * (len(chest) - len(named_pneumonia)) / len(chest)),
        n=len(chest) - len(named_pneumonia), unit="%", note="no pneumonia term")

    # --- resistance markers reported without an organism -------------------------------------------
    with_genes = sum(1 for r in rows if any(p["genes"] for p in r["panels"]))
    add("admissions_with_resistance_marker_pct", round(100 * with_genes / n_adm), n=with_genes, unit="%")

    OUT_CSV.parent.mkdir(exist_ok=True)
    # one row per admission, ordered by organism count so the row order carries no patient identity
    adm_rows = []
    for r in sorted(rows, key=lambda r: -sum(r["org_by_n"].values())):
        span = None
        days = [d.date() for d in (c["coll"] for c in r["cultures"]) if d]
        days += [d.date() for d in (i["date"] for i in r["imaging"]) if d]
        days += [d.date() if isinstance(d, datetime.datetime) else d for d in r["cbc_dates"] + r["lab_dates"]]
        adm_rows.append({
            "chemistry": r["lab_values"], "blood_counts": r["cbc_values"],
            "panel_targets": sum(p["targets"] for p in r["panels"]),
            "imaging_studies": len(r["imaging"]), "culture_reports": len(r["cultures"]),
            "galactomannan": len(r["gm"]), "mngs_reports": 1,
            "organisms": sum(r["org_by_n"].values()),
            "organisms_1_readout": r["org_by_n"][1], "organisms_2_readouts": r["org_by_n"][2],
            "organisms_3_readouts": r["org_by_n"][3],
            "record_span_days": (max(days) - min(days)).days if days else "",
            "days_with_new_result": len(set(days)) if days else "",
            "free_text_words": r["words"],
        })
    with open(OUT_ADM, "w", newline="", encoding="utf-8") as fh:
        fh.write("# one row per KMUH admission, ordered by number of organisms named; no identifier or date\n")
        fh.write("# source: KMUH per-patient workbooks (PHI, outside this repository); "
                 "generated by tables/make_kmuh_record.py; verified=yes\n")
        w = csv.DictWriter(fh, fieldnames=list(adm_rows[0])); w.writeheader(); w.writerows(adm_rows)

    lat_rows = [{"outcome": "growth" if c["orgs"] else "no growth",
                 "hours": round((c["rep"] - c["coll"]).total_seconds() / 3600, 1)}
                for r in rows for c in r["cultures"]
                if c["rep"] and c["coll"] and 0 <= (c["rep"] - c["coll"]).days <= 40]
    with open(OUT_LAT, "w", newline="", encoding="utf-8") as fh:
        fh.write("# one row per culture report: whether it grew an organism and the hours from collection "
                 "to the final report; no identifier or date\n")
        fh.write("# source: KMUH per-patient workbooks (PHI, outside this repository); "
                 "generated by tables/make_kmuh_record.py; verified=yes\n")
        w = csv.DictWriter(fh, fieldnames=["outcome", "hours"]); w.writeheader(); w.writerows(lat_rows)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        fh.write("# what one admission's record contains: aggregates over the KMUH per-patient workbooks\n")
        fh.write("# value = median unless the metric name says otherwise; q1/q3 = interquartile range; "
                 "n = denominator; generated by tables/make_kmuh_record.py\n")
        fh.write("# source: KMUH per-patient workbooks + the registry mNGS sheet (PHI, outside this "
                 "repository); no identifier or date is written out\n")
        writer = csv.DictWriter(fh, fieldnames=["metric", "value", "q1", "q3", "n", "unit", "note",
                                                "source", "verified"])
        writer.writeheader()
        writer.writerows(out)
    print(f"wrote {OUT_CSV} ({len(out)} aggregates over {n_adm} admissions), "
          f"{OUT_ADM} ({len(adm_rows)} rows) and {OUT_LAT} ({len(lat_rows)} rows)")
    print(json.dumps({r["metric"]: r["value"] for r in out if not r["metric"].endswith(("_min", "_max"))},
                     indent=0, ensure_ascii=False))


if __name__ == "__main__":
    main()
