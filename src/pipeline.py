"""Analyze the full UCI Online Retail II extract without model API calls."""
import csv,gzip,hashlib,json,sqlite3,datetime
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def classify(row):
 qty=int(row['Quantity']);price=Decimal(row['Price']).quantize(Decimal('.000001'));invoice=row['Invoice'].strip()
 datetime.datetime.fromisoformat(row['InvoiceDate'])
 if not price.is_finite() or price<=0:raise ValueError('Nonpositive price')
 if qty==0:raise ValueError('Zero quantity')
 if not invoice or not row['StockCode']:raise ValueError('Missing invoice or product')
 cancel=invoice.upper().startswith('C')
 if cancel and qty>=0:raise ValueError('Cancellation without negative quantity')
 kind='Cancellation' if cancel else 'Adjustment' if qty<0 else 'Sale'
 amount=int((price*qty*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
 return invoice,row['InvoiceDate'][:10],row['Country'].strip() or 'Unknown',row['StockCode'],row['CustomerID'],qty,amount,kind
def main():
 source=ROOT/'data/source/retail_lines.csv.gz';db=sqlite3.connect(ROOT/'reports/analytics.sqlite')
 db.executescript('DROP TABLE IF EXISTS Lines; CREATE TABLE Lines(Invoice TEXT,Date TEXT,Country TEXT,Product TEXT,Customer TEXT,Quantity INTEGER,AmountPence INTEGER,Kind TEXT,SourceSheet TEXT,SourceRow INTEGER);')
 seen=set();batch=[];raw=accepted=duplicates=invalid=missing_customer=0;duplicate_pence=0;issues=[]
 with gzip.open(source,'rt',encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   raw+=1
   key=hashlib.sha256(json.dumps([row[k] for k in ['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','CustomerID','Country']],ensure_ascii=False).encode()).digest()
   try:record=classify(row)
   except (ValueError,ArithmeticError) as exc:
    invalid+=1;issues.append([row['SourceSheet'],row['SourceRow'],str(exc)]);continue
   if key in seen:
    duplicates+=1;duplicate_pence+=record[6];issues.append([row['SourceSheet'],row['SourceRow'],'Exact repeated source fields; excluded by declared deduplication policy']);continue
   seen.add(key);accepted+=1;missing_customer+=not bool(record[4]);batch.append((*record,row['SourceSheet'],int(row['SourceRow'])))
   if len(batch)>=10000:db.executemany('INSERT INTO Lines VALUES(?,?,?,?,?,?,?,?,?,?)',batch);batch=[]
 if batch:db.executemany('INSERT INTO Lines VALUES(?,?,?,?,?,?,?,?,?,?)',batch)
 db.executescript((ROOT/'sql/analysis.sql').read_text(encoding='utf-8'));db.commit()
 def query(sql):
  c=db.execute(sql);return [dict(zip([x[0] for x in c.description],r)) for r in c]
 monthly=query('SELECT * FROM MonthlyCountry ORDER BY Month,Country');countries=query('SELECT Country,SUM(AmountPence) NetPence,COUNT(*) LineCount FROM Lines GROUP BY Country ORDER BY NetPence DESC');products=query("SELECT Product,SUM(AmountPence) NetPence,COUNT(DISTINCT Invoice) Invoices FROM Lines GROUP BY Product ORDER BY NetPence DESC LIMIT 25")
 totals=query("SELECT SUM(CASE WHEN Kind='Sale' THEN AmountPence ELSE 0 END) SalesPence,SUM(CASE WHEN Kind='Cancellation' THEN -AmountPence ELSE 0 END) CancellationPence,SUM(CASE WHEN Kind='Adjustment' THEN AmountPence ELSE 0 END) AdjustmentPence,SUM(AmountPence) NetPence,COUNT(DISTINCT CASE WHEN Kind='Sale' THEN Invoice END) SaleInvoices,COUNT(DISTINCT Country) Countries,MIN(Date) FirstDate,MAX(Date) LastDate FROM Lines")[0]
 checks={'source_row_accounting':raw==accepted+duplicates+invalid,'full_published_dataset':raw==1067371,'monetary_bridge':totals['NetPence']==totals['SalesPence']-totals['CancellationPence']+totals['AdjustmentPence'],'monthly_reconciliation':sum(r['NetPence'] for r in monthly)==totals['NetPence'],'country_reconciliation':sum(r['NetPence'] for r in countries)==totals['NetPence'],'accepted_count_matches_database':db.execute('SELECT COUNT(*) FROM Lines').fetchone()[0]==accepted}
 assert all(checks.values()),checks
 with gzip.open(ROOT/'reports/data_quality_exceptions.csv.gz','wt',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['SourceSheet','SourceRow','Reason']);w.writerows(issues)
 def export(name,rows):
  with (ROOT/'reports'/name).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 export('monthly_country.csv',monthly);export('country_summary.csv',countries);export('top_products.csv',products)
 dataset_id=hashlib.sha256(source.read_bytes()+Path(__file__).read_bytes()+(ROOT/'sql/analysis.sql').read_bytes()).hexdigest()
 metrics={}
 for key,value in {**totals,'SourceRows':raw,'AcceptedRows':accepted,'ExcludedRepeats':duplicates,'ExcludedInvalid':invalid,'MissingCustomerRows':missing_customer,'RepeatedLinePence':duplicate_pence}.items():
  if isinstance(value,int):metrics[key]={'value':value,'unit':'GBP pence' if key.endswith('Pence') else 'count','label':key,'scope':totals['FirstDate']+' to '+totals['LastDate']+'; deduplicated valid-price lines unless explicitly source/exclusion count'}
 limitations=['Real historical records from a UK retailer; not current market conditions.','Exact repeated fields are removed as a disclosed analysis assumption; distinct identical purchases cannot be resolved from this source. RepeatedLinePence measures sensitivity to that choice.','C-prefixed invoices are cancellations, not necessarily completed cash refunds or matched physical returns.','No product costs, discounts, advertising channels, inventory balances or payment terms are available; no profit or AP aging is inferred.','Missing customers are retained for transaction value; customer analyses would require an identified-customer subset.','Final December is partial; do not compare it with full calendar months. Source prices are normalized to six decimal places to remove spreadsheet binary artifacts, then each line is rounded to pence half-up.']
 packet={'dataset_id':dataset_id,'provenance':'Daqing Chen, Online Retail II, UCI, DOI 10.24432/C5CG6D, CC BY 4.0','metrics':metrics,'limitations':limitations}
 (ROOT/'reports/evidence_packet.json').write_text(json.dumps(packet,indent=2),encoding='utf-8')
 manifest={'dataset_id':dataset_id,'raw_rows':raw,'accepted_rows':accepted,'duplicate_rows':duplicates,'invalid_rows':invalid,'missing_customer_rows':missing_customer,'totals':totals,'checks':checks}
 (ROOT/'reports/validation_results.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 payload={'monthly':monthly,'countries':countries,'products':products,'validation':manifest}
 (ROOT/'reports/dashboard_data.json').write_text(json.dumps(payload),encoding='utf-8')
 template=(ROOT/'src/dashboard_template.html').read_text(encoding='utf-8');(ROOT/'reports/dashboard.html').write_text(template.replace('__DATA__',json.dumps(payload)),encoding='utf-8')
 # Never let an earlier verified report survive a changed evidence fingerprint.
 v=ROOT/'reports/ai_summary_validation.json'
 if v.exists() and json.loads(v.read_text())['dataset_id']!=dataset_id:
  v.unlink();(ROOT/'reports/ai_management_report.md').unlink(missing_ok=True)
 db.close();print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
