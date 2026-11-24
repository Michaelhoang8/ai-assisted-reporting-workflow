-- SQLite SQL. One row per single-item order. All money stored as integer CAD cents.
CREATE VIEW OrderEconomics AS
SELECT *, Quantity*UnitPriceCents GrossSalesCents,
 Quantity*UnitPriceCents-DiscountCents CollectedCents,
 -- Whole-order returns only in the demo; proportional rounding also supports partial units.
 CAST(ROUND((Quantity*UnitPriceCents-DiscountCents)*1.0*ReturnedUnits/Quantity) AS INTEGER) RefundCents,
 Quantity*UnitCostCents COGSCents
FROM Orders;

CREATE VIEW MonthlyChannelPerformance AS
SELECT substr(OrderDate,1,4) Year,substr(OrderDate,1,7) Month,Channel,
 COUNT(*) Orders,SUM(Quantity) Units,SUM(ReturnedUnits) ReturnedUnits,
 SUM(GrossSalesCents) GrossSalesCents,SUM(DiscountCents) DiscountCents,SUM(RefundCents) RefundCents,
 SUM(CollectedCents-RefundCents) NetRevenueCents,SUM(COGSCents) COGSCents,
 SUM(ShippingCostCents) ShippingCostCents,
 SUM(CollectedCents-RefundCents-COGSCents-ShippingCostCents) ContributionCents
FROM OrderEconomics GROUP BY substr(OrderDate,1,4),substr(OrderDate,1,7),Channel;

CREATE VIEW CategoryPerformance AS
SELECT substr(OrderDate,1,4) Year,Category,COUNT(*) Orders,SUM(Quantity) Units,
 SUM(ReturnedUnits) ReturnedUnits,SUM(CollectedCents-RefundCents) NetRevenueCents,
 SUM(CollectedCents-RefundCents-COGSCents-ShippingCostCents) ContributionCents
FROM OrderEconomics GROUP BY substr(OrderDate,1,4),Category;

CREATE VIEW AnnualChannelComparison AS
WITH totals AS (
 SELECT Year,Channel,SUM(Orders) Orders,SUM(NetRevenueCents) NetRevenueCents,
 SUM(ContributionCents) ContributionCents,SUM(Units) Units,SUM(ReturnedUnits) ReturnedUnits,
 SUM(DiscountCents) DiscountCents,SUM(GrossSalesCents) GrossSalesCents
 FROM MonthlyChannelPerformance GROUP BY Year,Channel)
SELECT a.*,b.NetRevenueCents PriorRevenueCents,
 (a.NetRevenueCents-b.NetRevenueCents)*1.0/NULLIF(b.NetRevenueCents,0) RevenueYoY,
 a.ContributionCents*1.0/NULLIF(a.NetRevenueCents,0) ContributionMargin,
 a.ReturnedUnits*1.0/NULLIF(a.Units,0) ReturnUnitRate
FROM totals a LEFT JOIN totals b ON a.Channel=b.Channel AND CAST(a.Year AS INTEGER)=CAST(b.Year AS INTEGER)+1;
