"""Figures for the CDFJ revision, regenerated from full-document text.

The figures in the submitted version were produced from `results` computed on
the first fifteen pages of each document. Seven of ten documents are longer
than that, so those figures showed a truncation artifact. These are rebuilt
from results/coverage_by_*.csv, which read the documents in full.

Figure 2 additionally plots the truncated and full scores side by side, because
the difference is itself a finding worth showing rather than silently fixing.

    python3 code/make_figures.py
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

LOW, MED = 80, 55


def band(v):
    return "#2e7d32" if v >= LOW else ("#ef6c00" if v >= MED else "#c62828")


def short(name):
    return (name.replace("MD ", "")
                .replace(" Policy", "").replace(" Report", "")
                .replace("Cybersecurity", "Cyber"))


def fig_scores():
    rows = list(csv.DictReader(open(os.path.join(RES, "truncation_effect.csv"))))
    rows.sort(key=lambda r: -int(r["coverage_full"]))
    y = np.arange(len(rows))
    full = [int(r["coverage_full"]) for r in rows]
    trunc = [int(r["coverage_first15pp"]) for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(y + 0.19, full, 0.38, color=[band(v) for v in full],
            label="full document")
    ax.barh(y - 0.19, trunc, 0.38, color="#9e9e9e", label="first 15 pages")
    for i, (f, t) in enumerate(zip(full, trunc)):
        ax.text(f + 1, i + 0.19, f"{f}%", va="center", fontsize=8)
        ax.text(t + 1, i - 0.19, f"{t}%", va="center", fontsize=8, color="#555")
    ax.set_yticks(y, [short(r["document"]) for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Control coverage (% of 22 ProofLayer controls with a keyword match)")
    ax.axvline(LOW, ls="--", lw=0.8, c="#2e7d32")
    ax.axvline(MED, ls="--", lw=0.8, c="#ef6c00")
    ax.set_xlim(0, 104)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.set_title("Coverage is sensitive to how much of the document is read", fontsize=10)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"fig2_coverage_scores.{ext}"), dpi=200)
    plt.close(fig)
    print("  fig2_coverage_scores")


def fig_heatmap():
    pairs = list(csv.DictReader(open(os.path.join(RES, "coverage_by_pair.csv"))))
    docs, ctrls = [], []
    for p in pairs:
        if p["document"] not in docs: docs.append(p["document"])
        if p["proof_layer_id"] not in ctrls: ctrls.append(p["proof_layer_id"])
    M = np.zeros((len(ctrls), len(docs)))
    for p in pairs:
        M[ctrls.index(p["proof_layer_id"]), docs.index(p["document"])] = int(p["covered"])
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.imshow(M, cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(docs)), [short(d) for d in docs],
                  rotation=40, ha="right", fontsize=7)
    ax.set_yticks(range(len(ctrls)), ctrls, fontsize=7)
    ax.set_title("Control coverage by document (green = keyword match present)",
                 fontsize=10)
    ax.set_xticks(np.arange(-.5, len(docs), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(ctrls), 1), minor=True)
    ax.grid(which="minor", color="white", lw=1)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"fig3_coverage_heatmap.{ext}"), dpi=200)
    plt.close(fig)
    print("  fig3_coverage_heatmap")


def fig_gaps():
    rows = list(csv.DictReader(open(os.path.join(RES, "coverage_by_control.csv"))))
    for r in rows:
        r["absent"] = int(r["docs_total"]) - int(r["docs_covered"])
    rows.sort(key=lambda r: -r["absent"])
    fig, ax = plt.subplots(figsize=(9, 6))
    y = np.arange(len(rows))
    cols = {"HIGH": "#c62828", "MEDIUM": "#ef6c00", "LOW": "#2e7d32"}
    ax.barh(y, [r["absent"] for r in rows],
            color=[cols.get(r["risk"], "#777") for r in rows])
    ax.set_yticks(y, [f"{r['proof_layer_id']}  {r['control'][:34]}  [{r['nist_800_53_r5']}]"
                      for r in rows], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("Documents with no keyword match (of 10)")
    ax.set_xlim(0, 10)
    ax.set_title("Controls absent across the Maryland corpus, full-text analysis",
                 fontsize=10)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"fig5_gap_frequency.{ext}"), dpi=200)
    plt.close(fig)
    print("  fig5_gap_frequency")


def fig_length():
    docs = list(csv.DictReader(open(os.path.join(RES, "coverage_by_document.csv"))))
    w = np.array([int(d["words"]) for d in docs], float)
    c = np.array([float(d["coverage_pct"]) for d in docs])
    lw = np.log(w)
    r = np.corrcoef(lw, c)[0, 1]
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.scatter(w, c, c=[band(v) for v in c], s=55, zorder=3)
    m, b = np.polyfit(lw, c, 1)
    xs = np.linspace(w.min(), w.max(), 100)
    ax.plot(xs, m * np.log(xs) + b, "--", c="#555", lw=1)
    for d in docs:
        ax.annotate(short(d["document"]), (int(d["words"]), float(d["coverage_pct"])),
                    fontsize=6, xytext=(4, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("Document length (words, log scale)")
    ax.set_ylabel("Control coverage (%)")
    ax.set_title(f"Coverage tracks document length (r = {r:.2f}, "
                 f"$r^2$ = {r*r:.2f}, n = 10)", fontsize=10)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"fig6_length_confound.{ext}"), dpi=200)
    plt.close(fig)
    print(f"  fig6_length_confound  (r={r:.3f})")


if __name__ == "__main__":
    fig_scores(); fig_heatmap(); fig_gaps(); fig_length()
    print("figures written to figures/")
