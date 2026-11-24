"""Local reproducible SQL analytics. Raw data is untrusted input, not AI instructions."""
import argparse,csv,datetime as dt,hashlib,json,sqlite3,sys
from pathlib import Path
from generate_data import HEADERS,CHANNELS
ROOT=Path(__file__).resolve().parents[1]
NUMERIC=HEADERS[5:]
def write_csv(path,headers,rows):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(headers);w.writerows(rows)
def read_validated(raw):
 accepted=[];issues=[];seen={};count=0
 with raw.open(newline='',encoding='utf-8-sig') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=HEADERS:raise ValueError('Unexpected source schema')
  for line,row in enumerate(reader,2):
   count+=1;key=row['OrderID'];reasons=[]
   if key in seen:
    if row!=seen[key]:raise ValueError(f'Conflicting duplicate OrderID {key}; source correction required')
    reasons.append('Exact duplicate OrderID')
   seen[key]=row.copy();typed=row.copy()
   for field,value in row.items():
    try:
     if value is None or value.strip()=='':raise ValueError('blank')
     if field in NUMERIC:typed[field]=int(value)
     elif field=='OrderDate':typed[field]=dt.date.fromisoformat(value).isoformat()
     else:typed[field]=value.strip()
    except (ValueError,AttributeError):reasons.append('Invalid or missing '+str(field))
   if not reasons:
    if typed['Channel'] not in CHANNELS:reasons.append('Unknown channel')
    if typed['Category'] not in ('Home','Outdoor','Accessories'):reasons.append('Unknown category')
    if not (typed['ProductID'].startswith('P') and typed['ProductID'][1:].isdigit() and 1<=int(typed['ProductID'][1:])<=30):reasons.append('Unknown product')
    elif typed['Category']!=['Home','Outdoor','Accessories'][(int(typed['ProductID'][1:])-1)%3]:reasons.append('Product category mismatch')
    if typed['Quantity']<=0:reasons.append('Nonpositive quantity')
    if not 0<=typed['ReturnedUnits']<=typed['Quantity']:reasons.append('Returned units outside quantity')
    if min(typed[k] for k in ['UnitPriceCents','DiscountCents','UnitCostCents','ShippingCostCents'])<0:reasons.append('Negative monetary value')
    if typed['DiscountCents']>typed['Quantity']*typed['UnitPriceCents']:reasons.append('Discount exceeds gross sales')
   if reasons:issues.append([line,key,'; '.join(reasons),json.dumps(row)])
   else:accepted.append([typed[h] for h in HEADERS])
 return count,accepted,issues

def run(raw,out):
 raw=Path(raw);out=Path(out);count,rows,issues=read_validated(raw)
 if not rows:raise ValueError('No accepted source rows')
 db=sqlite3.connect(':memory:')
 ddl=','.join(h+(' INTEGER' if h in NUMERIC else ' TEXT')+(' PRIMARY KEY' if h=='OrderID' else '') for h in HEADERS)
 db.execute('CREATE TABLE Orders('+ddl+')');db.executemany('INSERT INTO Orders VALUES ('+','.join('?' for _ in HEADERS)+')',rows)
 db.executescript((ROOT/'sql/analysis.sql').read_text())
 def query(sql):
  cur=db.execute(sql);return [dict(zip([c[0] for c in cur.description],r)) for r in cur.fetchall()]
 monthly=query('SELECT * FROM MonthlyChannelPerformance ORDER BY Month,Channel')
 annual=query('SELECT * FROM AnnualChannelComparison ORDER BY Year,Channel')
 categories=query('SELECT * FROM CategoryPerformance ORDER BY Year,Category')
 # Independent integer/decimal reconciliation; no reuse of SQL's calculated monetary fields.
 from decimal import Decimal,ROUND_HALF_UP
 gross=discount=refund=cost=shipping=0
 for row in rows:
  r=dict(zip(HEADERS,row));g=r['Quantity']*r['UnitPriceCents'];gross+=g;discount+=r['DiscountCents']
  refund+=int((Decimal(g-r['DiscountCents'])*r['ReturnedUnits']/r['Quantity']).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
  cost+=r['Quantity']*r['UnitCostCents'];shipping+=r['ShippingCostCents']
 net=gross-discount-refund
 checks={'source_row_accounting':count==len(rows)+len(issues),'order_count':sum(r['Orders'] for r in monthly)==len(rows),
 'net_revenue_reconciles':sum(r['NetRevenueCents'] for r in monthly)==net,
 'refunds_reconcile':sum(r['RefundCents'] for r in monthly)==refund,
 'contribution_reconciles':sum(r['ContributionCents'] for r in monthly)==net-cost-shipping,
 'category_revenue_reconciles':sum(r['NetRevenueCents'] for r in categories)==net,
 'annual_revenue_reconciles':sum(r['NetRevenueCents'] for r in annual)==net,
 'rates_bounded':all(0<=r['ReturnedUnits']<=r['Units'] for r in monthly)}
 if not all(checks.values()):raise AssertionError(checks)
 def total(year,key,channel=None,half=None):return sum(r[key] for r in monthly if r['Year']==str(year) and (channel is None or r['Channel']==channel) and (half is None or (int(r['Month'][-2:])>6)==(half==2)))
 def ratio(a,b):return a/b if b else None
 facts={}
 def metric(key,label,value,unit,scope):facts[key]={'label':label,'value':value,'unit':unit,'scope':scope}
 metric('accepted_orders','Accepted orders',len(rows),'orders','All source dates')
 metric('quality_exceptions','Quarantined source rows',len(issues),'rows','All source dates')
 for year in (2024,2025):
  revenue=total(year,'NetRevenueCents');contribution=total(year,'ContributionCents')
  metric(f'revenue_{year}',f'{year} net revenue',revenue,'CAD cents',f'FY{year}, all channels')
  metric(f'contribution_{year}',f'{year} contribution',contribution,'CAD cents',f'FY{year}, all channels')
  metric(f'margin_{year}',f'{year} contribution margin',ratio(contribution,revenue),'ratio',f'FY{year}, all channels')
  metric(f'return_rate_{year}',f'{year} returned-unit rate',ratio(total(year,'ReturnedUnits'),total(year,'Units')),'ratio',f'FY{year}, all channels')
 metric('revenue_yoy','Net revenue year-over-year',ratio(total(2025,'NetRevenueCents')-total(2024,'NetRevenueCents'),total(2024,'NetRevenueCents')),'ratio','FY2025 versus FY2024, all channels')
 for half in (1,2):
  scope=f'FY2025 H{half}, Paid Search';rev=total(2025,'NetRevenueCents','Paid Search',half)
  metric(f'paid_h{half}_margin',f'Paid Search H{half} contribution margin',ratio(total(2025,'ContributionCents','Paid Search',half),rev),'ratio',scope)
  metric(f'paid_h{half}_return_rate',f'Paid Search H{half} returned-unit rate',ratio(total(2025,'ReturnedUnits','Paid Search',half),total(2025,'Units','Paid Search',half)),'ratio',scope)
  metric(f'paid_h{half}_discount_rate',f'Paid Search H{half} discount share of gross sales',ratio(total(2025,'DiscountCents','Paid Search',half),total(2025,'GrossSalesCents','Paid Search',half)),'ratio',scope)
 fingerprint=hashlib.sha256(raw.read_bytes()+Path(__file__).read_bytes()+(ROOT/'sql/analysis.sql').read_bytes()).hexdigest()
 packet={'dataset_id':fingerprint,'provenance':'Synthetic e-commerce data, seed 2026; not an employer dataset','metrics':facts,
 'definitions':{'net_revenue':'Gross sales minus discounts minus refunds','contribution':'Net revenue minus all original product cost and shipping; excludes acquisition cost, tax and fixed overhead','return_rate':'Returned units divided by sold units; lifetime returns attributed to order month','reporting_basis':'Retrospective order-cohort analysis; not an as-of cash or general-ledger report'},
 'limitations':['No measured savings or causal effect','Returned goods assumed unsellable; original product cost retained','No advertising spend, customer IDs or causal experiment','Paid Search second-half discount and return pressure deliberately seeded','All AI interpretations require human review']}
 out.mkdir(parents=True,exist_ok=True)
 # Never leave an old AI report beside a changed dataset as if it were current.
 ai_validation=out/'ai_summary_validation.json'
 summary_current=False
 if ai_validation.exists():
  summary_current=json.loads(ai_validation.read_text()).get('dataset_id')==fingerprint
  if not summary_current:
   for artifact in ('ai_summary_validation.json','ai_management_report.md'):
    (out/artifact).unlink(missing_ok=True)
 write_csv(out/'clean_orders.csv',HEADERS,rows)
 write_csv(out/'data_quality_exceptions.csv',['Line','OrderID','Reason','RawRecord'],issues)
 for name,data in [('monthly_channel_performance',monthly),('annual_channel_comparison',annual),('category_performance',categories)]:
  if data:write_csv(out/(name+'.csv'),list(data[0]),[list(r.values()) for r in data])
 (out/'evidence_packet.json').write_text(json.dumps(packet,indent=2))
 (out/'validation_results.json').write_text(json.dumps(checks,indent=2))
 (out/'dashboard_data.json').write_text(json.dumps(monthly,indent=2))
 template=(ROOT/'src/dashboard_template.html').read_text(encoding='utf-8')
 (out/'dashboard.html').write_text(template.replace('__DATA__',json.dumps(monthly)),encoding='utf-8')
 db.commit();dest=sqlite3.connect(out/'analytics.sqlite');db.backup(dest);dest.close();db.close()
 manifest={'dataset_id':fingerprint,'raw_rows':count,'accepted_rows':len(rows),'quarantined_rows':len(issues),'checks_passed':len(checks),'ai_summary_status':'current verified summary retained' if summary_current else 'awaiting evidence-linked AI summary'}
 (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,default=ROOT/'data/raw/orders.csv');p.add_argument('--output',type=Path,default=ROOT/'reports');a=p.parse_args()
 try:print(json.dumps(run(a.raw,a.output),indent=2))
 except Exception as e:print('Pipeline failed: '+str(e),file=sys.stderr);sys.exit(1)
