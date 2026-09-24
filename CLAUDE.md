# CLAUDE.md — AETIA manuscript

Guidance for Claude Code when working in this folder (the paper only; pipeline code is in
`../Multimodal-Diagnosis-Model`, which has its own CLAUDE.md). Target: Nature Medicine Article.

## Layout and build

- `main.tex` (macros: `\toolname`, `\toolexpansion`, `\mngs`, `\filmarray`, `\rfive`, `\vtwenty`,
  model names, hospitals, `\todo{}`), `sections/{introduction,results,discussion,methods}.tex`,
  `Supplementary.tex`, `tables/`, `figures/` + `figures-source/`, `notes/`.
- `make` builds both PDFs; `make figures` regenerates the SVG/PDF figures from the Python scripts;
  `make wordcount` prints word counts and the `\todo` tally per file. Always rebuild after editing
  and check `grep -c undefined main.log Supplementary.log` is 0.
- README "Status" and "Before submission" are the ledger; update the `\todo` counts and the open
  items there whenever they change. `notes/sources.md` records where every fact came from.

## Non-negotiable conventions

- **Update the hub artifact only when the PI asks** (PI's ruling, 2026-09-24; it replaces the
  2026-09-20 "sync after every PDF change" order). After a PDF-changing edit, `make` and check
  `grep -c undefined main.log Supplementary.log` is 0, then stop; do not build or publish the hub
  unprompted. When asked, the sequence is: `python3 notes/hub/build_hub.py` →
  Artifact tool `list` with `scope: files` on `https://claude.ai/artifact/PB2BPxhvChugJsDavnGsKf`
  (required once per session before a republish; if the publish is still refused, the refusal
  returns the live page — merge and publish again) → publish `hub-build/index.html` with that `url`,
  `root: hub-build` and `files` = `hub-build/files.json` plus `null` for any page path that the
  listing shows but the new build no longer has (`hub-build/files_with_removals.json` holds the
  full null list). Report the link and version number. The artifact URL never changes; keep the
  hub's stat boxes and gallery in `build_hub.py` in step with the manuscript (figure count,
  Extended Data). Git commit/push only when the PI asks.

- **`\todo{}` is for critical items only** (PI's ruling, 2026-09-20 evening: "trust me more"). Numbers
  from the student slides and the repository docs are stated plainly; the ledger of their provenance
  is `notes/sources.md`, not red ink. Keep a `\todo` only for a genuine blank that must be filled
  (IRB protocol numbers, study period, consent wording, model used for historical runs, code URL /
  licence / DOI, data-availability route), a data conflict (slide-3 precision 71.62 vs 67.65), a
  placeholder that must not be published as fact (prototype vignettes, invented Discussion
  examples), missing reference-standard details, the undocumented two-hospital exclusions, the
  35-patient series overlap, baseline scoring definitions, and the statistics still to be added.
  Never add "confirm …" notes for things the PI can check on reading; affiliations, romanization
  and cross-check reminders are not todos. Thresholds and settings read from code or config are
  stated plainly (cite the file:line in the `%` comment under the subsection heading).
- **References are never typed from memory.** Add the DOI to `DOIS` in `notes/resolve_refs.py`
  (arXiv-only works go in `MANUAL`), run `python3 notes/resolve_refs.py`, never hand-edit
  `references.bib`.
- **Figures are scripts.** Edit `figures-source/make_fig*.py`, not the SVG; plotted numbers live in
  `figures-source/metrics.csv` / `burden.csv` with a `source` and `verified` column.
- **Supplementary cross-references are hard-coded numbers** (main.tex and Supplementary.tex are
  separate documents). Current map: Extended Data Fig. 1 cohort flow (in main.tex, so `\ref{fig:ed1}` works); Supp. Tables 1 mNGS features,
  2 tiers/levels, 3 guardrails, 4 module thresholds, 5 models/prompts; Supp. Notes 1 review prompt,
  2 direct-prompting prompt, 3 cases, 4 version boundaries, 5 evaluation outputs, 6 registry analysis of the
  sequencing report alone (the former "problem" figure's numbers); Supplementary Methods = sequencing workflow, conventional microbiology,
  evidence modules A/A1/B–D, direct-prompting runs, then the four exploratory registry analyses (all moved out of Methods
  2026-09-24 to hold Methods at ≤3,000 words by texcount; keep it there — add detail to the Supplementary Methods, not the Methods). Re-check after any reordering.
- **Figures (PI's rulings, updated 2026-09-22):** no figure belongs to the Introduction — motivation is text (the
  registry numbers live in the Introduction and Supp. Note 6; `figures-source/retired/make_fig_problem.py`
  is kept only for reference). Main figures are 1 overview, 2 the combined conventional-read-out and
  direct-prompting performance comparison, and 3 explained decisions (the Candida
  colonization-versus-infection pair, promoted from Extended Data;
  redesigned 2026-09-21 after the PI rejected a text-box version: **no prose boxes in figures** — encode as
  glyph matrices, node-link decision routes, bars; text only as labels and legends);
  the explainability result is a headline of the Results, placed right after the accuracy comparisons,
  not an appendix. Extended Data: 1 cohort flow, 2 registry report content and 3 the post-report course (`make_figED3.py`, plotted from `trajectory_summary.json`; PI asked for it 2026-09-21 after choosing figure over table — the result is convergence/divergence over time, which a table cannot carry). 2 and 3 (added 2026-09-21 on the PI's explicit instruction, superseding the "cohort flow only" ruling: the registry subsection's dumbbell/stack panels, `make_figED2.py`, every value read from `impact_summary.json`). **Fig. 1 carries concept labels only** (PI, 2026-09-21):
  no tier codes (V0–V3, O0–O2, R0–R4, D0–D3, M1–M5, C0–C3), no rule counts ("33 rules"), no thresholds, no
  level arithmetic — those live in Methods and Supp. Tables 1–4; every step is marked by the key (violet chip =
  language model, cog = deterministic rule) so the division of labour is the thing a reader remembers. Second ruling the
  same day: **a panel made of labelled boxes is "text based" and fails** — panel c was rebuilt twice until it became an
  evidence matrix (rows = candidates, glyph cells: one dot per article, strength bars, specimen ladder, colonization dot)
  with pictorial column headers; that matrix is also how the final rule's input is shown. Verify against the code before
  drawing a stage (B/C/D are pure functions run in parallel with A1 at R5 time, not sequential filters).
- Methods trace every rule to the code with a `%` comment (`path (function:line)`) under each
  `\subsection*`; text↔code disagreements are flagged inline with `\todo`, never silently rewritten.
- PHI never enters this folder: the cohort workbook and decks stay in `../`; only aggregates leave
  them (`tables/make_table1.py` via `COHORT_XLSX`).

## Methods structure (settled 2026-09-20, Nature Portfolio pattern)

Ethics and study oversight → Study design and participants → Metagenomic sequencing and conventional
microbiology → Reference standard → Data extraction and standardization → Overview of AETIA →
pipeline stages in execution order → Conventional read-out comparators → Direct-prompting comparison
→ Outcome measures and scoring → Computational reproducibility → Statistics and reproducibility →
Reporting summary → Data availability → Code availability. Keep it; add subsections rather than
reordering.

## Lessons learned (2026-09-20 session)

1. **The laboratory's internal control codes are never named in the manuscript.** The professor's
   ruling: the NTC/RK/00/8 codes in `rank_mngs_candidate_microbes.py` are meaningless to readers.
   Describe the mNGS input everywhere (main text, captions, Supplementary tables and prompt
   renderings, Fig. 1 labels) as "the organisms the laboratory reports, with read counts and a
   control-subtracted rank". Do not reintroduce the codes, even in Supplementary Table 1 or in
   a translated prompt. Grep before building: `grep -n "NTC\|\bRK\b\|control code" main.tex sections/*.tex Supplementary.tex figures-source/*.py`.
2. **Wet-lab and bioinformatics come from the sequencing laboratory's own publications, not from
   the code.** The laboratory is Asia Pathogenomics (professor-confirmed). Sources: Chou et al.
   2025 (Biomedicines; KMUH; extraction) and Takahashi et al. 2026 (Front Cell Infect Microbiol;
   library prep, AVITI 1×75, QC, T2T-CHM13, database sizes, reporting thresholds — all in its
   Supplementary Methods, fetched via Europe PMC `supplementaryFiles`). **State the platform as
   AVITI** (professor's decision), not DNBSEQ. Conventional assays: cite KMUH-authored papers for
   the assays in use there (Platelia GM: Hung 2021; FilmArray Pneumonia Panel: Chou 2025 +
   Buchan 2020) and state the pipeline's own interpretation thresholds from
   `upstream/agents/prompts/filmarray_GMtest_prompt.txt`.
3. When the professor says "improve to Nature standard", restructure to the Nature Portfolio Methods
   pattern above and add the sections Nature requires (Ethics first; Statistics and reproducibility
   with sample size / randomization / blinding / exclusions / single-run disclosure; Reporting
   summary; Data and Code availability with request route, licence and Zenodo DOI). Consolidate
   repeated `\todo`s (e.g. one "confirm model identifiers against run manifests" in the Overview
   instead of one per mention).
4. Code-verified facts to state without `\todo`: formatter (`gpt-5`, temperature 1, hard-coded) and agents use `gpt-5`;
   the safety review uses `gpt-5` at reasoning medium (config template) — the Methods once said Luna for both formatter and review, which was wrong; article judge, case-fit and rationale use `gpt-5.6-luna` at reasoning effort low;
   direct prompting uses reasoning effort medium, 4,000 output tokens; PubMed cutoff 2026-06-30;
   evidence window 2 days (template default — keep its `\todo` until the run manifest is seen).
5. Fig. 2 burden panels are **c,d** (a,b are the precision–recall plane and bars); the Methods once
   said b,c. Check panel letters against the caption when editing.
6. Europe PMC REST (`/search`, `/{PMCID}/fullTextXML`, `/{PMCID}/supplementaryFiles`) is the reliable
   way to read papers and supplements here; publisher HTML often returns 403 to WebFetch.
7. **Another Claude session may be editing this folder at the same time** (the hub/PDF-publishing
   session committed and then edited every section on 2026-09-20 evening, removing most numeric
   `\todo` marks). Before any edit: re-read the current file, match exact current strings, never
   restore an older copy, and re-run `make wordcount` rather than trusting remembered counts.
8. **Student flowcharts are worth checking against the code** — the 2026-09-20 chart exposed a real
   stage the Methods had understated (deterministic post-review rules in
   `merge_deterministic_max_with_missed_review.py`) and three unresolved text↔code discrepancies
   (agent count / specimen alignment branch, ranking formula, review model). Adopt what the code
   confirms; flag the rest with `\todo` naming file:line on both sides; do not adopt chart elements
   the code contradicts (Picked→Guardrails ordering). Heredocs that write Markdown with backticks
   must be quoted (`<<'PY'`) or the shell eats the code spans.
