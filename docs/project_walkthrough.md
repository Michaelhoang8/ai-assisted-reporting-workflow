# First-person portfolio walkthrough

Use this after reviewing and running the files. It describes the actual synthetic implementation and the AI assistance used to produce it.

“I built a reporting workflow around a synthetic e-commerce dataset containing sixty thousand accepted orders. I used Python to validate records and quarantine duplicates, malformed dates and inconsistent values. I used SQL to calculate net revenue, contribution, return rates and channel trends, then reconciled those totals independently in Python.

I created an interactive browser dashboard and an aggregate evidence packet for AI-assisted interpretation. The AI assistant drafted the management commentary, while a separate verifier checked every structured numerical claim against its metric ID, unit and dataset fingerprint. The report renderer inserted the final numbers from the evidence packet rather than trusting numbers embedded in prose.

The scenario showed revenue growth alongside margin pressure, particularly in Paid Search during the second half. I recommended reviewing discount policy and return reasons, while making clear that the scenario was synthetic and did not prove causality or savings.

The local analysis and verification workflow is runnable. AI drafting remains an explicit step using the supplied prompt; no external model API or production scheduler is deployed.”

## Interview discussion

- **Why use AI?** To accelerate the first draft of qualitative interpretation and recommendations while keeping financial computation in SQL.
- **What prevents invented numbers?** The verifier compares structured values and units to known evidence, rejects stale fingerprints, and renders numerical claims from the evidence packet.
- **Does verification guarantee correctness?** No. It checks structured numerical consistency, not every implication of prose. Qualitative review remains necessary.
- **How did you handle large data?** The prototype processes a CSV with tens of thousands of rows and uses SQLite for grouped calculations. It holds validated rows in memory; it is not a benchmark for multi-gigabyte data. A larger deployment would require streaming/batching and a managed database.
- **What business result did you achieve?** A reproducible reporting and verification process, plus scenario-based recommendations. No production savings, adoption or causal result was measured.
