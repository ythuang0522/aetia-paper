#!/usr/bin/env python3
"""Build references.bib from Crossref metadata so no citation is typed from memory.

Usage: python3 notes/resolve_refs.py   (writes ../references.bib; prints a resolution report)
Entries without a DOI (conference papers) are appended from MANUAL below, verbatim.
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "references.bib"

# key -> DOI. Keep this list as the single source of truth for cited works.
DOIS = {
    "chiu2019clinical": "10.1038/s41576-019-0113-7",
    "gu2019clinical": "10.1146/annurev-pathmechdis-012418-012751",
    "wilson2019clinical": "10.1056/NEJMoa1803396",
    "blauwkamp2019analytical": "10.1038/s41564-018-0349-6",
    "langelier2018integrating": "10.1073/pnas.1809700115",
    "miao2018microbiological": "10.1093/cid/ciy693",
    "charalampous2019nanopore": "10.1038/s41587-019-0156-5",
    "simner2018understanding": "10.1093/cid/cix881",
    "metlay2019diagnosis": "10.1164/rccm.201908-1581ST",
    "kalil2016management": "10.1093/cid/ciw353",
    "buchan2020practical": "10.1128/JCM.00135-20",
    "jain2015community": "10.1056/NEJMoa1500245",
    "singhal2023large": "10.1038/s41586-023-06291-2",
    "mcduff2025towards": "10.1038/s41586-025-08869-4",
    "tu2025towards": "10.1038/s41586-025-08866-7",
    "tang2024medagents": "10.18653/v1/2024.findings-acl.33",
    "maillard2024chatbot": "10.1093/cid/ciad632",
    "hager2024evaluation": "10.1038/s41591-024-03097-1",
    "salter2014reagent": "10.1186/s12915-014-0087-z",
    "charlson2011topographical": "10.1164/rccm.201104-0655OC",
    "dickson2016microbiome": "10.1146/annurev-physiol-021115-105238",
    "hogan2021clinical": "10.1093/cid/ciaa035",
    "diao2022metagenomics": "10.1016/j.jare.2021.09.012",
    "han2019mngs": "10.1080/1040841X.2019.1681933",
    "miller2022role": "10.1093/clinchem/hvab173",
    "schlaberg2017validation": "10.5858/arpa.2016-0539-RA",
    "xiong2024benchmarking": "10.18653/v1/2024.findings-acl.372",
    "ji2023survey": "10.1145/3571730",
    "bossuyt2015stard": "10.1136/bmj.h5527",
    "miller2019laboratory": "10.1101/gr.238170.118",
    "chen2020clinical": "10.1093/cid/ciaa1516",
    "qiu2024llm": "10.1038/s42256-024-00944-1",
    "rajpurkar2022ai": "10.1038/s41591-021-01614-0",
    "ghassemi2021false": "10.1016/S2589-7500(21)00208-9",
    "turpin2023language": "10.52202/075280-3275",
    "kapoor2023leakage": "10.1016/j.patter.2023.100804",
    "donnelly2020revision": "10.1093/cid/ciz1008",
    # Methods: sequencing laboratory workflow and conventional assays (added 2026-09-20)
    "takahashi2026diagnostic": "10.3389/fcimb.2026.1823299",   # Asia Pathogenomics pipeline: AVITI, T2T-CHM13, database, control thresholds (Supp. Methods)
    "chou2025investigating": "10.3390/biomedicines13010142",    # KMUH BALF mNGS by Asia Pathogenomics: extraction, MGIEasy, DNBSEQ-G50RS; FilmArray at KMUH
    "hung2021investigating": "10.3389/fphar.2021.747280",       # KMUH ICU: Platelia Aspergillus galactomannan EIA in serum and BAL
    "bolger2014trimmomatic": "10.1093/bioinformatics/btu170",
    "schmieder2011quality": "10.1093/bioinformatics/btr026",
    "nurk2022complete": "10.1126/science.abj6987",
}

MANUAL = r"""
@inproceedings{lewis2020retrieval,
  author    = {Lewis, Patrick and Perez, Ethan and Piktus, Aleksandra and Petroni, Fabio and Karpukhin, Vladimir and Goyal, Naman and K{\"u}ttler, Heinrich and Lewis, Mike and Yih, Wen-tau and Rockt{\"a}schel, Tim and Riedel, Sebastian and Kiela, Douwe},
  title     = {Retrieval-augmented generation for knowledge-intensive {NLP} tasks},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {33},
  pages     = {9459--9474},
  year      = {2020},
  note      = {arXiv:2005.11401}
}

@misc{li2013aligning,
  author    = {Li, Heng},
  title     = {Aligning sequence reads, clone sequences and assembly contigs with {BWA-MEM}},
  year      = {2013},
  note      = {arXiv:1303.3997}
}

@inproceedings{kim2024mdagents,
  author    = {Kim, Yubin and Park, Chanwoo and Jeong, Hyewon and Chan, Yik Siu and Xu, Xuhai and McDuff, Daniel and Lee, Hyeonhoon and Ghassemi, Marzyeh and Breazeal, Cynthia and Park, Hae Won},
  title     = {{MDAgents}: an adaptive collaboration of {LLMs} for medical decision-making},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {37},
  year      = {2024},
  note      = {arXiv:2404.15155}
}
"""


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return html.unescape(" ".join(s.split()))


def latex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")


def protect_caps(title: str) -> str:
    """Brace words with inner capitals or acronyms so BibTeX keeps their case."""
    out = []
    for w in title.split(" "):
        core = re.sub(r"[^A-Za-z0-9-]", "", w)
        if (len(core) > 1 and (core.isupper() or re.search(r"[a-z][A-Z]|\d[A-Z]|[A-Z]{2}", core))) and not w.startswith("{"):
            out.append("{" + w + "}")
        else:
            out.append(w)
    return " ".join(out)


def fetch(doi: str) -> dict:
    req = urllib.request.Request(f"https://api.crossref.org/works/{doi}",
                                 headers={"User-Agent": "ober-manuscript-bib/1.0 (mailto:ythuang@cs.ccu.edu.tw)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["message"]


def entry(key: str, m: dict) -> str:
    authors = []
    for a in m.get("author", []):
        if "family" in a:
            authors.append(f"{a['family']}, {a.get('given', '')}".strip().rstrip(","))
        elif "name" in a:
            authors.append("{" + a["name"] + "}")
    title = protect_caps(latex_escape(strip_tags(m["title"][0])))
    journal = latex_escape(strip_tags((m.get("container-title") or [""])[0]))
    # Prefer the print-issue year (journal citation convention); fall back to the online date.
    year = (m.get("published-print") or m.get("issued") or m.get("published-online"))["date-parts"][0][0]
    kind = "article"
    fields = [f"  author    = {{{' and '.join(authors)}}}", f"  title     = {{{title}}}"]
    if m.get("type") == "proceedings-article":
        kind = "inproceedings"
        fields.append(f"  booktitle = {{{journal}}}")
    else:
        fields.append(f"  journal   = {{{journal}}}")
    if m.get("volume"):
        fields.append(f"  volume    = {{{m['volume']}}}")
    if m.get("issue") and kind == "article":
        fields.append(f"  number    = {{{m['issue']}}}")
    if m.get("page"):
        fields.append(f"  pages     = {{{m['page'].replace('-', '--')}}}")
    fields.append(f"  year      = {{{year}}}")
    fields.append(f"  doi       = {{{m['DOI']}}}")
    return f"@{kind}{{{key},\n" + ",\n".join(fields) + "\n}\n"


def main() -> int:
    entries, failed = [], []
    for key, doi in DOIS.items():
        try:
            m = fetch(doi)
            entries.append(entry(key, m))
            print(f"ok   {key:28s} {strip_tags(m['title'][0])[:70]} | {(m.get('container-title') or [''])[0][:30]} {m['issued']['date-parts'][0][0]}")
        except Exception as exc:  # noqa: BLE001
            failed.append((key, doi, str(exc)))
            print(f"FAIL {key:28s} {doi} -> {exc}")
    header = ("% references.bib is generated by notes/resolve_refs.py from Crossref metadata (DOI list in that script).\n"
              "% Conference papers without DOI are in the MANUAL block of the same script. Regenerate rather than hand-edit.\n\n")
    OUT.write_text(header + "\n".join(entries) + MANUAL, encoding="utf-8")
    print(f"\nwrote {OUT} with {len(entries)} Crossref entries + manual; failed: {len(failed)}")
    for f in failed:
        print("  unresolved:", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
