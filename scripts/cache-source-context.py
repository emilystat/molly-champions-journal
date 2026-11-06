"""Keep source-study context privately for sense matching; no slide prose enters app data."""
import ast,json,re,html,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('source_cache',type=Path);a=p.parse_args()
words=json.loads((R/'data/words.json').read_text());manifest=json.loads((R/'data/manifest.json').read_text());sets={s['key']:s for s in manifest['sources']};wanted={}
for w in words:
 ref=sorted(w['refs'],key=lambda r:(sets[r['source']]['year'],sets[r['source']]['category']=='new-2027'),reverse=True)[0]
 wanted.setdefault(ref['source'],{})[ref['slide']]=w
out={}
for key,slides in wanted.items():
 text=(a.source_cache/(key+'.html')).read_text()
 for m in re.finditer(r"SK_svgData = ('(?:\\.|[^'\\])*');",text):
  svg=ast.literal_eval(m[1].replace('\\/','/'));sid=re.search(r'<g id="([^"]+)"',svg)
  if not sid or sid[1] not in slides:continue
  labels=[html.unescape(t).strip() for t in re.findall(r'aria-label="([^"]*)"',svg)]
  detail=next((s for s in labels if re.search(r'\b(?:Plural noun|Noun|Verb|Adjective|Adverb|Interjection|Preposition|Conjunction|Pronoun)\s*:',s,re.I)),'')
  context=re.sub(r'^.*?\b(?:Plural noun|Noun|Verb|Adjective|Adverb|Interjection|Preposition|Conjunction|Pronoun)\s*:\s*','',detail,flags=re.S|re.I)
  if context:out[slides[sid[1]]['id']]={'context':context,'source':key,'slide':sid[1]}
(R/'research/source-context.json').write_text(json.dumps(out,ensure_ascii=False));print('Cached private source context for',len(out),'word-sense matches.')
