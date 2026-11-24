# AI-assisted management report

Real UCI Online Retail II records. This summary was authored by the AI assistant from the local evidence packet. Structured numbers were checked in code; qualitative judgments require human review.

Dataset fingerprint: `6f161fca7f6e0d53e65c46502d4aa119ae847731a214bab5ab3f7d43823da530`

## Verified evidence

- **SalesPence: GBP 20,476,260.43.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `SalesPence`.
- **CancellationPence: GBP 1,462,424.18.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `CancellationPence`.
- **AdjustmentPence: GBP 0.00.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `AdjustmentPence`.
- **NetPence: GBP 19,013,836.25.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `NetPence`.
- **SaleInvoices: 40,077 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `SaleInvoices`.
- **Countries: 43 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `Countries`.
- **SourceRows: 1,067,371 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `SourceRows`.
- **AcceptedRows: 1,027,016 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `AcceptedRows`.
- **ExcludedRepeats: 34,147 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `ExcludedRepeats`.
- **ExcludedInvalid: 6,208 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `ExcludedInvalid`.
- **MissingCustomerRows: 229,201 count.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `MissingCustomerRows`.
- **RepeatedLinePence: GBP 431,716.87.** Scope: 2009-12-01 to 2011-12-09; deduplicated valid-price lines unless explicitly source/exclusion count. Evidence ID: `RepeatedLinePence`.

## Interpretation — review required

- Cancellation entries materially reduce the positive recorded sales value. They should be reviewed as a separate accounting stream rather than assumed to be matched product returns. Evidence: `SalesPence`, `CancellationPence`, `NetPence`.
- Missing customer identifiers limit customer-level analyses, while the corresponding valid transaction values remain usable in country and monthly reporting. Evidence: `MissingCustomerRows`, `AcceptedRows`.
- Repeated source fields affect the recorded-value estimate. Deduplication is a documented analytical assumption, and the excluded amount provides a sensitivity measure. Evidence: `ExcludedRepeats`, `RepeatedLinePence`.

## Recommended next steps — review required

- Investigate the highest-value cancellation invoices alongside the original records before drawing conclusions about operational causes. Evidence: `CancellationPence`.
- Compare complete overlapping months when assessing trends; exclude the partial final month from full-month growth claims. Evidence: `SourceRows`, `SaleInvoices`.
- Report deduplication sensitivity and customer-coverage limitations alongside any commercial recommendation. Evidence: `RepeatedLinePence`, `MissingCustomerRows`.

## Limitations

- Real historical records from a UK retailer; not current market conditions.
- Exact repeated fields are removed as a disclosed analysis assumption; distinct identical purchases cannot be resolved from this source. RepeatedLinePence measures sensitivity to that choice.
- C-prefixed invoices are cancellations, not necessarily completed cash refunds or matched physical returns.
- No product costs, discounts, advertising channels, inventory balances or payment terms are available; no profit or AP aging is inferred.
- Missing customers are retained for transaction value; customer analyses would require an identified-customer subset.
- Final December is partial; do not compare it with full calendar months. Source prices are normalized to six decimal places to remove spreadsheet binary artifacts, then each line is rounded to pence half-up.

Recorded sales and cancellation line values are not profit or cash flow. Cancellations remain in their recorded invoice month.

Validation: 12 structured metric claims passed. No external model API or production workflow was invoked.
