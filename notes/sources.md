# Source ledger

Every claim in the manuscript traces to one of the sources below. Status: `slide-only` (number
exists only on a slide), `code-verified` (traced to the repository), `needs eval JSON` (must be
recomputed from the frozen evaluation outputs, which are not in this folder). Decks and the
workbook stay in `../` and are never copied into this repository.

## Decks

### `../0914 專題匯報.pdf` — student progress report, 2026-09-15 (Canva export, 6 slides)

| Slide | Content | Used in | Status |
|---|---|---|---|
| 1 | Title; presenters 吳昱承, 張鈞婷, 鐘元廷 (PDF author metadata: 葉元婷) | author block: Chun-Ting Chang, Yuan-Ting Chung, Yu-Cheng Wu (CCU), after the three clinicians; 葉元婷 is not an author (professor, 2026-09-20) | settled |
| 2 | "最終指標結果": Multimodal Diagnosis P 71.6 / R 91.4 / F1 80.3; mNGS 8.0 / 93.1 / 14.8; FilmArray/GM 67.6 / 39.7 / 50.0; Culture 48.1 / 43.1 / 45.5 | abstract, Results §2, Fig. 2a, `figures-source/metrics.csv` (r5_55) | slide-only → needs eval JSON. Cohort assumed = 55-case R5 delivery (docs/VALIDATION.md); baseline definitions (what counts as an mNGS/FilmArray/culture "prediction") not in the public code |
| 3 | "模型比較": 上游+AETIA R5 R 90.79 / P 71.62 / F1 77.53; GPT Sol 57.89 / 67.69 / 62.41; Luna 57.89 / 69.84 / 63.31; Terra 56.58 / 70.49 / 62.77; Astra 60.53 / 67.65 / 63.89 | Results §3, Fig. 3, `metrics.csv` (direct_raw_41) | slide-only → needs eval JSON. **Discrepancy:** docs/VALIDATION.md gives AETIA on the 41 = TP 69 / FP 33 / FN 7 → P 67.65, R 90.79, F1 77.53. Recall and F1 match the slide; precision does not (71.62 = the 55-case value). Draft uses 67.65 with `\todo` |
| 4 | "最終輸出": simple version (hospital, patient ID, selected pathogens, reasons) and reasoning version (patient data → candidates → consider/exclude reasons → case & literature evidence → source check → final ranking) | Fig. 1d, Methods "Rationale generation and delivery" | code-verified (`OBER_patient_delivery/export_delivery.mjs`, `docs/WORKFLOW.md` §4) |
| 5 | Exhibition questions (poster content; interactive demo) | — | not used |
| 6 | Thanks | — | — |

### `../20260117_Asia Mirobiome_YTH.pdf` — Y.-T. Huang, Asia Microbiome talk, 2026-01-17 (2 slides, pp. 14–15)

| Slide | Content | Used in | Status |
|---|---|---|---|
| 14 | "Multi-Agent Infectious Diagnosis": X-ray/CT/MRI, blood counts, inflammatory markers, GM test, PCR/FilmArray, patient history, mNGS → Image / CBC / IM / GM / PCR / Patient / NGS agents → clinical-contextualized diagnosis agent ↔ PubMed reflection → clinical-contextualized reasoning; collaboration KMUH, TVGH, TSGH | Fig. 1a framing; intro | concept slide; agent names mapped to the actual prompts in `upstream/agents/prompts/` (Image, CBC/Lab/underlying, FilmArray+GM, molecular, culture, mNGS-to-specimen) |
| 15 | ICU patients n = 35: positive rate Culture 24.2 % (avg 3.16 species), FilmArray 63.6 % (3.00), mNGS 100 % (5.76), Agentic Dx 100 % (1.97); case vignettes: patient #23 *K. pneumoniae* (CT bilateral consolidations + pleural effusions; CRP peak; hypoxaemia; 68,569 reads) vs *C. albicans* commensal; patient #20 *C. tropicalis* (multiple positive blood cultures; high BALF reads; cross-specimen support). Credit: Dr. Chang, KMUH | Fig. 2c,d (`figures-source/burden.csv`), Results §§2 and 4, Fig. 4e,f (`figures-source/make_fig_explain.py`), Fig. 1d worked entry (`make_fig_overview.py`, qualitative labels only, no read count), Supplementary Note 3 | slide-only; earlier prototype ("Agentic Dx"); relation to the 55/41 cohorts unconfirmed; vignettes must be regenerated from AETIA R5 outputs and approved for publication. The evidence items shown on the cards (rule path, module values, per-modality support and opposition, article identifiers, input hashes) are code-verified fields of the delivered record (`OBER_patient_delivery/export_delivery.mjs`, `generate_r5_final_decisions.py`), not slide content |

## KMUH per-patient record (Fig. 4a; Results §4; Methods)

`tables/make_kmuh_record.py` reads the per-patient source workbooks in `../KMUH patients` (PHI, folder
in `KMUH_DIR`) plus the registry `mNGS` sheet and writes `figures-source/kmuh_record.csv` (one row per
aggregate: metric, median, IQR, n, unit). Status: **code-verified** — every number in Fig. 4a is
recomputed from those workbooks. Linkage: `NGS patient N` ↔ registry `K{N:03d}`; the mNGS specimen date
falls inside the recorded admission in 33 of 35 datable cases (K016 12 days after the recorded
discharge, K020 a month before the recorded admission — both look like a second admission that the
admission sheet does not carry). Analysis set 32 of 36 workbooks: patient 7 has no microbiology,
imaging or panel data; patient 11 is annotated `同 patient 9`; patients 26 and 27 are byte-identical to
25. In each duplicate group the registry holds a *separate* mNGS specimen for the same admission
(K009/K011, K025/K026/K027), i.e. the admission was sequenced two or three times; counted once.
Fig. 4a-c are drawn from two long-format files written by the same script: `kmuh_admissions.csv` (one row per admission: results by modality, organisms split by how many read-outs named them, record span, word count; ordered by organism count so the row order carries no patient identity) and `kmuh_latency.csv` (one row per culture report: outcome and hours to the final report). Headline aggregates: 247 results per admission (IQR 214–263), 31-day record, new result on 16 days,
1,452 words of free text; 8 organisms per admission (IQR 6–11), 270 organism–admission pairs, 81 %
named by one read-out (mNGS alone 48 %, culture alone 23 %, panel/GM alone 11 %), 91 % with no
sterile-site culture; 254 culture reports, 72 % positive, no-growth reported at a median 147 h against
75 h for growth; 365 chest studies, 90 % naming pneumonia/infiltrate/consolidation, 44 % of those
hedged; a resistance marker without an organism in 34 % of admissions. Caveats: culture positivity does
**not** fall with hospital day (62 % days 0–2, 81 % days 3–7, 73 % from day 8), so the "cultures go
negative once antimicrobials start" argument is **not** supported by this cohort and must not be
written as if it were; mortality flags (16/30 coded N/N), length of stay (14 discharge dates) and the
admission-versus-discharge diagnosis shift (81 % by a keyword rule) were computed but are **not** used.

## Registry analysis (Fig. 4a; Introduction; Supplementary Note 6)

`tables/make_discordance.py` reads the workbook below and writes `figures-source/discordance.csv`
(one de-identified row per mNGS detection: specimen class, organism, reads, adjudicated status,
conventional support) and `figures-source/discordance_summary.json` (the aggregates quoted in the
Results §5, Supplementary Note 6 and Discussion). Status: **code-verified** — every
number is recomputed from the workbook by that script, none comes from a slide. Scope: the 33 registry
cases whose adjudicated pathogen list is in the shared workbook (the KMUH line keeps its adjudication in
the per-patient workbooks, so 1 of 51 KMUH cases appears here); read counts from the `Read count` sheet
cover 80 of 104 detections. Adjudication cells that record no pathogen (`不明`, `not infection case`,
`no pathogen`) are excluded; names are normalized with the same synonym table as the evaluation, plus
workbook-specific fixes (`candida albican`, `ecoli`, `hsv`, `aspergillosis` → `aspergillus`,
`non-tuberculosis mycobacterium`). Re-run after any label consolidation: `make figures-source/discordance.csv`.
Added 2026-09-21: `figures-source/missed_by_mngs.csv` (one row per read-out class × specimen that found
an adjudicated pathogen absent from the sequenced specimen's report; `day_offsets` = collection day minus
the mNGS arrival day, parsed from the `YYYY/M/D` strings of the `mNGS` sheet) and the summary keys
`absent_by_first_readout`, `absent_found_within_2_days`, `absent_found_nearest_day_max`,
`absent_found_different_specimen`. Serology aliases (`chlamydophila pneumoniae igm`, `legionella ab`)
were added, which moved one pathogen from "found by no test" to "found by serology" (15 → 16 of 17).
Read-out class is inferred from the result string (IgM/IgG/Ab → serology; galactomannan/Ag → antigen;
culture sheet → culture; otherwise PCR, which covers multiplex panels, viral loads and targeted assays).

Added 2026-09-21 (second pass, folded Fig. 4a): `figures-source/sampling.csv`, one aggregate row per
read-out lane (mNGS / culture / targeted) over all 105 registry specimens — number of dated tests,
share of patients in which the lane named any organism, median and IQR (and 5th–95th centile) of the
collection day relative to the mNGS specimen, share collected within two days of it, and median/IQR
turnaround — plus the summary key `sampling` (median 7 d, IQR 3–15, from admission to the mNGS
specimen; 1 mNGS specimen per patient) and the percentage keys `detections_both_ways_pct` (47),
`absent_found_different_specimen_pct` (69), `absent_found_within_2_days_pct` (88). Status:
**code-verified**. Two limits of the source, both stated in Methods and in the figure: a conventional
test enters the registry only when it detected an organism (225 of 226 dated culture rows are
positive), so the culture and targeted lanes show when the evidence that named an organism was
produced, not the full test load — culture yield and the effect of antimicrobial exposure on it are
**not** computable here and are handled in the Discussion with citations (PI's decision, 2026-09-21);
and the `mNGS` sheet's arrival and report dates are equal in 54 of 105 rows, so no sequencing
turnaround is quoted from them. Collection intervals beyond ±90 days are dropped as date-entry errors.

Pipeline facts used in Results §4 / Methods for organisms the report lacks (code-verified, not run on
the registry cases): hospital-evidence candidates —
`Multimodal-Diagnosis-Model/upstream/tools/deterministic_mngs_max_scorer.py` (`direct_hospital_support_modules`:845,
`hospital_only_candidate_from_evidence`:977, `hospital_only_candidates`:1106; same in
`deterministic_mngs_max_scorer_v19_recovered.py`), direct modules = culture (pulmonary-relevant rows only,
`module_has_pulmonary_relevant_evidence`:1200), filmarray_gmtest, molecular_microbiology; level ≤ 2, or
level 3 for *Aspergillus*; Candida/yeast blocked without invasive evidence
(`R-S4-CANDIDA-HOSPITAL-NONINVASIVE-NOT-PICKED`). IgM-serology rule —
`upstream/rules/review_context_rescue_rules.json` (`atypical_respiratory_indirect_serology`),
`upstream/tools/candidate_evidence_profile.py` (`atypical_respiratory_serology_profile`:78), applied in
`review_missed_mngs_candidates.py`:1557 and `merge_deterministic_max_with_missed_review.py`:1970
(target and maximum tier `review_context_needed`). The number of hospital-evidence selections among
the 123 is not in the docs → `\todo` in Results §4.

## Registry treatment impact, organism burden and concordance (Results §§5–6; Discussion; added 2026-09-21)

`tables/make_impact.py` reads the same workbook and writes `figures-source/impact.csv` (one row per
aggregate: group, metric, n, denominator, value, unit) and `figures-source/impact_summary.json`.
It imports `norm`, `q`, `sheet_rows`, `NON_PATHOGEN` and `STERILE` from `make_discordance.py` so the two
analyses cannot drift apart. Status: **code-verified** — every number is recomputed from the workbook.
Re-run with `make figures-source/impact.csv`. Five analyses, only the last of which needs adjudication:

| Analysis | Scope | Headline numbers | Used in |
|---|---|---|---|
| Treatment impact (`微生物診斷資料` cols 146–148, 157, 160) | all 105 | therapy changed 69 (65.7%); attributed to mNGS 52 (49.5%, = 58.4% of the 89 with attribution recorded); of those 36 escalation / 13 de-escalation / 3 inconclusive; 13 of 19 de-escalations attributed; ventilated ≤3 d 81/98 (82.7%); in-hospital death 51 (48.6%) | Results §6 ¶1, Discussion ¶1 |
| Null result: does list length predict action? | all 105 | organisms per report median 4 whether or not the change was attributed to mNGS; death 57.7% vs 56.8% | Results §6 ¶1–2 |
| Organism burden by specimen, with the within-BALF control | all 105 | airway (BALF+sputum, n=67) median 5 (IQR 3–7) vs sterile-site (n=38) median 1 (1–2); ICU 5 vs ward 1, steroid 5 vs 3, ARDS 5 vs 3 **across all specimens**, but **within BALF alone** ICU 5 vs 5, steroid 5.5 vs 5, ARDS 5 vs 5 — only HAP/VAP 5 vs CAP 3 survives | Results §5 ¶1, Discussion ¶3 |
| Culture concordance | all 105 | 75 of 414 reported organisms (18.1%) had a same-species culture in the admission; 90 of 165 cultured organisms (54.5%) absent from the report. Cross-check against the workbook's own `Lab vs.mNGS` tally (312 comparisons): NGS+/Cx− 49.0%, partial 29.8%, mismatch 6.7%, exact match 5.8%, NGS−/Cx+ 2.9% | Results §5 ¶2. The workbook does not define "partial match"/"mismatch", so the text quotes the category names without interpreting them |
| Class composition | all 105 | reported 55.6% bacteria / 27.1% viruses / 15.9% fungi / 1.4% mycobacteria vs adjudicated 52.7 / 21.8 / 23.6 / 1.8; 100 of 112 reported viruses (89.3%) are herpesviruses | Results §5 ¶2 |
| Cases with no adjudicated pathogen | 22 of 105 | 6 explicit negatives (TSGH: `不明`, `無`, `not infection case`, `no pathogen`) + 16 rows whose only adjudication cell is `-` (all TVGH); mNGS reported ≥1 organism in 18 of the 22, 47 organisms in all, median 1, max 8 | Results §5 ¶5, Discussion limitations |

Outcome analysis added 2026-09-21 (second pass, at the PI's request) to the same script, with Fisher's
exact test and a Newton-Raphson logistic model written in `make_impact.py` itself (`fisher_or`,
`logistic_or`) because this machine has no scipy/statsmodels. Result, in `impact_summary.json` under
`outcome_attributed`: in-hospital death 30/52 (57.7%) where the team credited the treatment change to
mNGS against 21/37 (56.8%) where it did not, OR 1.04 (0.45-2.41), Fisher p = 1.00; adjusted OR 1.22
(0.46-3.21), p = 0.69 over 89 patients and 51 deaths. The exposure is balanced at baseline (ARDS 51.9 vs
54.1, malignancy 40.4 vs 40.5, steroids 40.4 vs 48.6) and the one imbalance (ICU 71.2 vs 91.9) runs
against the exposed group, which is what makes the null interpretable. **Reported as a null, not as
evidence of absent benefit.** The parallel test on "any treatment change" (OR 3.04, 1.31-7.07, p = 0.013)
is kept in `outcome_changed_confounded` and is **not** reported as a finding: the changed group has more
ARDS (56.5 vs 25.0) and more corticosteroid use (44.9 vs 25.0) before the change, so it measures the
indication. Duration endpoints (length of stay, ventilation) were computed during exploration and are
deliberately **not** in the script or the paper -- a change attributed to a specimen taken a median of
7 days into the admission can only be recorded in survivors, so they are immortal-time biased. Methods
subsection "Registry treatment and outcome analysis" states all of this; Discussion names both biases
without repeating numbers (PI's section-discipline ruling).

**Open question (the one `\todo` this analysis adds):** whether TVGH's `-` means "no causative pathogen
identified" or "not recorded". All 16 are from one hospital, 12 of 16 had no therapy change and their
treatment/outcome columns are filled in, which points to the former — but the no-infection stratum cannot
be scored until the investigators confirm it. `make_impact.py` keeps the two groups separate
(`explicit negative` vs `dash only`) so the answer changes one constant, not the analysis.

Plotted as **Extended Data Fig. 2** by `figures-source/make_figED2.py`, which reads `impact_summary.json`
and types no number of its own: **a**, dumbbells of the median organisms per report for the compartment
contrast (orange) and for each patient stratum over all specimens (grey) and within bronchoalveolar lavage
(blue), which is the visual form of the control described above; **b**, the 312-comparison stack, the two
corroboration rates, and the reported-against-adjudicated class composition. Added on the PI's instruction
of 2026-09-21, which supersedes the earlier "Extended Data: cohort flow only" ruling.

Turnaround is **not** recomputed here: the mNGS/culture/targeted lanes already exist in
`figures-source/sampling.csv` (mNGS reported a median of 0 days after receipt, IQR 0–2; culture 3 d,
IQR 2–5). The Results no longer interpret these dates as time from specimen collection. Data-quality note surfaced by this pass and recorded as
`microbiology_rows_without_a_registry_specimen` in the JSON: `微生物診斷資料` has 110 rows against 105
registry specimens — 5 carry a case code absent from the `mNGS` sheet, and they are excluded from every
aggregate above. Resolve with the investigators.

## KMUH whole-record extracts — physiological trajectory (Results; Discussion; Extended Data Fig. 3; added 2026-09-21)

New source: `../phenotype for KMUH/` (PHI, outside the repo; path in `PHENOTYPE_DIR`). Delivered by KMUH
2026-09-21. One workbook per admission for 49 of the 51 KMUH registry admissions (`patient N` ↔ registry
`K{N:03d}`; 7, 14 and 16 absent), produced by **GX10 MedicalPhenotype V2.7**, a local pipeline
(Ollama; Llama4 Scout extracts evidence, GPT-OSS 120B adjudicates, Llama4 Scout re-reviews) that converts
the full admission PDF into 8 sheets: `Phenotypes_Wide/_Long`, `Review_Only`, `Microbiology`,
`Clinical_Timeline`, `Lab_Results`, `Evidence`, `Clinical_Facts`. Plus 98 CSVs (`*_clinical_facts.csv`,
`*_microbiology.csv`) and `MedicalPhenotype_V2_7_...docx` documenting the 22 phenotypes.

**Used in the manuscript: the `Lab_Results` sheet only.** `tables/make_trajectory.py` anchors every dated
value to the mNGS specimen day from the registry and writes `figures-source/trajectory.csv` (one row per
marker × window × outcome group) and `trajectory_summary.json`. Status: **code-verified**. Re-run with
`make figures-source/trajectory.csv`. Analysis set 48 admissions (31 deaths, 17 survivors).

| Finding | Numbers | Used in |
|---|---|---|
| Therapeutic window | death a median of 15 d after the specimen (IQR 7–21, range 1–57); 22/31 >7 d, 17/31 >14 d | Results §7 ¶2, Discussion |
| Defervescence is universal | all 10 decedents and all 5 survivors febrile pre-specimen were afebrile at d3–7; decedents ≥38 °C 39%→18%→3% across pre/d0–2/d3–7; paired −0.5 °C, n=27, P=0.001 | Results §7 ¶2 |
| Oxygenation improves then reverses | pO2 up by d3–7 in 17/27 decedents; 12 of those 17 fell again; fever returned in 9 of the 21 whose temperature improved | Results §7 ¶2 |
| Platelets move the other way | survivors 169→257→360, decedents 82→48→55 (×10³/µL); paired −19, n=14, P=0.004; improved in only 2/14 | Results §7 ¶3 |
| Plotted as | **Extended Data Fig. 3** (`figures-source/make_figED3.py`, reads `trajectory_summary.json`, types no number): **a** one row per admission, grouped by outcome, ordered by length of admission — a temperature-state matrix over the five windows beside a bar of the days of admission that followed the specimen; **b** the same temperatures as the proportion reaching 38 °C, n at every point; **c** per-decedent improvement classification (held / reversed / never) for temperature, pO2 and platelets |
|---|---|---|
| Stage chain, orchestrator contract | `README.md`, `docs/WORKFLOW.md`, `docs/FULL_PIPELINE.md`, `run_full_pipeline.py::build_plan` | Fig. 1, Results §1, Methods |
| Cohort counts: master K53/T19/V35 = 107; KH 33 (297 sections); two-hospital 48 (480), 6 empty grouped; R5 delivery 55 = KH 30 + 25 (20 rich/moderate + 5 full root); Direct-Raw 41 = 30 + 11 | `docs/FRONTEND.md`, `docs/COHORT_VALIDATION.json` | Extended Data Fig. 1, Methods "Study design" |
| 55 R5 decisions replay byte-identical; 114 picked + 9 rescued = 123 selected; 518 candidates; 62 A1 artifacts, 15 with fallback; Direct-Raw 164 predictions rescored identical; AETIA on the 41: TP 69 / FP 33 / FN 7 | `docs/VALIDATION.md` | Results §§3–4; Extended Data Fig. 1; metrics.csv |
| Reported runs used scorer v19; v20 replay: picked set equal 55/55, candidate levels differ in 15, pick order in 5 | `docs/UPSTREAM_REPLAY_SUMMARY.json`, `docs/VERSIONS.md`, `docs/UPSTREAM_RECOVERY.md` | Methods "Deterministic scoring", Supp. Note 4 |
| Tests: 319 Python + 8 Node offline; 382 source / 470 package manifest hashes | `README.md` §測試, `docs/VALIDATION.md` | Methods "Reproducibility" |
| Modality agents and prompts; default model gpt-5 | `upstream/tools/analyze_llm_agent.py:27`, `upstream/agents/prompts/` | Methods, Supp. Table 5 |
| Ranking: priority 1–5 from NTC/RK codes, code scores, log-read percentile, 0.6/0.4 weights, labels 0.70/0.45 | `upstream/tools/rank_mngs_candidate_microbes.py:14-33,105-155` | Methods, Supp. Table 1 |
| Read tiers R0–R4, dominance D0–D3 | `upstream/tools/mngs_common.py:303-314`; `deterministic_mngs_max_scorer.py:1539-1562` | Methods, Supp. Table 1 |
| M1–M4 clauses; level mapping; picking; 33 `R-S4-*` guardrail identifiers; protected list | `deterministic_mngs_max_scorer.py:1565-1850, 2784-2925`; `mngs_common.py:33-60` | Methods, Supp. Tables 2–3 |
| Host context V/O tiers → host expansion | `deterministic_mngs_max_scorer.py:761-781` | Methods |
| Review tiers and prompt; model gpt-5 | `upstream/tools/review_missed_mngs_candidates.py:22,274-360` | Methods, Supp. Note 1 |
| PubMed query, 10 articles, cutoff 2026-06-30; article judge gpt-5.6-luna low 1200; module A ≥3 of ≥5 | `RAG_re/rag_re/pubmed.py:40-46`, `RAG_re/config/default.json`, `RAG_re/rag_re/rules.py:136-218`, `RAG_re/prompts/article_support_v1.txt` | Fig. 1c, Methods, Supp. Table 4 |
| A1 verdict rule; traceability gate; model gpt-5.6-luna low 1400; prompt excludes gold/picked/reads/culture/PCR/review | `RAG_re_casefit/rag_re_casefit/rules.py:40-120`, `config/default.json`, `docs/WORKFLOW.md` §3 | Fig. 1c, Methods |
| B axes, C grades, D states, temporal ±3 d, clinical_v1 exploratory | `RAG_re_clinical/rag_re_clinical/clinical_rules.py:805-1095`, `config/clinical_v1.json`; B/C/D are pure functions evaluated at R5 time (`evaluate_modules`, `clinical_rules.py:1295-1338`, `contract.pure = True`), in parallel with A1, not as sequential filters | Fig. 1c, Methods, Supp. Table 4 |
| R5 formula and rule id | `OBER_patient_delivery/generate_r5_final_decisions.py:17-21,98-116` | Fig. 1d, Methods |
| Evidence window default 2 days (date mode); rationale model gpt-5.6-luna low | `examples/full_pipeline_config.template.json:36-37`, `generate_llm_rationales.py:96-97` | Methods |
| Direct-Raw: sections, DROP_KEYS, prompt_v1, reasoning medium, 4000 tokens, models, 22/19 per-model rerun split, 123 + 41 responses | `LLM_test/direct_raw_benchmark/{direct_raw_runner.py, prompt_v1.txt, astra_batch.py:17,59, compare_identity_reruns.py:120}` | Methods, Supp. Note 2 |
| Evaluation: (patient, organism) pairs, FROZEN_SYNONYMS, no genus relaxation, micro metrics, answer-positive cohort caveat | `evaluate_direct_raw.py:12-27,75-115,120-135` | Methods "Evaluation", Discussion |
| External name AETIA; no LICENSE; repo private | `docs/OBER_NAMING.md`, `LICENSE_STATUS.md` | macros, Code availability |

## Cohort flow figure and the exclusion criterion (2026-09-21)

**Extended Data Fig. 1 rebuilt** (`figures-source/make_figED1.py`). The previous version drew two parallel
hospital lines (KMUH / TVGH+TSGH) with provenance prose inside the boxes ("297 / 297 sections identical",
`IDs kmuh_case_code`, `IDs legacy_global`). The PI's point, 2026-09-21: multicentre diagnostic-accuracy
studies pool their flow. Rebuilt as a single STARD spine — registry 105 → standardized record 81 →
delivery cohort 55 → direct-prompting 41 — with the per-hospital contribution annotated at every node and
exclusions branching right with n and reason (24 / 26 / 14). The two lines differ only in where their
adjudication is stored and how records were assembled, which is provenance and now lives in Methods text.
The 35-patient ICU series is drawn detached, because it is not part of this flow.

**Undocumented exclusion, surfaced by the PI the same day.** The real criterion excluded patients whose
ultimate diagnosis was infection at another site (e.g. UTI) or no infection. The Methods had said only
"at least one adjudicated causative pathogen". This is a selection on the outcome: it defines a population
that cannot be identified when the test is ordered, it removes the cases where the site and colonization
guardrails matter most (the correct output there is an empty pulmonary list), and it is the direct cause
of the precision caveat already in the Discussion. Methods and Discussion now state it explicitly, and the
figure footnote carries it. Open (`\todo` in Methods): how many were excluded on this ground, the site of
infection in each, and whether the filter was applied to the registry or to the delivered set.

Supporting observation from the workbook: the registry is **not** a pneumonia registry. It holds 6 CSF,
5 tissue, 1 ascites, 1 pus and 1 abscess specimens; the departments include neurology and haematology;
and 25 of 105 specimens carry no pneumonia category. The Methods sentence describing all participants as
having "suspected lower respiratory tract infection" does not match the registry contents and should be
reconciled with the clinical team.

**The better design, if the team agrees:** keep these patients and score them with "no pulmonary pathogen"
as a correct answer, reporting specificity on that stratum. The 22 specimens with no adjudicated pathogen
(registry impact section above) are part of the same missing stratum.

## Published descriptions of the sequencing laboratory and hospital assays (added 2026-09-20)

| Source | Facts used | Used in |
|---|---|---|
| Chou et al., *Biomedicines* 2025, 10.3390/biomedicines13010142 (KMUH BALF mNGS by Asia Pathogenomics) | 65 °C 30 min inactivation; bead beating; TIANMicrobe Pathogen DNA Kit; QIAamp Viral RNA Mini Kit; ~100 ng input; MGIEasy FS DNA / RNA kits, 12/14 cycles; DNBSEQ-G50RS SE50; ~40 M reads per library; FilmArray Pneumonia Panel copies/mL reported at KMUH | Methods "Metagenomic sequencing" |
| Takahashi et al., *Front Cell Infect Microbiol* 2026, 10.3389/fcimb.2026.1823299, Supplementary Methods (Asia Pathogenomics, Osaka cases) | AVITI 1×75; Trimmomatic v0.39 + PRINSEQ v0.20.4 (≥70 bp, Q20, duplicates, complexity); BWA-MEM v0.7.17 to T2T-CHM13 v2.0; database 5,884 viral / 18,432 bacterial / 3,146 fungal / 370 parasitic genomes; TPM ≥10× highest negative control; fastidious taxa ≥1 unique read absent from controls; Shannon-entropy uniformity; extraction, library and NTC controls | Methods "Metagenomic sequencing" |
| Hung et al., *Front Pharmacol* 2021, 10.3389/fphar.2021.747280 (KMUH ICU) | Platelia *Aspergillus* GM-EIA in serum and BAL at KMUH | Methods (conventional microbiology) |
| `upstream/agents/prompts/filmarray_GMtest_prompt.txt` | Panels recognised (Pneumonia Panel, RP2.1, BCID2); semiquant bins 10^4–≥10^7 → levels 4–1; GM cut-offs BAL ≥1.0 / 0.5–0.99 / serum ≥0.5 | Methods (conventional microbiology) |

**Decisions (2026-09-20):** platform stated as AVITI 1×75 (Takahashi 2026 Supp. Methods) per the professor; extraction from Chou 2025 (Taiwan laboratory). The laboratory's internal control codes (NTC/RK, `rank_mngs_candidate_microbes.py:22-28`) are never named in the manuscript — the report is described as the organisms the laboratory outputs with read counts and a control-subtracted rank. **Open:** whether RNA libraries were run for every specimen; TVGH/TSGH assay confirmation.

## Author names and affiliations (Europe PMC, 2026-09-20)

| Author | Source record | Affiliations used |
|---|---|---|
| 張維安 → Wei-An Chang | Chou et al., *Biomedicines* 2025, 10.3390/biomedicines13010142 | Div. Pulmonary and Critical Care Medicine, Dept Internal Medicine, KMUH/KMU; Dept Internal Medicine, School of Medicine, College of Medicine, KMU; Graduate Institute of Clinical Medicine, College of Medicine, KMU |
| 沈志浩 → Chih-Hao Shen | Wang et al., *BMC Infect Dis* 2026, 10.1186/s12879-026-13877-4; Wu et al., *J Infect Public Health* 2025, 10.1016/j.jiph.2025.102767 | Div. Pulmonary and Critical Care Medicine, Dept Internal Medicine, Tri-Service General Hospital, National Defense Medical University |
| 馮嘉毅 → Jia-Yih Feng | Chen et al., *Pulmonology* 2026, 10.1080/25310429.2026.2704386; *BMC Infect Dis* 2026 (above) | Dept Chest Medicine, TVGH; School of Medicine and Institute of Emergency and Critical Care Medicine, National Yang Ming Chiao Tung University |

## Student flowchart (肺部 mNGS 致病菌判讀流程, 2026-09-20) vs code

| Chart element | Code | Outcome |
|---|---|---|
| Guardrails + Merge after the LLM review | `merge_deterministic_max_with_missed_review.py` main:2206-2217 — sanitize/canonicalize, weak-environmental omission, triage, non-pulmonary-support guardrail, syndrome-pattern convergence, tier convergence v2, atypical-serology rescue, group representatives; never promotes | Adopted (Methods, Supp. Table 5; the Fig. 1b post-review box was dropped in the 2026-09-21 concept-only redesign). Chart's Picked→Guardrails arrow is wrong: R-S4 guardrails run inside the scorer before picking |
| Five agents | `analyze_llm_agent.py:59-103`; LLM mNGS-to-specimen is an alternative branch; specimen alignment by keyword (`deterministic_mngs_max_scorer.py:718`) | Flagged `\todo`; confirm branch used for the 55 |
| 中央 taxonomy classifier, routing only | `organism_taxonomy_classifier.py:163` (`routing_only: True`), v20 only; v19→v20 also changed the M1/M2 clause (`docs/UPSTREAM_RECOVERY.md:30-32`) | Adopted in Methods + Supp. Note 4; no figure box |
| Luna LLM review | `DEFAULT_MODEL = "gpt-5"`, template config gpt-5/medium; policy id `v11_luna_rescue_cleanup` | Flagged `\todo` |
| Imaging = context only | image prompt forbids Against; scorer `module_support["image"] = "Not_available"` (:1884); summary D-SUM-01 pools organism_hints for display | Adopted as one sentence |
| Deterministic hospital summary | reported runs summary v3 (recovered), current v4; 52/55 scorer-identical on rebuild (`UPSTREAM_RECOVERY.md:65`) | Adopted |
| Ranking (not on chart, found while checking) | two scripts, different formulas (0.6/0.4 across-file vs 0.7/0.3 within-specimen) | Flagged `\todo`; read `score_formula` in frozen ranked JSON |

## Not found (needed before submission)

- Evaluation JSON / per-patient tables for the 55-case run and the 41-case comparison (`reports/idfixed_20260906`, `reports/astra_20260906`, the 55-case metrics) — gitignored `**/reports/`.
- Gold files and the cohort manifests (`**/gold/`, `cohort_manifest.json`).
- The script that scored the three conventional baselines on slide 2.
- Study period; IRB approvals. (Sequencing workflow now sourced from the laboratory's publications, above.)
- The formatter and vision model identifiers used for the historical front-end runs.

## How to fold in a new deck

1. Read it (pptx via the `pptx` skill; pdf via the Read tool). 2. Add one row per slide above.
3. If it carries numbers, add them to `figures-source/metrics.csv` (or a new CSV) with `source` and
`verified=no`, then regenerate (`make figures`). 4. Update the text and the README ledger.
