"""Verify structured AI claims against the exact SQL evidence packet.
Does not claim to fact-check free-text interpretations or recommendations.
"""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify(packet,summary):
 if summary.get('dataset_id')!=packet['dataset_id']:raise ValueError('Stale or mismatched dataset_id')
 if not summary.get('claims'):raise ValueError('Summary requires evidence claims')
 seen=set()
 for claim in summary['claims']:
  key=claim['metric_id']
  if key in seen:raise ValueError('Duplicate metric claim')
  seen.add(key)
  if key not in packet['metrics']:raise ValueError('Unknown metric: '+key)
  metric=packet['metrics'][key]
  if type(claim.get('value')) is not type(metric['value']) or claim['value']!=metric['value']:raise ValueError('Incorrect value for '+key)
  if claim.get('unit')!=metric['unit']:raise ValueError('Incorrect unit for '+key)
 for section in ('interpretations','recommendations'):
  if not isinstance(summary.get(section),list):raise ValueError('Missing '+section)
  for item in summary[section]:
   if not item.get('text') or not item.get('evidence_ids'):raise ValueError('Text and evidence IDs required')
   if any(k not in seen for k in item['evidence_ids']):raise ValueError('Uncited evidence ID')
   # Prose is kept qualitative. Numeric statements are rendered from verified metrics only.
   if re.search(r'\d|[%$]',item['text']):raise ValueError('Put numeric claims in structured metrics, not prose')
 return {'dataset_id':packet['dataset_id'],'dataset_match':True,'numeric_claims_verified':len(seen),'prose_review':'Human review required; evidence links do not establish causality','status':'structured claims passed'}
def display(m):
 value=m['value']
 if value is None:return 'Unavailable'
 if m['unit']=='CAD cents':return f'CAD ${value/100:,.2f}'
 if m['unit']=='ratio':return f'{value:.2%}'
 return f"{value:,} {m['unit']}"
def render(packet,summary,result):
 text=['# AI-assisted management report','','Synthetic portfolio case. This summary was authored by the AI assistant from the local evidence packet. Structured numbers were checked in code; qualitative judgments require human review.','',f"Dataset fingerprint: `{packet['dataset_id']}`",'','## Verified evidence','']
 for c in summary['claims']:
  m=packet['metrics'][c['metric_id']];text.append(f"- **{m['label']}: {display(m)}.** Scope: {m['scope']}. Evidence ID: `{c['metric_id']}`.")
 for section,title in [('interpretations','Interpretation — review required'),('recommendations','Recommended next steps — review required')]:
  text+=['','## '+title,'']
  for item in summary[section]:text.append('- '+item['text']+' Evidence: '+', '.join('`'+k+'`' for k in item['evidence_ids'])+'.')
 text+=['','## Limitations','']+['- '+x for x in packet['limitations']]
 text+=['','Contribution excludes advertising, fixed overhead and tax. Returns are attributed retrospectively to the original order month. This is not a cash-flow or accounting close report.','',f"Validation: {result['numeric_claims_verified']} structured metric claims passed. No external model API or production workflow was invoked."]
 return '\n'.join(text)+'\n'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,default=ROOT/'reports/evidence_packet.json');p.add_argument('--summary',type=Path,default=ROOT/'ai/summary.json');p.add_argument('--output',type=Path,default=ROOT/'reports');a=p.parse_args()
 try:
  packet=json.loads(a.evidence.read_text());summary=json.loads(a.summary.read_text());result=verify(packet,summary)
  a.output.mkdir(parents=True,exist_ok=True);(a.output/'ai_summary_validation.json').write_text(json.dumps(result,indent=2));(a.output/'ai_management_report.md').write_text(render(packet,summary,result),encoding='utf-8');print(json.dumps(result,indent=2))
 except Exception as e:print('AI summary rejected: '+str(e),file=sys.stderr);sys.exit(1)
