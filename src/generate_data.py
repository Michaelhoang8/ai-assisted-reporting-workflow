"""Deterministic fictional e-commerce line-item exports; no external data access."""
import csv,random,calendar
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HEADERS=['OrderID','OrderDate','Channel','ProductID','Category','Quantity','UnitPriceCents','DiscountCents','UnitCostCents','ShippingCostCents','ReturnedUnits']
CHANNELS=['Organic','Paid Search','Marketplace','Email']
def generate():
 rng=random.Random(2026);raw=ROOT/'data/raw';raw.mkdir(parents=True,exist_ok=True)
 rows=[]
 for year in (2024,2025):
  for month in range(1,13):
   for n in range(2500):
    channel=rng.choices(CHANNELS,weights=[30,35,25,10])[0]
    product=rng.randint(1,30);category=['Home','Outdoor','Accessories'][(product-1)%3]
    qty=rng.randint(1,4);price=1800+product*210;cost=round(price*.48)
    if year==2025:price=round(price*1.07);cost=round(cost*1.05)
    gross=qty*price
    promo=.20 if year==2025 and month>=7 and channel=='Paid Search' else rng.choice([0,.05,.10])
    discount=round(gross*promo)
    returned=qty if rng.random()<(.16 if year==2025 and month>=7 and channel=='Paid Search' else .045) else 0
    day=rng.randint(1,calendar.monthrange(year,month)[1])
    rows.append([f'O{len(rows)+1:06}',f'{year}-{month:02}-{day:02}',channel,f'P{product:03}',category,qty,price,discount,cost,rng.randint(400,1000),returned])
 # Intentional ingestion defects, preserved in the raw export.
 rows.extend([rows[0].copy(),rows[123].copy()])
 for key,index,value in [('BAD_CHANNEL',2,'Unknown'),('BAD_DATE',1,'2025-02-30'),('BAD_PRICE',6,''),('BAD_RETURNS',10,99)]:
  row=rows[100].copy();row[0]=key;row[index]=value;rows.append(row)
 with (raw/'orders.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(HEADERS);w.writerows(rows)
 print(f'Generated {len(rows):,} synthetic rows at {raw}')
if __name__=='__main__':generate()
