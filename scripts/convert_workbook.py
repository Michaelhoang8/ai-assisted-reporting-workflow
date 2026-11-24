from pathlib import Path
import zipfile,io,xml.etree.ElementTree as ET,csv,gzip,datetime,json,hashlib
root=Path(__file__).resolve().parents[1]/'data/source'
ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
with zipfile.ZipFile(root/'online_retail_ii.zip') as outer:
 with zipfile.ZipFile(io.BytesIO(outer.read('online_retail_II.xlsx'))) as book:
  strings=[]
  with book.open('xl/sharedStrings.xml') as f:
   for _,el in ET.iterparse(f,events=('end',)):
    if el.tag==ns+'si':strings.append(''.join(x.text or '' for x in el.iter(ns+'t')));el.clear()
  count=0
  with gzip.open(root/'retail_lines.csv.gz','wt',encoding='utf-8',newline='') as out:
   writer=csv.writer(out);writer.writerow(['SourceSheet','SourceRow','Invoice','StockCode','Description','Quantity','InvoiceDate','Price','CustomerID','Country'])
   for sheet in ['sheet1','sheet2']:
    with book.open('xl/worksheets/'+sheet+'.xml') as f:
     for _,el in ET.iterparse(f,events=('end',)):
      if el.tag!=ns+'row':continue
      rn=int(el.attrib['r']);values=['']*8
      for c in el.findall(ns+'c'):
       idx=ord(c.attrib['r'][0])-65;v=c.find(ns+'v');value=v.text if v is not None else ''
       if c.attrib.get('t')=='s':value=strings[int(value)]
       if 0<=idx<8:values[idx]=value
      if rn>1 and any(values):
       values[4]=(datetime.datetime(1899,12,30)+datetime.timedelta(days=float(values[4]))).isoformat(timespec='seconds') if values[4] else ''
       writer.writerow([sheet,rn]+values);count+=1
      el.clear()
  print('Converted',count,'retail transaction rows',flush=True)
  assert count==1067371
  p=root/'manifest.json';m=json.loads(p.read_text());m['normalized_file']='retail_lines.csv.gz';m['normalized_rows']=count;m['normalized_sha256']=hashlib.sha256((root/'retail_lines.csv.gz').read_bytes()).hexdigest();p.write_text(json.dumps(m,indent=2))
