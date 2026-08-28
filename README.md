# ProofLayer

Control coverage screening engine and analysis artefact for the paper:

> **ProofLayer: Control Coverage Screening for Government Cybersecurity Policies
> via Multi-LLM Orchestration**
> Devharsh Trivedi, Bowie State University.
> Journal of Cybersecurity, Digital Forensics and Jurisprudence, accepted 2026.

## A correction to an earlier version of this repository

An earlier version of this README reported a mean coverage of 49.1 percent and
listed systemic gaps of 9 of 10 and 8 of 10 documents, using control identifiers
of the form AC-02 and SC-02.

**All of those figures were computed on the first fifteen pages of each
document.** The extraction routine was called with `max_pages=15`. Seven of the
ten corpus documents are longer than fifteen pages; the Maryland IT Security
Manual is 219 pages, so its score rested on roughly seven percent of its text.
Reading the documents in full changes the corpus mean from 49.1 to 62.8 percent
and shrinks every gap count. The remediation ranking that earlier version
offered is withdrawn.

The old identifiers are also gone. Sixteen of twenty-two collided with NIST
SP 800-53 labels that mean something else: ProofLayer's "AC-04" mapped to NIST
IA-2, "PS-01" to AT-2, "CP-01" to CP-9. Internal identifiers are now `PL-01`
through `PL-22`, and the crosswalk to NIST, FedRAMP, CMMC 2.0 and SOC 2 is
published as data rather than implied by the numbering.

`results/truncation_effect.csv` gives the per-document comparison. Re-running
the matcher under the fifteen-page cap reproduces 49.1 percent exactly, which is
what identified the cause.

## What this study measured, and what it did not

**Measured.** A keyword-based mapping of ten Maryland state and local government
cybersecurity policy documents against 22 controls crosswalked to 13 NIST
SP 800-53 Revision 5 families. Reading each document in full gives a mean
coverage of **62.8 percent** (standard deviation 24.1). The most frequently
absent controls are access control policy (PL-01), incident reporting (PL-11)
and encryption at rest (PL-15), each missing from seven of ten documents, and
account management (PL-02) and audit review (PL-09), each missing from six.

**Measured, and unflattering to the metric.** Coverage correlates with document
length at r = 0.690 against log word count, so 48 percent of its variance across
the corpus is explained by length alone. The Procurement Manual, 25,289 words
and almost entirely off-topic, scores the same as a 1,423-word network security
policy. Of 138 covered document-control pairs, 18.1 percent carry a negation cue
within 130 characters of the match, and 44.2 percent rest on a single matched
keyword out of a mean 6.1 available. `results/error_analysis.md` works through
four cases, including a footnote URL scored as transport encryption and an
incident-reporting requirement with a two-business-day deadline scored as absent
because the keyword list lacked the word "notifying".

**Described, not evaluated.** The Stage 2 language-model gap analysis in
`code/llm.py`. It is implemented and specified, but it has **not** been compared
against expert annotation, so its output carries no measured accuracy. No
expert-annotated ground truth exists for this corpus. Generating labels with a
language model and scoring the model against them would be circular, and the
author's companion paper documents that exact failure mode, so it was not done.

**Projected, not measured.** The cost-aware routing saving of roughly 24 percent
is arithmetic over published vendor list prices, not observed spend. No run was
instrumented to record token usage.

Keyword presence is a proxy for policy vocabulary, not for compliance. A keyword
can appear in a context that does not satisfy the control, including a negated
one, and a policy can satisfy a control without using the dictionary's terms.
Read the results as indicators of where to look, not as findings about whether
an agency is compliant.

## Layout

```
code/run_coverage.py    Stage 1 matcher; regenerates every result file
code/make_figures.py    regenerates every figure from results/
code/analysis.ipynb     superseded, see the note below
data/control_crosswalk  22 controls: PL ids, NIST r5, FedRAMP, CMMC 2.0, SOC 2
data/corpus_manifest    the ten documents with SHA-256 hashes
results/                220 document-control pairs, per-document and per-control
                        summaries, the truncation comparison, error analysis
figures/                figures as they appear in the paper, PDF and PNG
paper/                  manuscript source, bibliography, compiled PDF
```

`code/analysis.ipynb` is the original notebook and still contains the
`max_pages=15` call. It is retained for provenance, so that the truncation can
be inspected rather than taken on trust. **It does not reproduce the published
figures.** Use `code/run_coverage.py`.

## Reproducing the analysis

The corpus is **not** redistributed here. All ten documents are published by
Maryland state agencies and are publicly available; `data/corpus_manifest.csv`
lists each filename with its size and SHA-256 so you can verify you hold the
same bytes.

1. Collect the ten documents listed in the manifest into a directory.
2. Point `POLICY_DIR` in `code/run_coverage.py` at it.
3. `python3 code/run_coverage.py` then `python3 code/make_figures.py`.

Requires `pdfplumber`, `numpy` and `matplotlib`. No API key: the evaluated
Stage 1 result is pure keyword matching. Stage 2 and the routing layer do
require credentials, and are not needed to reproduce anything the paper claims
as a result.

## Licensing

- Code: MIT, see `LICENSE`.
- Manifest, crosswalk and results: CC BY 4.0, see `LICENSE-DATA`.
- The Maryland policy documents are works of state government and are
  distributed by their issuing agencies, not by this repository.

## Citation

See `CITATION.cff`. Please cite the paper rather than this repository.
