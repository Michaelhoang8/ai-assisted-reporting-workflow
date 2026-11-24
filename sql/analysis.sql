CREATE INDEX IF NOT EXISTS ix_lines_month_country ON Lines(Date,Country);
DROP VIEW IF EXISTS MonthlyCountry;
CREATE VIEW MonthlyCountry AS
SELECT SUBSTR(Date,1,7) Month, Country, COUNT(*) LineCount,
 SUM(CASE WHEN Kind='Sale' THEN AmountPence ELSE 0 END) SalesPence,
 SUM(CASE WHEN Kind='Cancellation' THEN -AmountPence ELSE 0 END) CancellationPence,
 SUM(CASE WHEN Kind='Adjustment' THEN AmountPence ELSE 0 END) AdjustmentPence,
 SUM(AmountPence) NetPence,
 COUNT(DISTINCT CASE WHEN Kind='Sale' THEN Invoice END) SaleInvoices
FROM Lines GROUP BY SUBSTR(Date,1,7),Country;
