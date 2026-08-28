# Error analysis, ProofLayer Stage 1 keyword matcher

Produced for the CDFJ revision, 25 August 2026, in response to Reviewer 1
item 12. Every example below is traceable to a row in
`results/coverage_by_pair.csv` and to the source PDF.

No expert-annotated ground truth exists for this corpus, so these are not
sampled from a labelled set and no precision or recall figure is computed from
them. They are cases identified by inspecting the matched keyword and its
surrounding text, which is the strongest error analysis available without
annotators, and it is reported as such.

## Scale of the diagnostic signals

Of 220 document-control pairs, 138 were scored as covered.

| signal | count | share of covered |
|---|---|---|
| covered on exactly one matched keyword | 61 | 44.2% |
| a negation cue within 130 characters of the hit | 25 | 18.1% |
| both of the above | 8 | 5.8% |
| mean keywords matched when covered | 1.97 of 6.1 available | |

## Representative false positives

**A URL counted as encryption in transit.** PL-14 (Data Encryption in Transit,
NIST SC-8) is scored present in the MD Cybersecurity Council Report on the
strength of the keyword `https`. The match is a footnote citation:

> "...report was developed by Dr. Greg von Lehmen, University of Maryland
> Global Campus, as staff to the Maryland Cybersecurity Council.
> `https://www.umgc.edu/mdcybersecuritycouncil`..."

The document is not asserting a transport-encryption control. It is citing a
web page.

**Organisational roles counted as role-based access control.** PL-03 (Least
Privilege / RBAC, NIST AC-6) is scored present in two documents on the keyword
`roles`, matching:

> "...the department responsible for **roles**: developing, maintaining,
> revising, and enforcing information security policy..."

This is a statement about departmental responsibility, not about privilege
assignment.

**A negated clause counted as personnel screening.** PL-18 (Personnel
Screening, NIST PS-3) is scored present in the MD IT Security Manual on
`clearance`, matching:

> "...procedures for the use of maintenance personnel that **lack** appropriate
> security **clearances** or are not US citizens..."

The sentence describes handling personnel who do not hold clearances. Keyword
presence records the opposite of what the passage says.

## A representative false negative, and what it costs the paper

**PL-11 (Incident Reporting, NIST IR-6) is scored absent from the MD Judicial
Information Security Policy.** The document states:

> "...requirements for **notifying** the JIS information security officer
> within **two business days** of a security incident on the network."

That is an incident reporting requirement with an explicit timeframe. It was
missed because the control's keyword list contains "incident reporting",
"report incident", "notification requirement" and similar, but not "notify" or
"notifying".

This matters beyond the single cell. The submitted manuscript inferred from the
absence of PL-11 that Maryland agency policies "have not been updated to
reflect the mandatory reporting timelines" of recent federal requirements. At
least one document in the corpus states a reporting timeline explicitly. The
inference does not survive contact with the text.

## What these errors have in common

Three of the four cases are not marginal keyword choices. They are structural
limits of lexical matching: a URL is not a control, a word can appear inside a
negation, and a concept can be expressed in vocabulary the list does not
contain. Enlarging the keyword lists addresses the fourth case and makes the
first three worse, because a longer list matches more incidental text.

This is the argument for the Stage 2 classifier the manuscript describes. It is
not evidence that the Stage 2 classifier works, which remains unevaluated.
