#!/usr/bin/env python3
"""Build the claude.ai hub for the compiled manuscript: page images, PDFs, figure previews, index.html.

Usage (from the paper folder, after `make`):
    python3 notes/hub/build_hub.py            # writes hub-build/ (gitignored)
Then publish with the Artifact tool, keeping the SAME artifact URL:
    file_path = hub-build/index.html, root = hub-build, files = contents of hub-build/files.json
The PDFs and images are published as supporting files at fixed paths next to the page
(main.pdf, supplementary.pdf, pages/main-NN.jpg, pages/supp-NN.jpg, figures/figN.png), so every
rebuild replaces them in place and the links never change. Pages that no longer exist are removed
by the nulls in files.json. In a new session, list the artifact's files first
(Artifact tool: action "list", scope "files") before republishing, or the replace is refused.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hub-build"
ARTIFACT = "https://claude.ai/artifact/PB2BPxhvChugJsDavnGsKf"
REPO = "https://github.com/ythuang0522/aetia-paper"
DPI = 110
MAX_PAGES = 80  # nulls are emitted up to this count so stale pages disappear on republish


def run(*cmd: str) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def pages_of(pdf: Path) -> int:
    return int(re.search(r"Pages:\s+(\d+)", run("pdfinfo", str(pdf))).group(1))


def render_pages(pdf: Path, prefix: str) -> int:
    n = pages_of(pdf)
    tmp = OUT / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    run("pdftoppm", "-jpeg", "-jpegopt", "quality=82", "-r", str(DPI), str(pdf), str(tmp / prefix))
    (OUT / "pages").mkdir(exist_ok=True)
    for i in range(1, n + 1):
        cands = [tmp / f"{prefix}-{i}.jpg", tmp / f"{prefix}-{i:02d}.jpg", tmp / f"{prefix}-{i:03d}.jpg"]
        src = next(c for c in cands if c.exists())
        shutil.move(str(src), OUT / "pages" / f"{prefix}-{i:02d}.jpg")
    shutil.rmtree(tmp)
    return n


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "figures").mkdir(parents=True)
    shutil.copy(ROOT / "main.pdf", OUT / "main.pdf")
    shutil.copy(ROOT / "Supplementary.pdf", OUT / "supplementary.pdf")
    n_main = render_pages(ROOT / "main.pdf", "main")
    n_supp = render_pages(ROOT / "Supplementary.pdf", "supp")
    figs = [("fig1", "fig1_overview"), ("fig2", "fig2_benchmark"),
            ("fig3", "fig3_explanation"), ("ed1", "ed1_cohort_flow"),
            ("ed2", "ed2_registry"), ("ed3", "ed3_trajectory")]
    fig_labels = {"fig1": "Fig. 1", "fig2": "Fig. 2", "fig3": "Fig. 3",
                  "ed1": "Extended Data Fig. 1", "ed2": "Extended Data Fig. 2",
                  "ed3": "Extended Data Fig. 3"}
    for short, name in figs:
        run("rsvg-convert", "-f", "png", "-z", "1.6", "-o", str(OUT / "figures" / f"{short}.png"), str(ROOT / "figures" / f"{name}.svg"))

    tex = [ROOT / "main.tex", ROOT / "Supplementary.tex", ROOT / "tables" / "table1_cohort.tex", *sorted((ROOT / "sections").glob("*.tex"))]
    todo = sum(t.read_text(encoding="utf-8").count("\\todo{") for t in tex)
    refs = sum(1 for ln in (ROOT / "references.bib").read_text(encoding="utf-8").splitlines() if ln.startswith("@"))
    commit = run("git", "-C", str(ROOT), "log", "-1", "--format=%h").strip()
    dirty = bool(run("git", "-C", str(ROOT), "status", "--porcelain").strip())
    date = run("git", "-C", str(ROOT), "log", "-1", "--format=%ad", "--date=short").strip()

    def page_imgs(prefix: str, n: int, label: str) -> str:
        return "".join(
            f'<figure class="page"><img src="pages/{prefix}-{i:02d}.jpg" alt="{label} page {i}" loading="lazy" width="909" height="1286">'
            f'<figcaption>{label} · page {i} of {n}</figcaption></figure>'
            for i in range(1, n + 1))

    figcaps = {
        "fig1": "Overview of AETIA (concept-only redesign, 2026-09-21): language-model agents per read-out, a funnel of four rule-based filters with colonizer guardrails, a safety review that can flag but not pick, an evidence matrix for every candidate (articles read by a language model against a label-blind case card; sequencing, direct tests and colonization graded by rules), and the final rule that freezes the list before the explanation is written.",
        "fig2": "Combined performance figure: precision–recall planes and P/R/F1 for AETIA against individual diagnostic read-outs (n = 55) and four language models prompted directly on identical data (n = 41).",
        "fig3": "Clinical evidence underlying individual pathogen-selection decisions: source-record complexity, worked evidence traces and the disposition of all 518 candidates.",
        "ed1": "Cohort flow from the 105-specimen registry to the 55-patient R5 cohort and the 41-patient direct-prompting cohort (Extended Data).",
        "ed2": "Registry mNGS report burden by specimen and patient stratum, with organism-level culture agreement and class composition.",
        "ed3": "Physiological trajectories after the mNGS specimen under conventional care; no patient in this analysis received AETIA.",
    }
    fig_html = "".join(
        f'<figure><img src="figures/{k}.png" alt="{fig_labels[k]}" loading="lazy"><figcaption><b>{fig_labels[k]}</b> {figcaps[k]}</figcaption></figure>'
        for k, _ in figs)

    html = f"""<title>AETIA Manuscript</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{{
  --bg:#f7f8fb; --surface:#ffffff; --ink:#151a24; --ink-2:#4a5262; --muted:#7a8291; --line:#dfe3ea;
  --accent:#1d4ed8; --accent-ink:#ffffff; --accent-soft:#e6edfb; --flag:#b45309; --flag-soft:#fdf1df; --page-shadow:rgba(21,26,36,.12);
  color-scheme:light;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --bg:#0f1319; --surface:#171c25; --ink:#eef1f6; --ink-2:#b7bfcc; --muted:#8a93a3; --line:#2a323f;
    --accent:#6f9bff; --accent-ink:#0b1020; --accent-soft:#1a2540; --flag:#f0b35a; --flag-soft:#2c2114; --page-shadow:rgba(0,0,0,.5);
    color-scheme:dark;
  }}
}}
:root[data-theme="dark"]{{
  --bg:#0f1319; --surface:#171c25; --ink:#eef1f6; --ink-2:#b7bfcc; --muted:#8a93a3; --line:#2a323f;
  --accent:#6f9bff; --accent-ink:#0b1020; --accent-soft:#1a2540; --flag:#f0b35a; --flag-soft:#2c2114; --page-shadow:rgba(0,0,0,.5);
  color-scheme:dark;
}}
body{{background:var(--bg); color:var(--ink); font-family:"Source Sans 3","Helvetica Neue",Arial,sans-serif; font-size:16px; line-height:1.5;}}
.wrap{{max-width:1080px; margin:0 auto; padding-block:36px 64px; padding-inline:20px;}}
.eyebrow{{font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600;}}
h1{{font-family:"Source Serif 4",Georgia,"Times New Roman",serif; font-weight:600; font-size:clamp(24px,3.4vw,36px); line-height:1.2; margin:8px 0 10px; text-wrap:balance; max-width:30ch;}}
.sub{{color:var(--ink-2); max-width:70ch; margin:0 0 22px;}}
.actions{{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:28px;}}
.btn{{display:inline-flex; align-items:center; gap:8px; padding:10px 16px; border-radius:8px; border:1px solid var(--line); background:var(--surface); color:var(--ink); text-decoration:none; font-weight:600;}}
.btn:hover{{border-color:var(--accent);}} .btn:focus-visible{{outline:2px solid var(--accent); outline-offset:2px;}}
.btn.primary{{background:var(--accent); color:var(--accent-ink); border-color:var(--accent);}}
.grid{{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:28px;}}
@media (max-width:720px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}
.stat{{background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:14px 16px;}}
.stat .k{{font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-weight:600;}}
.stat .v{{font-size:26px; font-weight:600; font-variant-numeric:tabular-nums; margin-top:2px;}}
.stat .n{{font-size:13px; color:var(--ink-2);}}
.tabs{{display:flex; gap:6px; border-bottom:1px solid var(--line); margin:8px 0 18px;}}
.tabs button{{appearance:none; background:none; border:0; border-bottom:2px solid transparent; padding:10px 14px; font:inherit; font-weight:600; color:var(--ink-2); cursor:pointer;}}
.tabs button[aria-selected="true"]{{color:var(--accent); border-bottom-color:var(--accent);}}
.tabs button:focus-visible{{outline:2px solid var(--accent); outline-offset:-2px;}}
.reader{{display:grid; gap:18px; justify-items:center;}}
.page{{margin:0; width:100%; max-width:820px;}}
.page img{{display:block; width:100%; height:auto; background:#ffffff; border:1px solid var(--line); box-shadow:0 2px 12px var(--page-shadow); border-radius:3px;}}
.page figcaption{{font-size:12px; color:var(--muted); text-align:center; margin-top:6px; font-variant-numeric:tabular-nums;}}
h2{{font-family:"Source Serif 4",Georgia,serif; font-weight:600; font-size:22px; margin:36px 0 12px;}}
.flags{{display:grid; gap:10px;}}
.flag{{display:grid; grid-template-columns:auto 1fr; gap:12px; align-items:start; background:var(--flag-soft); border-left:3px solid var(--flag); border-radius:8px; padding:12px 14px;}}
.flag .tag{{font-size:12px; font-weight:600; color:var(--flag); text-transform:uppercase; letter-spacing:.08em; padding-top:3px;}}
.flag p{{margin:0; color:var(--ink);}}
figure{{margin:0 0 26px; background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:14px;}}
figure img{{display:block; width:100%; height:auto; border-radius:6px; background:#ffffff;}}
figcaption{{font-size:14px; color:var(--ink-2); margin-top:10px;}}
.meta{{color:var(--muted); font-size:14px; margin-top:28px;}}
code{{font-family:"SF Mono",Menlo,Consolas,monospace; font-size:.9em; background:var(--accent-soft); padding:1px 5px; border-radius:4px;}}
a{{color:var(--accent);}}
@media (prefers-reduced-motion: no-preference){{ html{{scroll-behavior:smooth;}} }}
</style>
<div class="wrap">
  <div class="eyebrow">Manuscript draft · Nature Medicine target · built {date} from <code>{commit}</code>{' (uncommitted edits present)' if dirty else ''}</div>
  <h1>Multimodal integration of metagenomic and clinical data for pathogen identification in lower respiratory tract infection</h1>
  <p class="sub">AETIA (Agentic Evidence Tracing of Infectious Aetiology). Modality-specific language-model agents, a deterministic scorer with pre-specified guardrails, PubMed case-fit evidence and a frozen final rule, evaluated on patients from KMUH, TVGH and TSGH. Numbers that still come from a slide rather than an evaluation file are marked in red.</p>
  <div class="actions">
    <a class="btn primary" href="main.pdf" target="_blank" rel="noopener">Manuscript PDF</a>
    <a class="btn" href="supplementary.pdf" target="_blank" rel="noopener">Supplementary PDF</a>
    <a class="btn" href="{REPO}" target="_blank" rel="noopener">LaTeX sources on GitHub</a>
  </div>
  <div class="grid">
    <div class="stat"><div class="k">Main text</div><div class="v">{n_main} pp</div><div class="n">line-numbered, 4 figures, Table 1, Extended Data Fig. 1</div></div>
    <div class="stat"><div class="k">Supplementary</div><div class="v">{n_supp} pp</div><div class="n">5 tables, 6 notes</div></div>
    <div class="stat"><div class="k">Unverified marks</div><div class="v">{todo}</div><div class="n">red <code>\\todo</code> items to resolve</div></div>
    <div class="stat"><div class="k">References</div><div class="v">{refs}</div><div class="n">resolved through Crossref</div></div>
  </div>

  <div class="tabs" role="tablist" aria-label="Document">
    <button id="tab-main" role="tab" aria-selected="true" aria-controls="reader-main">Main text ({n_main} pages)</button>
    <button id="tab-supp" role="tab" aria-selected="false" aria-controls="reader-supp">Supplementary ({n_supp} pages)</button>
  </div>
  <div id="reader-main" class="reader" role="tabpanel" aria-labelledby="tab-main">{page_imgs("main", n_main, "Main text")}</div>
  <div id="reader-supp" class="reader" role="tabpanel" aria-labelledby="tab-supp" hidden>{page_imgs("supp", n_supp, "Supplementary")}</div>

  <h2>Open before submission</h2>
  <div class="flags">
    <div class="flag"><span class="tag">Data</span><p>All performance numbers are transcribed from the 2026-09-15 student deck and the 2026-01-17 talk. The frozen evaluation outputs (55-case R5 metrics, 41-case direct-prompting reports, gold version) are needed to replace them.</p></div>
    <div class="flag"><span class="tag">Conflict</span><p>Slide 3 lists the pipeline's precision on the 41 patients as 71.62%; the recorded tally TP 69 / FP 33 / FN 7 gives 67.65%, and the slide's own recall and F1 match only the latter. The draft uses 67.65%.</p></div>
    <div class="flag"><span class="tag">Cohorts</span><p>Confirm that slide 2 is the 55-case delivery cohort, how the 35-patient ICU series relates to it, and the two-hospital 54 → 48 → 25 inclusion steps (Extended Data Fig. 1). Table 1 currently describes the 105-specimen registry.</p></div>
    <div class="flag"><span class="tag">People</span><p>IRB approvals and consent statements, the OpenAI data-processing terms, Author contributions / Competing interests / Acknowledgements, case-level presentation approval for the two vignettes (author list settled 2026-09-20).</p></div>
  </div>

  <h2>Figures</h2>
  {fig_html}
  <p class="meta">Page images are rendered at {DPI} dpi for reading here; the PDF buttons open the exact compiled files. Links keep the same addresses across rebuilds. Figures are generated by scripts in <code>figures-source/</code>; the cohort workbook stays outside the repository and only aggregates enter Table 1.</p>
</div>
<script>
(function(){{
  var tabs=[["tab-main","reader-main"],["tab-supp","reader-supp"]];
  tabs.forEach(function(t){{
    document.getElementById(t[0]).addEventListener("click",function(){{
      tabs.forEach(function(u){{
        var sel=u[0]===t[0];
        document.getElementById(u[0]).setAttribute("aria-selected",sel?"true":"false");
        document.getElementById(u[1]).hidden=!sel;
      }});
      try{{localStorage.setItem("aetia-hub-tab",t[0]);}}catch(e){{}}
    }});
  }});
  try{{var saved=localStorage.getItem("aetia-hub-tab"); if(saved==="tab-supp"){{document.getElementById("tab-supp").click();}}}}catch(e){{}}
}})();
</script>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")

    files: dict[str, str | None] = {"main.pdf": "main.pdf", "supplementary.pdf": "supplementary.pdf"}
    for short, _ in figs:
        files[f"figures/{short}.png"] = f"figures/{short}.png"
    removals: dict[str, None] = {}
    for prefix, n in (("main", n_main), ("supp", n_supp)):
        for i in range(1, MAX_PAGES + 1):
            if i <= n:
                files[f"pages/{prefix}-{i:02d}.jpg"] = f"pages/{prefix}-{i:02d}.jpg"
            else:
                removals[f"pages/{prefix}-{i:02d}.jpg"] = None
    # files.json: everything to publish now. files_with_removals.json: the same plus nulls that delete
    # page images left over from a longer earlier build (use it only after listing the artifact's files).
    (OUT / "files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
    (OUT / "files_with_removals.json").write_text(json.dumps({**files, **removals}, indent=1), encoding="utf-8")
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"hub-build ready: main {n_main} pp, supp {n_supp} pp, todo {todo}, refs {refs}, commit {commit}{' (dirty)' if dirty else ''}; {total/1e6:.1f} MB")
    # Compact publish list for the Artifact tool's `files` parameter (plain list = publish each file at its own path).
    print("files:", json.dumps(sorted(files), separators=(",", ":")))


if __name__ == "__main__":
    sys.exit(main())
