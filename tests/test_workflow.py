from contextlib import closing
import copy,csv,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import run,read_validated
from generate_data import HEADERS
from verify_summary import verify

class DataTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.raw=self.root/'orders.csv';self.out=self.root/'reports'
  self.rows=[['A','2024-01-15','Organic','P001','Home',3,101,2,40,10,1],['B','2025-01-15','Email','P002','Outdoor',2,200,0,80,20,2]];self.write()
 def tearDown(self):self.temp.cleanup()
 def write(self):
  with self.raw.open('w',newline='') as f:w=csv.writer(f);w.writerow(HEADERS);w.writerows(self.rows)
 def test_partial_refund_rounding_and_contribution(self):
  result=run(self.raw,self.out)
  with closing(sqlite3.connect(self.out/'analytics.sqlite')) as db:
   self.assertEqual(db.execute("SELECT RefundCents FROM OrderEconomics WHERE OrderID='A'").fetchone()[0],100)
   self.assertEqual(db.execute("SELECT ContributionCents FROM MonthlyChannelPerformance WHERE Year='2024'").fetchone()[0],71)
   self.assertEqual(db.execute("SELECT NetRevenueCents,ContributionCents FROM MonthlyChannelPerformance WHERE Year='2025'").fetchone(),(0,-180))
  self.assertEqual(result['checks_passed'],8)
 def test_exact_duplicate_quarantined(self):
  self.rows.append(self.rows[0].copy());self.write();count,accepted,issues=read_validated(self.raw)
  self.assertEqual((count,len(accepted),len(issues)),(3,2,1))
 def test_conflicting_duplicate_fails(self):
  row=self.rows[0].copy();row[6]=102;self.rows.append(row);self.write()
  with self.assertRaisesRegex(ValueError,'Conflicting duplicate'):read_validated(self.raw)
 def test_missing_price_not_zero(self):
  self.rows[0][6]='';self.write();_,a,e=read_validated(self.raw);self.assertEqual(len(a),1);self.assertIn('UnitPriceCents',e[0][2])
 def test_discount_and_returns_rejected(self):
  self.rows[0][7]=99999;self.rows[1][10]=3;self.write();_,a,e=read_validated(self.raw);self.assertEqual((len(a),len(e)),(0,2))
 def test_changed_data_invalidates_ai_artifacts(self):
  old=run(self.raw,self.out);(self.out/'ai_summary_validation.json').write_text(json.dumps({'dataset_id':old['dataset_id']}));(self.out/'ai_management_report.md').write_text('Old summary')
  self.rows[0][6]=105;self.write();new=run(self.raw,self.out)
  self.assertNotEqual(old['dataset_id'],new['dataset_id']);self.assertFalse((self.out/'ai_management_report.md').exists())
 def test_identical_data_same_fingerprint(self):
  self.assertEqual(run(self.raw,self.out)['dataset_id'],run(self.raw,self.out)['dataset_id'])

class SummaryTests(unittest.TestCase):
 def setUp(self):
  self.packet={'dataset_id':'abc','metrics':{'m':{'value':123,'unit':'CAD cents'}}}
  self.summary={'dataset_id':'abc','claims':[{'metric_id':'m','value':123,'unit':'CAD cents'}],'interpretations':[{'text':'Revenue warrants review','evidence_ids':['m']}],'recommendations':[]}
 def test_valid_summary_passes(self):self.assertEqual(verify(self.packet,self.summary)['numeric_claims_verified'],1)
 def test_wrong_value_rejected(self):
  self.summary['claims'][0]['value']=124
  with self.assertRaisesRegex(ValueError,'Incorrect value'):verify(self.packet,self.summary)
 def test_wrong_unit_rejected(self):
  self.summary['claims'][0]['unit']='CAD dollars'
  with self.assertRaisesRegex(ValueError,'Incorrect unit'):verify(self.packet,self.summary)
 def test_stale_summary_rejected(self):
  self.summary['dataset_id']='old'
  with self.assertRaisesRegex(ValueError,'Stale'):verify(self.packet,self.summary)
 def test_unknown_metric_rejected(self):
  self.summary['claims'][0]['metric_id']='invented'
  with self.assertRaisesRegex(ValueError,'Unknown metric'):verify(self.packet,self.summary)
 def test_numeric_prose_rejected(self):
  self.summary['interpretations'][0]['text']='Revenue rose 50%'
  with self.assertRaisesRegex(ValueError,'numeric claims'):verify(self.packet,self.summary)
 def test_uncited_evidence_rejected(self):
  self.summary['interpretations'][0]['evidence_ids']=['unknown']
  with self.assertRaisesRegex(ValueError,'Uncited'):verify(self.packet,self.summary)
 def test_duplicate_claim_rejected(self):
  self.summary['claims'].append(copy.deepcopy(self.summary['claims'][0]))
  with self.assertRaisesRegex(ValueError,'Duplicate'):verify(self.packet,self.summary)
if __name__=='__main__':unittest.main()
