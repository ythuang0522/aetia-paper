"""Generate the claude.ai hub page for the compiled manuscript.

Usage: python3 notes/hub/build_hub.py MAIN_PDF_URL SUPP_PDF_URL FIG1_URL FIG2_URL FIG3_URL OUT.html [COMMIT] [TODO] [PAGES_MAIN] [PAGES_SUPP] [REFS]
The five URLs are the /_blob/<id> asset URLs returned when main.pdf, Supplementary.pdf and the three figure PNGs
are uploaded to the artifact https://claude.ai/artifact/PB2BPxhvChugJsDavnGsKf (Artifact tool, asset upload).
Refresh procedure: make -> rsvg-convert the three figure SVGs to PNG (-z 1.6) -> upload the 5 files as assets ->
run this script with the new URLs and the current stats -> republish the artifact with the generated HTML.
"""
import sys
from pathlib import Path
argv = sys.argv + [""] * 12
main_pdf, supp_pdf, fig1, fig2, fig3 = argv[1:6]
commit = argv[7] or "3e4462b"; todo = argv[8] or "198"; pages_main = argv[9] or "23"; pages_supp = argv[10] or "9"; refs = argv[11] or "39"
have_assets = bool(main_pdf)

def link(url, label, primary=False):
    cls = "btn primary" if primary else "btn"
    if not url:
        return f'<span class="{cls} disabled" aria-disabled="true">{label} <small>uploading…</small></span>'
    return f'<a class="{cls}" href="{url}" target="_blank" rel="noopener">{label}</a>'

viewer = (f'<div class="viewer"><iframe title="AETIA manuscript PDF" src="{main_pdf}#view=FitH"></iframe></div>'
          if main_pdf else '<div class="viewer placeholder">PDF preview appears here once the file is uploaded.</div>')

def fig(url, n, cap):
    if not url:
        return ""
    return f'<figure><img src="{url}" alt="Figure {n}: {cap}" loading="lazy"><figcaption><b>Fig. {n}</b> {cap}</figcaption></figure>'

figs = fig(fig1, 1, "Overview of AETIA: modality agents, deterministic sieve with guardrails and safety review, evidence modules, R5 gate and auditable delivery.") + \
       fig(fig2, 2, "Precision–recall plane and P/R/F1 against the raw mNGS report, FilmArray/GM and culture (n = 55); organism burden (n = 35).") + \
       fig(fig3, 3, "Precision–recall plane and P/R/F1 against four frontier language models prompted directly on identical data (n = 41).")

html = f"""<title>AETIA Manuscript</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{{
  --bg:#f7f8fb; --surface:#ffffff; --ink:#151a24; --ink-2:#4a5262; --muted:#7a8291; --line:#dfe3ea;
  --accent:#1d4ed8; --accent-ink:#ffffff; --accent-soft:#e6edfb; --flag:#b45309; --flag-soft:#fdf1df;
  color-scheme:light;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --bg:#0f1319; --surface:#171c25; --ink:#eef1f6; --ink-2:#b7bfcc; --muted:#8a93a3; --line:#2a323f;
    --accent:#6f9bff; --accent-ink:#0b1020; --accent-soft:#1a2540; --flag:#f0b35a; --flag-soft:#2c2114;
    color-scheme:dark;
  }}
}}
:root[data-theme="dark"]{{
  --bg:#0f1319; --surface:#171c25; --ink:#eef1f6; --ink-2:#b7bfcc; --muted:#8a93a3; --line:#2a323f;
  --accent:#6f9bff; --accent-ink:#0b1020; --accent-soft:#1a2540; --flag:#f0b35a; --flag-soft:#2c2114;
  color-scheme:dark;
}}
body{{background:var(--bg); color:var(--ink); font-family:"Source Sans 3", "Helvetica Neue", Arial, sans-serif; font-size:16px; line-height:1.5;}}
.wrap{{max-width:1080px; margin:0 auto; padding-block:36px 64px; padding-inline:20px;}}
.eyebrow{{font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600;}}
h1{{font-family:"Source Serif 4", Georgia, "Times New Roman", serif; font-weight:600; font-size:clamp(24px,3.4vw,36px); line-height:1.2; margin:8px 0 10px; text-wrap:balance; max-width:30ch;}}
.sub{{color:var(--ink-2); max-width:70ch; margin:0 0 22px;}}
.actions{{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:28px;}}
.btn{{display:inline-flex; align-items:center; gap:8px; padding:10px 16px; border-radius:8px; border:1px solid var(--line); background:var(--surface); color:var(--ink); text-decoration:none; font-weight:600;}}
.btn:hover{{border-color:var(--accent);}}
.btn:focus-visible{{outline:2px solid var(--accent); outline-offset:2px;}}
.btn.primary{{background:var(--accent); color:var(--accent-ink); border-color:var(--accent);}}
.btn.disabled{{opacity:.6;}}
.btn small{{font-weight:400; color:inherit; opacity:.8;}}
.grid{{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:28px;}}
@media (max-width:720px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}
.stat{{background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:14px 16px;}}
.stat .k{{font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-weight:600;}}
.stat .v{{font-size:26px; font-weight:600; font-variant-numeric:tabular-nums; margin-top:2px;}}
.stat .n{{font-size:13px; color:var(--ink-2);}}
.viewer{{background:var(--surface); border:1px solid var(--line); border-radius:12px; overflow:hidden; aspect-ratio:3/4; max-height:80vh; max-width:100%;}}
.viewer iframe{{width:100%; height:100%; border:0;}}
.viewer.placeholder{{display:flex; align-items:center; justify-content:center; color:var(--muted); aspect-ratio:auto; padding:40px;}}
h2{{font-family:"Source Serif 4", Georgia, serif; font-weight:600; font-size:22px; margin:36px 0 12px;}}
.flags{{display:grid; gap:10px;}}
.flag{{display:grid; grid-template-columns:auto 1fr; gap:12px; align-items:start; background:var(--flag-soft); border-left:3px solid var(--flag); border-radius:8px; padding:12px 14px;}}
.flag .tag{{font-size:12px; font-weight:600; color:var(--flag); text-transform:uppercase; letter-spacing:.08em; padding-top:3px;}}
.flag p{{margin:0; color:var(--ink);}}
figure{{margin:0 0 26px; background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:14px;}}
figure img{{display:block; width:100%; height:auto; border-radius:6px; background:#ffffff;}}
figcaption{{font-size:14px; color:var(--ink-2); margin-top:10px;}}
.meta{{color:var(--muted); font-size:14px; margin-top:28px;}}
code{{font-family:"SF Mono", Menlo, Consolas, monospace; font-size:.9em; background:var(--accent-soft); padding:1px 5px; border-radius:4px;}}
a{{color:var(--accent);}}
</style>
<div class="wrap">
  <div class="eyebrow">Manuscript draft · Nature Medicine target · 2026-09-20</div>
  <h1>Auditable multimodal integration of metagenomic sequencing and clinical evidence identifies causative pathogens in lower respiratory tract infection</h1>
  <p class="sub">AETIA (Agentic Evidence Tracing of Infectious Aetiology). Modality-specific language-model agents, a deterministic scorer with pre-specified guardrails, PubMed case-fit evidence and a frozen final rule, evaluated on patients from KMUH, TVGH and TSGH. Every number that still comes from a slide rather than an evaluation file is marked in red in the PDF.</p>
  <div class="actions">
    {link(main_pdf, "Open the manuscript PDF", primary=True)}
    {link(supp_pdf, "Supplementary PDF")}
    <a class="btn" href="https://github.com/ythuang0522/aetia-paper" target="_blank" rel="noopener">LaTeX sources on GitHub</a>
  </div>
  <div class="grid">
    <div class="stat"><div class="k">Main text</div><div class="v">{pages_main} pp</div><div class="n">line-numbered, 3 figures, Table 1</div></div>
    <div class="stat"><div class="k">Supplementary</div><div class="v">{pages_supp} pp</div><div class="n">1 figure, 5 tables, 5 notes</div></div>
    <div class="stat"><div class="k">Unverified marks</div><div class="v">{todo}</div><div class="n">red <code>\\todo</code> items to resolve</div></div>
    <div class="stat"><div class="k">References</div><div class="v">{refs}</div><div class="n">resolved through Crossref</div></div>
  </div>
  {viewer}
  <h2>Open before submission</h2>
  <div class="flags">
    <div class="flag"><span class="tag">Data</span><p>All performance numbers are transcribed from the 2026-09-15 student deck and the 2026-01-17 talk. The frozen evaluation outputs (55-case R5 metrics, 41-case direct-prompting reports, gold version) are needed to replace them.</p></div>
    <div class="flag"><span class="tag">Conflict</span><p>Slide 3 lists the pipeline's precision on the 41 patients as 71.62%; the recorded tally TP 69 / FP 33 / FN 7 gives 67.65%, and the slide's own recall and F1 match only the latter. The draft uses 67.65%.</p></div>
    <div class="flag"><span class="tag">Cohorts</span><p>Confirm that slide 2 is the 55-case delivery cohort, how the 35-patient ICU series relates to it, and the two-hospital 54 → 48 → 25 inclusion steps. Table 1 currently describes the 105-specimen registry.</p></div>
    <div class="flag"><span class="tag">People</span><p>Author list and order, clinical co-authors per hospital, IRB approvals and consent statements, case-level presentation approval for the two vignettes.</p></div>
  </div>
  <h2>Figures</h2>
  {figs}
  <p class="meta">Built from commit <code>{commit}</code> with <code>make</code> (latexmk, rsvg-convert). Figures are generated by scripts in <code>figures-source/</code>; the cohort workbook stays outside the repository and only aggregates enter Table 1.</p>
</div>
"""
Path(sys.argv[6] if len(sys.argv) > 6 else "hub.html").write_text(html, encoding="utf-8")
print("written", have_assets)
