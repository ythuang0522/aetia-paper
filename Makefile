# Multimodal pathogen-selection manuscript (AETIA). Build: `make`; figures/tables regenerate from source.
COHORT_XLSX ?= ../三院-final-mNGS merged file.xlsx
PY ?= python3

FIGS = figures/fig1_overview.pdf figures/fig2_benchmark.pdf figures/fig3_llm_comparison.pdf
SUPPFIGS = figures/supp/figS1_cohort_flow.pdf

all: main.pdf Supplementary.pdf

main.pdf: main.tex sections/*.tex references.bib $(FIGS) tables/table1_cohort.tex
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

Supplementary.pdf: Supplementary.tex references.bib $(SUPPFIGS)
	latexmk -pdf -interaction=nonstopmode -halt-on-error Supplementary.tex

figures: $(FIGS) $(SUPPFIGS)

figures/fig1_overview.svg: figures-source/make_fig1.py figures-source/svgkit.py
	$(PY) figures-source/make_fig1.py

figures/fig2_benchmark.svg: figures-source/make_fig2.py figures-source/svgkit.py figures-source/metrics.csv
	$(PY) figures-source/make_fig2.py

figures/fig3_llm_comparison.svg: figures-source/make_fig3.py figures-source/svgkit.py figures-source/metrics.csv
	$(PY) figures-source/make_fig3.py

figures/supp/figS1_cohort_flow.svg: figures-source/make_figS1.py figures-source/svgkit.py
	$(PY) figures-source/make_figS1.py

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
