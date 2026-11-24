import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import classify
from verify_summary import verify
class RetailTests(unittest.TestCase):
 def row(self,**kw):return {'Invoice':'123','Quantity':'3','Price':'1.005','InvoiceDate':'2011-01-01T10:00:00','StockCode':'A','CustomerID':'','Country':'UK',**kw}
 def test_round_line_not_unit(self):self.assertEqual(classify(self.row())[6],302)
 def test_cancellation_sign(self):self.assertEqual(classify(self.row(Invoice='C123',Quantity='-3'))[-1],'Cancellation')
 def test_negative_adjustment_separate(self):self.assertEqual(classify(self.row(Quantity='-1'))[-1],'Adjustment')
 def test_zero_price_excluded(self):
  with self.assertRaises(ValueError):classify(self.row(Price='0'))
 def test_missing_customer_retained(self):self.assertEqual(classify(self.row())[4],'')
 def test_invalid_cancellation_rejected(self):
  with self.assertRaises(ValueError):classify(self.row(Invoice='C123'))
class EvidenceTests(unittest.TestCase):
 def setUp(self):
  self.packet={'dataset_id':'abc','metrics':{'m':{'value':123,'unit':'GBP pence'}}};self.summary={'dataset_id':'abc','claims':[{'metric_id':'m','value':123,'unit':'GBP pence'}],'interpretations':[{'text':'Investigate cancellations','evidence_ids':['m']}],'recommendations':[]}
 def test_valid(self):self.assertEqual(verify(self.packet,self.summary)['numeric_claims_verified'],1)
 def test_stale(self):
  self.summary['dataset_id']='old'
  with self.assertRaises(ValueError):verify(self.packet,self.summary)
 def test_wrong_value(self):
  self.summary['claims'][0]['value']=124
  with self.assertRaises(ValueError):verify(self.packet,self.summary)
 def test_numeric_prose(self):
  self.summary['interpretations'][0]['text']='Revenue rose 90%'
  with self.assertRaises(ValueError):verify(self.packet,self.summary)
 def test_wrong_unit(self):
  self.summary['claims'][0]['unit']='USD'
  with self.assertRaises(ValueError):verify(self.packet,self.summary)
if __name__=='__main__':unittest.main()
