# ProofLayer

Compliance auditing engine and analysis artefact for the paper:

> **ProofLayer: Automated Cybersecurity Compliance Auditing for State Government
> Policies via Multi-LLM Orchestration**
> Devharsh Trivedi, Bowie State University

## What this study measured, and what it did not

This distinction matters for reading both the paper and this code, so it is stated
up front.

**Evaluated.** A keyword-based mapping of ten Maryland state and local government
cybersecurity policy documents against 22 controls drawn from 13 NIST SP 800-53
Rev 5 families. Mean coverage is 49.1 percent, with nine of ten documents rated
high or medium risk. Systemic gaps: account management (AC-02, absent in 9 of 10),
encryption at rest (SC-02, 9 of 10), access control policy (AC-01, 8 of 10), and
incident reporting (IR-02, 8 of 10).

**Described, not evaluated.** The Stage 2 LLM gap-analysis module in
`code/llm.py`. It is implemented and specified, but it has **not** been compared
against expert annotation, so its output carries no measured accuracy. Section 6
of the paper sets out the annotation protocol that would settle this: 10 documents
by 22 controls is 220 document-control judgments, ternary labels, at least one
annotator independent of the authors, labels fixed before the model output is
inspected.

**Projected, not measured.** The cost-aware routing saving of roughly 24 percent
is arithmetic over published vendor list prices, not an observed saving. See the
note in the cost cell of `code/analysis.ipynb`, which documents the 4,000-token
`gpt-4o` baseline used for the long-document step.

Keyword presence is a proxy for control coverage, not compliance verification. A
keyword can appear in a context that does not satisfy the control, and a policy
can satisfy a control without using the dictionary's terminology. Read the results
as indicators of likely gaps.

## Layout

```
code/     analysis notebook, control dataset, backend, frontend
data/     corpus manifest with SHA-256 hashes, control dataset as CSV
figures/  figures as they appear in the paper, PDF and PNG
paper/    manuscript source, bibliography, compiled PDF
```

## Reproducing the analysis

The corpus is **not** redistributed here. All ten documents are published by
Maryland state agencies and are publicly available; `data/corpus_manifest.csv`
lists each filename with its size and SHA-256 so you can verify you have the same
bytes we did.

1. Collect the ten documents listed in the manifest into a directory.
2. Point `POLICY_DIR` in `code/analysis.ipynb` at it.
3. Run the notebook. It requires `pdfplumber`, `numpy`, `pandas` and
   `matplotlib`, and needs no API key: the evaluated Stage 1 result is pure
   keyword matching.

Stage 2 and the routing layer do require API credentials. They are not needed to
reproduce anything the paper claims as a result.

## Running the system

```
cd code
pip install -r requirements.txt
# set OPENAI_API_KEY, and optionally ANTHROPIC_API_KEY, in backend/.env
```

`start.bat` writes a template `.env`. The key strings in it are placeholders; no
credentials are committed to this repository.

## Licensing

- Code: MIT, see `LICENSE`.
- Manifest and control dataset: CC BY 4.0, see `LICENSE-DATA`.
- The Maryland policy documents themselves are works of state government and are
  distributed by their issuing agencies, not by this repository.

## Citation

See `CITATION.cff`.
