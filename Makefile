# Multimodal pathogen-selection manuscript (AETIA). Build: `make`; figures/tables regenerate from source.
COHORT_XLSX ?= ../三院-final-mNGS merged file.xlsx
PY ?= python3

FIGS = figures/fig1_overview.pdf figures/fig2_benchmark.pdf figures/fig3_llm_comparison.pdf figures/fig4_explanation.pdf figures/ed1_cohort_flow.pdf figures/ed2_registry.pdf figures/ed3_trajectory.pdf

all: main.pdf Supplementary.pdf

main.pdf: main.tex sections/*.tex references.bib $(FIGS) tables/table1_cohort.tex
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

Supplementary.pdf: Supplementary.tex references.bib
	latexmk -pdf -interaction=nonstopmode -halt-on-error Supplementary.tex

figures: $(FIGS)

# Registry discordance analysis for Fig. 1: reads the cohort workbook (PHI, outside this repo);
# only de-identified per-detection rows and aggregate counts are written into figures-source/.
figures-source/discordance.csv: tables/make_discordance.py
	COHORT_XLSX="$(COHORT_XLSX)" $(PY) tables/make_discordance.py

# Registry treatment-impact, organism-burden and concordance aggregates (Results, Discussion).
# Same handling: the workbook stays outside the repository, only aggregates are written out.
figures-source/impact.csv: tables/make_impact.py tables/make_discordance.py
	COHORT_XLSX="$(COHORT_XLSX)" $(PY) tables/make_impact.py

# Physiological trajectory around the mNGS specimen. Reads the registry workbook and the KMUH
# whole-record extracts (both PHI, outside this repository); writes only aggregates.
PHENOTYPE_DIR ?= ../phenotype for KMUH
figures-source/trajectory.csv: tables/make_trajectory.py
	COHORT_XLSX="$(COHORT_XLSX)" PHENOTYPE_DIR="$(PHENOTYPE_DIR)" $(PY) tables/make_trajectory.py

figures/fig1_overview.svg: figures-source/make_fig_overview.py figures-source/svgkit.py figures-source/icons.py
	$(PY) figures-source/make_fig_overview.py

figures/fig2_benchmark.svg: figures-source/make_fig_benchmark.py figures-source/svgkit.py figures-source/metrics.csv figures-source/burden.csv
	$(PY) figures-source/make_fig_benchmark.py

figures/fig3_llm_comparison.svg: figures-source/make_fig_llm.py figures-source/svgkit.py figures-source/metrics.csv
	$(PY) figures-source/make_fig_llm.py

figures/ed1_cohort_flow.svg: figures-source/make_figED1.py figures-source/svgkit.py
	$(PY) figures-source/make_figED1.py

# Extended Data Fig. 2 plots figures-source/impact_summary.json; no number is typed in the script.
figures/ed2_registry.svg: figures-source/make_figED2.py figures-source/svgkit.py figures-source/impact_summary.json
	$(PY) figures-source/make_figED2.py

# Extended Data Fig. 3 plots figures-source/trajectory_summary.json; no number is typed in the script.
figures/ed3_trajectory.svg: figures-source/make_figED3.py figures-source/svgkit.py figures-source/trajectory_summary.json
	$(PY) figures-source/make_figED3.py

figures/fig4_explanation.svg: figures-source/make_fig_explain.py figures-source/svgkit.py
	$(PY) figures-source/make_fig_explain.py

figures/%.pdf: figures/%.svg
	rsvg-convert -f pdf -o $@ $<

# Table 1 is computed from the cohort workbook, which stays OUTSIDE this repository (PHI).
# Only counts and percentages are written to tables/table1_cohort.tex.
tables/table1_cohort.tex: tables/make_table1.py
	COHORT_XLSX="$(COHORT_XLSX)" $(PY) tables/make_table1.py

wordcount:
	@texcount -1 -sum sections/introduction.tex sections/results.tex sections/discussion.tex
	@echo "todo marks:" && grep -o '\\todo{' main.tex sections/*.tex Supplementary.tex | sort | uniq -c

clean:
	latexmk -C
	latexmk -C Supplementary.tex
	rm -f *.bbl *.blg *.run.xml

.PHONY: all figures wordcount clean
