#!/usr/bin/env python3
"""Audit public Hoover study decks; extract word spellings and factual source metadata.
No definitions, example sentences, images, or audio recordings are republished.
Downloads are cached in the ignored research directory. Uses system TLS verification.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import ast, hashlib, html, json, re, subprocess, time
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'research'/'decks'; CACHE.mkdir(parents=True,exist_ok=True)
links=json.loads((ROOT/'research/study-links.json').read_text())
def load(item):
 url=item['url']; key=hashlib.sha256(url.encode()).hexdigest()[:16]; file=CACHE/(key+'.html')
 if not file.exists():
  part=file.with_suffix('.part')
  subprocess.run(['/usr/bin/curl','--silent','--show-error','--fail','--location','--max-time','60','--max-filesize','20000000','--retry','2','--retry-delay','2','--output',str(part),url],check=True)
  part.replace(file)
 s=file.read_text()
 title=html.unescape(re.search(r'<title>(.*?)</title>',s,re.S).group(1)).replace(' - Google Slides','')
 match=re.search(r'(\d)\.(\d{2})(N?)',title)
 year=re.search(r'20\d{2}',title)
 kind='school' if re.search(r'school',title,re.I) else 'champions'
 deck={'key':key,'title':title,'url':url,'year':int(year[0]) if year else None,'level':int(match[1]) if match else None,'set':match[0] if match else None,'kind':kind,'words':[]}
 i=s.index('docData: ')
 model,_=json.JSONDecoder().raw_decode(s[i+9:])
 media_details={sl[0]:[{'id':m[1],'name':m[9]} for m in sl[3] if len(m)>9 and isinstance(m[9],str)] for sl in model[1]}
 media={sid:[m['name'] for m in entries] for sid,entries in media_details.items()}
 def clean(text): return re.sub(r'\s+',' ',html.unescape(html.unescape(text))).strip().strip('*').strip()
 def key(text):
  import unicodedata
  return ''.join(c for c in unicodedata.normalize('NFD',text.casefold()) if c.isalpha())
 for m in re.finditer(r"SK_svgData = ('(?:\\.|[^'\\])*');",s):
  svg=ast.literal_eval(m[1].replace('\\/','/'))
  labels=[html.unescape(t).strip() for t in re.findall(r'aria-label="([^"]*)"',svg)]
  gid=re.search(r'<g id="([^"]+)"',svg)
  if not gid or len(labels)<2:continue
  filenames=media.get(gid[1],[])
  targets=[re.sub(r'\.(mp3|wav|m4a|ogg)$','',f,flags=re.I) for f in filenames]
  candidates=[]
  for label in labels:
   head=clean(label)
   if 0<len(head)<=60 and all(c.isalpha() or c in " '-’.," for c in head) and len(head.split())<=5 and head.lower() not in ['sentence','the end','nytimes spelling bee']:
    candidates.append(head)
  matches=[h for h in candidates if any(key(h)==key(t) for t in targets)]
  if matches: head=matches[0];confidence='audio-filename-match'
  elif len(candidates)==1:head=candidates[0];confidence='label-only'
  elif filenames and candidates:
   # Explicit alternate forms may share one recording.
   alternates=[h for h in candidates if any(key(t) in [key(a) for a in re.split(r'\s+or\s+|\s*/\s*',h,flags=re.I)] for t in targets)]
   if alternates:head=alternates[0];confidence='alternate-match'
   else: head=candidates[0];confidence='needs-review'
  else: continue
  detail=next((x for x in labels if re.search(r'\b(Noun|Verb|Adjective|Adverb|Interjection|Preposition|Conjunction|Pronoun)\s*:',x,re.I)), '')
  pos=re.search(r'\b(Plural noun|Noun|Verb|Adjective|Adverb|Interjection|Preposition|Conjunction|Pronoun)\s*:',detail,re.I)
  first=detail.splitlines()[0].strip() if detail else ''
  origin=first if first and ':' not in first and len(first)<150 else ''
  deck['words'].append({'display':head,'slide':gid[1], 'origin':origin,'pos':pos[1].lower() if pos else '', 'confidence':confidence,'audioNames':filenames, 'audio':next((a for a in media_details.get(gid[1],[]) if key(re.sub(r'\.(mp3|wav|m4a|ogg)$','',a['name'],flags=re.I))==key(head)), None)})
 return deck
results=[]; errors=[]
with ThreadPoolExecutor(max_workers=3) as pool:
 tasks={pool.submit(load,item):item for item in links}
 for n,f in enumerate(as_completed(tasks),1):
  try:results.append(f.result())
  except Exception as e:errors.append({'url':tasks[f]['url'],'error':str(e)})
  if n%10==0 or n==len(tasks): print(f'Audited {n}/{len(tasks)} decks; {len(errors)} unavailable',flush=True)
results.sort(key=lambda d:(d['kind'],d['level'] or 0,d['year'] or 0,d['set'] or '',d['title']))
(ROOT/'research'/'deck-audit.json').write_text(json.dumps({'decks':results,'errors':errors},ensure_ascii=False,indent=2))
for d in results: print(d['kind'],d['year'],d['level'],d['set'],len(d['words']),d['title'])
print('Unavailable:',len(errors))
