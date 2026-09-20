# Source ledger

Every claim in the manuscript traces to one of the sources below. Status: `slide-only` (number
exists only on a slide), `code-verified` (traced to the repository), `needs eval JSON` (must be
recomputed from the frozen evaluation outputs, which are not in this folder). Decks and the
workbook stay in `../` and are never copied into this repository.

## Decks

### `../0914 專題匯報.pdf` — student progress report, 2026-09-15 (Canva export, 6 slides)

| Slide | Content | Used in | Status |
|---|---|---|---|
| 1 | Title; presenters 吳昱承, 張鈞婷, 鐘元廷 (PDF author metadata: 葉元婷) | author block (`\todo`) | — |
| 2 | "最終指標結果": Multimodal Diagnosis P 71.6 / R 91.4 / F1 80.3; mNGS 8.0 / 93.1 / 14.8; FilmArray/GM 67.6 / 39.7 / 50.0; Culture 48.1 / 43.1 / 45.5 | abstract, intro, Results §2, Fig. 2a, `figures-source/metrics.csv` (r5_55) | slide-only → needs eval JSON. Cohort assumed = 55-case R5 delivery (docs/VALIDATION.md); baseline definitions (what counts as an mNGS/FilmArray/culture "prediction") not in the public code |
| 3 | "模型比較": 上游+AETIA R5 R 90.79 / P 71.62 / F1 77.53; GPT Sol 57.89 / 67.69 / 62.41; Luna 57.89 / 69.84 / 63.31; Terra 56.58 / 70.49 / 62.77; Astra 60.53 / 67.65 / 63.89 | Results §4, Fig. 3, `metrics.csv` (direct_raw_41) | slide-only → needs eval JSON. **Discrepancy:** docs/VALIDATION.md gives AETIA on the 41 = TP 69 / FP 33 / FN 7 → P 67.65, R 90.79, F1 77.53. Recall and F1 match the slide; precision does not (71.62 = the 55-case value). Draft uses 67.65 with `\todo` |
| 4 | "最終輸出": simple version (hospital, patient ID, selected pathogens, reasons) and reasoning version (patient data → candidates → consider/exclude reasons → case & literature evidence → source check → final ranking) | Fig. 1d, Methods "Rationale generation and delivery" | code-verified (`OBER_patient_delivery/export_delivery.mjs`, `docs/WORKFLOW.md` §4) |
| 5 | Exhibition questions (poster content; interactive demo) | — | not used |
| 6 | Thanks | — | — |

### `../20260117_Asia Mirobiome_YTH.pdf` — Y.-T. Huang, Asia Microbiome talk, 2026-01-17 (2 slides, pp. 14–15)

| Slide | Content | Used in | Status |
|---|---|---|---|
| 14 | "Multi-Agent Infectious Diagnosis": X-ray/CT/MRI, blood counts, inflammatory markers, GM test, PCR/FilmArray, patient history, mNGS → Image / CBC / IM / GM / PCR / Patient / NGS agents → clinical-contextualized diagnosis agent ↔ PubMed reflection → clinical-contextualized reasoning; collaboration KMUH, TVGH, TSGH | Fig. 1a framing; intro | concept slide; agent names mapped to the actual prompts in `upstream/agents/prompts/` (Image, CBC/Lab/underlying, FilmArray+GM, molecular, culture, mNGS-to-specimen) |
| 15 | ICU patients n = 35: positive rate Culture 24.2 % (avg 3.16 species), FilmArray 63.6 % (3.00), mNGS 100 % (5.76), Agentic Dx 100 % (1.97); case vignettes: patient #23 *K. pneumoniae* (CT bilateral consolidations + pleural effusions; CRP peak; hypoxaemia; 68,569 reads) vs *C. albicans* commensal; patient #20 *C. tropicalis* (multiple positive blood cultures; high BALF reads; cross-specimen support). Credit: Dr. Chang, KMUH | Fig. 2b,c (`figures-source/burden.csv`), Results §3 and §6, Supplementary Note 3 | slide-only; earlier prototype ("Agentic Dx"); relation to the 55/41 cohorts unconfirmed; vignettes must be regenerated from AETIA R5 outputs and approved for publication |

## Workbook

`../三院-final-mNGS merged file.xlsx` (2025-06-29) — three-hospital registry, 105 specimens
(KMUH 51, VGHTPE 35, TS 19). Sheets: 基本資料 (demographics, comorbidities, ARDS, pneumonia type,
P/F ratio), 微生物診斷資料 (cultures, non-culture tests, therapy change, mNGS influence,
**clinical pathogen diagnosis 1–8 = reference labels**, ventilation, discharge status), mNGS (report
organisms 1–10 per specimen), summary sheets. **Contains PHI** (date of birth, hospital IDs,
specimen IDs) → read only by `tables/make_table1.py` via `COHORT_XLSX`; only aggregates leave it.
Used in: Table 1, Results §2 (cohort description), Methods "Study design".
Cross-check: the script reproduces the workbook's own 圖表們 summary (age 69, male 64.8 %, DM 27.62 %,
CKD 15.24 %, malignancy 37.14 %, CAP 21, Abx change 65.71 %, survival 51.43 %) except
corticosteroids (38.5 % vs 5.71 %: mixed 是/有 encodings) and mNGS influence (denominator).

## Code repository — `../Multimodal-Diagnosis-Model` (state of 2026-09-20)

| Fact | Where | Used in |
|---|---|---|
| Stage chain, orchestrator contract | `README.md`, `docs/WORKFLOW.md`, `docs/FULL_PIPELINE.md`, `run_full_pipeline.py::build_plan` | Fig. 1, Results §1, Methods |
| Cohort counts: master K53/T19/V35 = 107; KH 33 (297 sections); two-hospital 48 (480), 6 empty grouped; R5 delivery 55 = KH 30 + 25 (20 rich/moderate + 5 full root); Direct-Raw 41 = 30 + 11 | `docs/FRONTEND.md`, `docs/COHORT_VALIDATION.json` | Fig. S1, Methods "Study design" |
| 55 R5 decisions replay byte-identical; 114 picked + 9 rescued = 123 selected; 518 candidates; 62 A1 artifacts, 15 with fallback; Direct-Raw 164 predictions rescored identical; AETIA on the 41: TP 69 / FP 33 / FN 7 | `docs/VALIDATION.md` | Results §5, §7; Fig. S1; metrics.csv |
| Reported runs used scorer v19; v20 replay: picked set equal 55/55, candidate levels differ in 15, pick order in 5 | `docs/UPSTREAM_REPLAY_SUMMARY.json`, `docs/VERSIONS.md`, `docs/UPSTREAM_RECOVERY.md` | Results §7, Methods "Deterministic scoring", Supp. Note 4 |
| Tests: 319 Python + 8 Node offline; 382 source / 470 package manifest hashes | `README.md` §測試, `docs/VALIDATION.md` | Results §7, Methods "Reproducibility" |
| Modality agents and prompts; default model gpt-5 | `upstream/tools/analyze_llm_agent.py:27`, `upstream/agents/prompts/` | Methods, Supp. Table 5 |
| Ranking: priority 1–5 from NTC/RK codes, code scores, log-read percentile, 0.6/0.4 weights, labels 0.70/0.45 | `upstream/tools/rank_mngs_candidate_microbes.py:14-33,105-155` | Methods, Supp. Table 1 |
| Read tiers R0–R4, dominance D0–D3 | `upstream/tools/mngs_common.py:303-314`; `deterministic_mngs_max_scorer.py:1539-1562` | Methods, Supp. Table 1 |
| M1–M4 clauses; level mapping; picking; 33 `R-S4-*` guardrail identifiers; protected list | `deterministic_mngs_max_scorer.py:1565-1850, 2784-2925`; `mngs_common.py:33-60` | Methods, Supp. Tables 2–3 |
| Host context V/O tiers → host expansion | `deterministic_mngs_max_scorer.py:761-781` | Methods |
| Review tiers and prompt; model gpt-5 | `upstream/tools/review_missed_mngs_candidates.py:22,274-360` | Methods, Supp. Note 1 |
| PubMed query, 10 articles, cutoff 2026-06-30; article judge gpt-5.6-luna low 1200; module A ≥3 of ≥5 | `RAG_re/rag_re/pubmed.py:40-46`, `RAG_re/config/default.json`, `RAG_re/rag_re/rules.py:136-218`, `RAG_re/prompts/article_support_v1.txt` | Methods, Supp. Table 4 |
| A1 verdict rule; traceability gate; model gpt-5.6-luna low 1400; prompt excludes gold/picked/reads/culture/PCR/review | `RAG_re_casefit/rag_re_casefit/rules.py:40-120`, `config/default.json`, `docs/WORKFLOW.md` §3 | Methods |
| B axes, C grades, D states, temporal ±3 d, clinical_v1 exploratory | `RAG_re_clinical/rag_re_clinical/clinical_rules.py:805-1095`, `config/clinical_v1.json` | Methods, Supp. Table 4 |
| R5 formula and rule id | `OBER_patient_delivery/generate_r5_final_decisions.py:17-21,98-116` | Fig. 1d, Methods |
| Evidence window default 2 days (date mode); rationale model gpt-5.6-luna low | `examples/full_pipeline_config.template.json:36-37`, `generate_llm_rationales.py:96-97` | Methods |
| Direct-Raw: sections, DROP_KEYS, prompt_v1, reasoning medium, 4000 tokens, models, 22/19 per-model rerun split, 123 + 41 responses | `LLM_test/direct_raw_benchmark/{direct_raw_runner.py, prompt_v1.txt, astra_batch.py:17,59, compare_identity_reruns.py:120}` | Methods, Supp. Note 2 |
| Evaluation: (patient, organism) pairs, FROZEN_SYNONYMS, no genus relaxation, micro metrics, answer-positive cohort caveat | `evaluate_direct_raw.py:12-27,75-115,120-135` | Methods "Evaluation", Discussion |
| External name AETIA; no LICENSE; repo private | `docs/OBER_NAMING.md`, `LICENSE_STATUS.md` | macros, Code availability |

## Not found (needed before submission)

- Evaluation JSON / per-patient tables for the 55-case run and the 41-case comparison (`reports/idfixed_20260906`, `reports/astra_20260906`, the 55-case metrics) — gitignored `**/reports/`.
- Gold files and the cohort manifests (`**/gold/`, `cohort_manifest.json`).
- The script that scored the three conventional baselines on slide 2.
- Sequencing laboratory, platform and wet-lab protocol; study period; IRB approvals.
- The formatter and vision model identifiers used for the historical front-end runs.

## How to fold in a new deck

1. Read it (pptx via the `pptx` skill; pdf via the Read tool). 2. Add one row per slide above.
3. If it carries numbers, add them to `figures-source/metrics.csv` (or a new CSV) with `source` and
`verified=no`, then regenerate (`make figures`). 4. Update the text and the README ledger.
