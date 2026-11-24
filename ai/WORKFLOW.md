# How AI participates

1. Python validates raw records and retains a quarantine log.
2. SQL computes the report metrics; Python independently reconciles financial totals.
3. The pipeline writes an aggregate evidence packet containing numbers, units, reporting scopes, metric definitions, limitations and a data/code fingerprint.
4. An AI assistant selects evidence and drafts qualitative interpretation and recommendations in structured JSON. It does not calculate authoritative financial results or correct raw transactions.
5. The local verifier rejects a different dataset fingerprint, unknown metric, changed number, incorrect unit, duplicate claim, unreferenced evidence or free-text numeric statement.
6. The renderer inserts metric labels, formatted numbers and scope directly from the evidence packet. A person reviews the interpretation before using it for decisions.

## What was performed for this portfolio

The assistant authored `ai/summary.json` from the generated evidence packet during this task. The verifier rendered `reports/ai_management_report.md` and recorded validation results. No external model API, credentials or background AI job were used. The code does not regenerate AI commentary autonomously; the prompt and verification steps make that handoff explicit and repeatable.

## Review boundaries

Structured equality checks catch incorrect cited numbers; they do not prove that qualitative prose is true, helpful, non-causal or complete. Evidence IDs show provenance, not support for every possible interpretation. A malicious or careless narrative could still use qualitative falsehoods, so the final review is necessary. This project does not claim to eliminate hallucinations.

The AI receives only aggregate facts in this demonstration. No row-level names, addresses, customer IDs, source exception text or credentials are needed. For another dataset, review the packet's contents before sharing it with an external service.

## Changing the data

Run the pipeline again after replacing the source extract. When the dataset/code fingerprint changes, previous rendered AI outputs are removed as generated artifacts. `ai/summary.json` remains as an authoring file, but its fingerprint will fail validation. Draft a new summary from the new packet; do not simply replace its fingerprint while keeping old findings.

## Manual review checklist

- Do all conclusions match the scopes of their evidence?
- Are monetary claims contribution rather than net profit?
- Are seeded conditions and accounting assumptions visible?
- Are proposed explanations labeled as hypotheses?
- Are recommendations feasible and supported by the dataset's limits?
- Are savings, causality or implementation results being claimed without evidence?
