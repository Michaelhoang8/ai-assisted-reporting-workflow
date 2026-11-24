# Data dictionary and analytical definitions

Source: `data/raw/orders.csv`, created locally with seed 2026. All money is CAD cents in storage. Dates are ISO strings. Text fields are bounded to the fictional catalog and channel list.

| Field | Meaning / rule |
|---|---|
| OrderID | Unique one-product order key; exact ingestion replays quarantined |
| OrderDate | Original purchase date, valid ISO calendar date |
| Channel | Organic, Paid Search, Marketplace or Email |
| ProductID | P001–P030 |
| Category | Home, Outdoor or Accessories; must match product mapping |
| Quantity | Positive integer units sold |
| UnitPriceCents | Nonnegative unit selling price before discount |
| DiscountCents | Order-level discount; cannot exceed quantity × unit price |
| UnitCostCents | Nonnegative original unit product cost |
| ShippingCostCents | Nonnegative cost to ship the order |
| ReturnedUnits | Between zero and quantity, inclusive; final retrospective returns |

## Transformations

- Gross sales = quantity × unit price.
- Collected before returns = gross sales − order discount.
- Refund = collected × returned units / sold units, rounded to the nearest cent, halves up. The demonstration generates full-order returns; the calculation and tests also support partial returns.
- Net revenue = collected − refund.
- Product cost = original quantity × unit cost. Returned product cost is not recovered.
- Contribution = net revenue − product cost − shipping.
- Contribution margin = summed contribution / summed net revenue.
- Returned-unit rate = summed returned units / summed sold units.
- Discount share = summed discount / summed gross sales.
- Year-over-year revenue = (current − prior) / prior; missing or zero prior revenue gives unavailable.

Rates aggregate from their numerators and denominators, never from averaging channel percentages. Source units and cents remain present in report CSVs, with formatting applied only in the dashboard or rendered narrative.

## Quality policy

The supplied data has two exact duplicate rows, one unknown channel, one invalid date, one missing price and one impossible return quantity. Invalid records are retained in the exception CSV with line numbers and raw-row evidence. Conflicting records sharing an OrderID stop the run; the pipeline does not arbitrarily pick a winner. Nulls are not imputed to zero.

Raw count = accepted count + rejected count. SQL totals are reconciled against independent Python integer/Decimal calculations. This establishes internal consistency, not source completeness for an external system.

## Evidence lineage

Raw CSV → validated Orders table → OrderEconomics → MonthlyChannelPerformance / CategoryPerformance / AnnualChannelComparison → evidence packet → assistant-authored structured summary → verified Markdown report.

Each evidence ID carries its scope and unit. `dataset_id` is a SHA-256 digest of the raw export, runner source and SQL source. It links claims to this exact analysis version; it is not a digital signature or security attestation.
