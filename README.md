# AI-Assisted Retail Reporting

**1,067,371 real transaction lines from December 2009 to December 2011.** A reproducible analysis of real public data from [Daqing Chen — UCI Online Retail II](https://doi.org/10.24432/C5CG6D). The default reports use observed records, with no synthetic financial or operational fields.

![Report preview](docs/screenshots/dashboard.png)

[Dashboard recording](docs/recordings/walkthrough.mp4) · [Screenshot gallery](docs/screenshots) · [Data provenance](docs/DATA_SOURCE.md)

## What the project demonstrates

Positive sales, cancellations, country concentration, monthly trends, data-quality exclusions and an evidence-linked AI report. SQL owns the calculations; the verifier checks every structured claim, unit and dataset fingerprint.

## Run locally

Python 3.10+; standard library only. Compressed source snapshots are checked in, so analysis runs offline.

```sh
python scripts/verify_source.py
python src/pipeline.py
python src/verify_summary.py
python -m unittest discover -s tests -v
```

Open `reports/dashboard.html` in a browser. Generated SQLite databases are excluded from Git to keep the repository compact; running the pipeline recreates them from the full source. No sampled subset is substituted for the full extract.

## Optional AI workflow

[Read the verified report](reports/ai_management_report.md), [evidence packet](reports/evidence_packet.json), and [claim-verification result](reports/ai_summary_validation.json). The supplied summary was authored by an AI assistant from this actual evidence. Free-text interpretation still needs human review.

For a different model, use [the prompt](ai/SUMMARY_PROMPT.md), provide the evidence packet, save its structured JSON draft, and run `python src/verify_summary.py --summary path/to/draft.json`. No provider or API key is required by the local pipeline. A changed dataset or analysis invalidates the old draft.

## Analytical scope

Costs, profit, marketing channels and inventory are not available. Cancellations are not matched physical returns. Exact repeated fields are excluded under a disclosed assumption with value sensitivity in the evidence packet. Customer IDs can be missing; the final month is partial. No paid API calls or automatic prose regeneration occur.

## Reviewable files

- `data/source/`: compressed full source snapshot, source URL, retrieval timestamp and checksums.
- `src/` and `sql/`: transformations, reporting calculations and local rendering.
- `reports/`: computed summaries, validation results and source-quality evidence.
- `tests/`: edge-case tests for the actual source semantics.
- `docs/`: methodology, screenshots and an automated browser walkthrough.

The earlier synthetic demonstration remains in Git history. Current outputs and screenshots were rebuilt from these public sources; recordings demonstrate the reports, not a person's development session.
