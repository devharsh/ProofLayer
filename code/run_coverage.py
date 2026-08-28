"""ProofLayer Stage 1: keyword-based control coverage over the Maryland corpus.

Rewritten for the CDFJ revision in response to reviewer comments. Three changes
of substance from the notebook this replaces.

1.  Internal control identifiers are now PL-01..PL-22. The previous scheme used
    labels such as AC-04 and PS-01 that a reader would naturally read as the
    NIST SP 800-53 controls of the same name. They were not. ProofLayer's
    "AC-04" mapped to NIST IA-2, "PS-01" to AT-2 and "CP-01" to CP-9. Sixteen of
    twenty-two identifiers collided in this way. The crosswalk is now explicit
    and released as data rather than implied by the numbering.

2.  The measured quantity is named coverage, not compliance. Keyword presence
    establishes that a document mentions the vocabulary associated with a
    control. It does not establish that the control is implemented, that the
    mention is affirmative rather than negated, or that the document is even in
    scope for that control. Calling it compliance overstates it, and the
    reviewers were right to say so.

3.  Every document-control pair is written out with the matched keyword and a
    surrounding snippet, so a reader can inspect why a pair was scored the way
    it was. The previous version released no per-pair data at all.

    python3 code/run_coverage.py
"""

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POLICY_DIR = os.path.join(ROOT, "..", "Compliance-Auditing-CCSCE", "policies")
DATA = os.path.join(ROOT, "data")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(DATA, exist_ok=True)
os.makedirs(RESULTS, exist_ok=True)

POLICY_FILES = {
    "MD_DOIT_CyberRiskMgmt_Policy.pdf":         "MD Risk Mgmt Policy",
    "MD_DOIT_SystemNetworkSecurity_Policy.pdf": "MD System & Network Security Policy",
    "MD_DOIT_ContinuousMonitoring_Policy.pdf":  "MD Continuous Monitoring Policy",
    "MD_CybersecurityCouncil_Report_2025.pdf":  "MD Cybersecurity Council Report 2025",
    "MD_IT_SecurityManual.pdf":                 "MD IT Security Manual",
    "MD_UMGC_LocalGov_Cybersecurity_2021.pdf":  "MD Local Gov Cybersecurity 2021",
    "MD_DHMH_IT_SecurityPolicy.pdf":            "MD Health Dept IT Security Policy",
    "MD_Judicial_InfoSecurity_Policy.pdf":      "MD Judicial Info Security Policy",
    "MD_MSDE_AUP_2024.pdf":                     "MD MSDE Acceptable Use Policy 2024",
    "MD_Procurement_Manual.pdf":                "MD Procurement Manual",
}

# Negation cues checked in the window around a hit. Reviewer comment: keyword
# presence does not capture negation. We cannot fully solve that with lexical
# matching, but we can at least count how often a hit sits next to a negation,
# which bounds how much of the coverage number is potentially spurious.
NEGATION = [
    "not required", "no requirement", "does not", "shall not", "must not",
    "is not", "are not", "without", "except", "exempt", "n/a",
    "not applicable", "no longer", "prohibited from",
]


def extract(path):
    import pdfplumber
    out = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            t = page.extract_text() or ""
            out.append((i, t))
    return out


def main():
    controls = json.load(open(os.path.join(DATA, "control_crosswalk.json")))
    pair_rows, doc_rows = [], []

    for fn, label in POLICY_FILES.items():
        path = os.path.join(POLICY_DIR, fn)
        if not os.path.exists(path):
            print(f"  MISSING {fn}", file=sys.stderr)
            continue
        pages = extract(path)
        full = "\n".join(t for _, t in pages).lower()
        n_words = len(full.split())
        hits_for_doc = 0

        for c in controls:
            kws = [k.strip().lower() for k in c["keywords"].split(";")]
            matched, snippets, negated = [], [], 0
            for kw in kws:
                for m in re.finditer(re.escape(kw), full):
                    matched.append(kw)
                    lo, hi = max(0, m.start() - 130), min(len(full), m.end() + 130)
                    win = re.sub(r"\s+", " ", full[lo:hi])
                    if any(nz in win for nz in NEGATION):
                        negated += 1
                    if len(snippets) < 3:
                        snippets.append(win)
                    break                      # one hit per keyword is enough
            covered = int(bool(matched))
            hits_for_doc += covered
            pair_rows.append({
                "document": label, "file": fn,
                "proof_layer_id": c["proof_layer_id"],
                "control": c["control"],
                "nist_800_53_r5": c["nist_800_53_r5"],
                "risk": c["risk"],
                "covered": covered,
                "n_keywords_matched": len(set(matched)),
                "n_keywords_total": len(kws),
                "matched_keywords": "; ".join(sorted(set(matched))),
                "hits_near_negation": negated,
                "snippet_1": snippets[0] if snippets else "",
                "snippet_2": snippets[1] if len(snippets) > 1 else "",
            })

        doc_rows.append({
            "document": label, "file": fn, "pages": len(pages), "words": n_words,
            "controls_covered": hits_for_doc, "controls_total": len(controls),
            "coverage_pct": round(100.0 * hits_for_doc / len(controls), 1),
        })
        print(f"  {label:42s} {hits_for_doc:2d}/{len(controls)} controls, "
              f"{len(pages):3d}pp, {n_words:6d} words")

    for name, rows in (("coverage_by_pair.csv", pair_rows),
                       ("coverage_by_document.csv", doc_rows)):
        with open(os.path.join(RESULTS, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(f"wrote results/{name}  ({len(rows)} rows)")

    # per-control frequency across the corpus
    freq = {}
    for r in pair_rows:
        k = (r["proof_layer_id"], r["control"], r["nist_800_53_r5"], r["risk"])
        freq[k] = freq.get(k, 0) + r["covered"]
    with open(os.path.join(RESULTS, "coverage_by_control.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["proof_layer_id", "control", "nist_800_53_r5", "risk",
                    "docs_covered", "docs_total"])
        for (pid, ctl, nist, risk), n in sorted(freq.items()):
            w.writerow([pid, ctl, nist, risk, n, len(doc_rows)])
    print(f"wrote results/coverage_by_control.csv  ({len(freq)} rows)")


if __name__ == "__main__":
    main()
