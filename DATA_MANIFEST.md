# ProofLayer supplementary data

Accompanies the CDFJ article. Everything reported in the manuscript can be
recomputed from these files, which are published in this repository rather than
as a supplementary archive.

## Contents

    data/control_crosswalk.json     22 controls: PL ids, the legacy id each
    data/control_crosswalk.csv      replaces, NIST SP 800-53 r5, FedRAMP,
                                    CMMC 2.0, SOC 2, risk band, keyword lists

    results/coverage_by_pair.csv    220 document-control pairs: covered flag,
                                    which keywords matched, how many of the
                                    available keywords, a count of negation
                                    cues near the hit, and two text snippets
    results/coverage_by_document.csv   10 documents: pages, words, coverage
    results/coverage_by_control.csv    22 controls: documents covered
    results/truncation_effect.csv      first-15-pages vs full text, per document
    results/measurement_diagnostics.json  the correlation, negation and
                                    single-keyword figures quoted in Section 5.3
    results/error_analysis.md       the four worked error cases, with sources

    code/run_coverage.py            regenerates every results/ file from the
                                    policy corpus
    code/make_figures.py            regenerates every figure from results/

## Reproducing

Requires Python 3.10+, `pdfplumber`, `matplotlib`, `numpy`.

    python3 code/run_coverage.py     # rebuilds results/
    python3 code/make_figures.py     # rebuilds figures/

`run_coverage.py` expects the ten Maryland policy PDFs named in `POLICY_FILES`.
They are public documents published by Maryland state agencies; we do not
redistribute them here, and the filenames in the script identify each one.

## Two things this package does not contain

**Expert annotations.** There is no ground-truth labelling of document-control
pairs, so no precision, recall, F1 or inter-rater agreement is computed
anywhere in the manuscript. Reviewers asked for this and we could not supply
it. We did not substitute model-generated labels.

**Measured token cost.** The orchestration cost figure in the manuscript is a
projection over published vendor rates, not instrumented spend, and is labelled
as such throughout.
