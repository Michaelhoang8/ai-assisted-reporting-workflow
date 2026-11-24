# Data source and transformation policy

Publisher: Daqing Chen — UCI Online Retail II

Dataset: https://doi.org/10.24432/C5CG6D

Size: 1,067,371 real transaction lines from December 2009 to December 2011

Retrieved UTC: 2026-11-24T19:41:37.642293+00:00

Download: https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip

Original SHA-256: `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb`

Reuse/attribution reference: https://creativecommons.org/licenses/by/4.0/. Government sources are published for public reuse under their portal terms; this repository does not relicense the source data as project code. UCI Online Retail II is attributed to Daqing Chen (2012), DOI 10.24432/C5CG6D, under CC BY 4.0. No source publisher endorses this analysis.

The raw government CSV is gzip-compressed without altering field content. UCI's workbook is converted by the included XML streaming converter into a lossless-field CSV, with explicit sheet and row references and Excel dates converted to ISO timestamps. The original workbook download is available through the source manifest; the large ZIP is not committed.

## Grain, calculations and limitations

Positive sales, cancellations, country concentration, monthly trends, data-quality exclusions and an evidence-linked AI report. SQL owns the calculations; the verifier checks every structured claim, unit and dataset fingerprint.

Costs, profit, marketing channels and inventory are not available. Cancellations are not matched physical returns. Exact repeated fields are excluded under a disclosed assumption with value sensitivity in the evidence packet. Customer IDs can be missing; the final month is partial. No paid API calls or automatic prose regeneration occur.

Pinned snapshots make builds reproducible. A new upstream download must be reviewed as a new data version: update its manifest and checksums, rebuild outputs, re-review AI claims where applicable and recapture media. Never silently change a pinned snapshot.
