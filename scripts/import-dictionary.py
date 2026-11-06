#!/usr/bin/env python3
"""Import short English glosses from Wiktionary, preserving source revision and CC BY-SA attribution.
Unsupported wikitext templates are skipped, not guessed. School-specific senses still need human review.
"""
import json,re,html,subprocess,time,hashlib,urllib.parse
from pathlib import Path
R=Path(__file__).resolve().parents[1]; cache=R/'research/dictionary';cache.mkdir(exist_ok=True)
words=json.loads((R/'data/words.json').read_text());out={};missing=[]
POS={'Noun','Verb','Adjective','Adverb','Proper noun','Interjection','Preposition','Conjunction','Pronoun','Numeral','Phrase'}
def plain(s):
 s=re.sub(r'<ref\b[^>]*>.*?</ref>','',s,flags=re.S|re.I);s=re.sub(r'<[^>]+>','',s)
 for _ in range(15):
  def temp(m):
   t=m[1].split('|');name=t[0].lower();args=t[1:]
   if name in ['lb','label','context','senseid','sense','defdate','rfdef','rfe','qualifier','qual','q','gloss','non-gloss definition','ngd','n-g','chiefly','attention','senseid-safe']:return '' if name not in ['gloss','non-gloss definition','ngd','n-g'] else (args[-1] if args else '')
   if name in ['l','m','link','mention','term']:
    vals=[a for a in args if '=' not in a];return vals[2] if len(vals)>2 else vals[1] if len(vals)>1 else ''
   if name in ['w','wikipedia']:return args[1] if len(args)>1 else args[0] if args else ''
   if name in ['plural of','en-plural of']:
    a=args[1] if len(args)>1 and len(args[0])<4 else args[0] if args else '';return 'Plural of '+a
   if name in ['given name','surname']:return 'A given name' if name=='given name' else 'A surname'
   if name in ['abbreviation of','initialism of','acronym of']:
    vals=[a for a in args if '=' not in a];return name.capitalize()+' '+(vals[1] if len(vals)>1 else vals[0] if vals else '')
   if name in ['taxlink','vern','taxfmt']:return args[0] if args else ''
   if name in ['smallcaps','smallcap','sc','nowrap','nobr','sic','nuclide']:return args[0] if args else ''
   return m[0]
  v=re.sub(r'\{\{([^{}]*)\}\}',temp,s)
  if v==s:break
  s=v
 if '{{' in s or '[[' not in s and ']]' in s:return ''
 s=re.sub(r'\[\[(?:[^]|]+\|)?([^]]+)\]\]',r'\1',s)
 s=re.sub(r'\[https?://[^ ]+ ([^]]+)\]',r'\1',s)
 s=s.replace("'''",'').replace("''",'');s=html.unescape(s);s=re.sub(r'\s+',' ',s).strip(' ;')
 return s if 12<=len(s)<=450 and len(s.split())<=65 and not re.search(r'https?://|\|',s) else ''
def glosses(text,w):
 m=re.search(r'^==English==\s*$(.*?)(?=^==[^=\n].*?==\s*$|\Z)',text,re.M|re.S)
 if not m:return []
 pos='';entries=[]
 for line in m[1].splitlines():
  h=re.match(r'^={3,6}([^=]+)={3,6}\s*$',line)
  if h:pos=h[1].strip();continue
  if pos not in POS or not re.match(r'^#(?![:*#])\s*',line):continue
  if re.search(r'\{\{(?:lb|label)\|[^}]*\b(?:offensive|vulgar|derogatory|slur|obsolete|archaic)\b',line,re.I):continue
  p=plain(re.sub(r'^#\s*','',line))
  if p and not any(e['text']==p for e in entries):entries.append({'pos':pos.lower(),'text':p})
 preferred=[e for e in entries if e['pos'] in w['pos'] or e['pos']=='proper noun' and 'noun' in w['pos']]
 return (preferred or entries)[:2]
for i in range(0,len(words),50):
 batch=words[i:i+50];titles='|'.join(w['word'] for w in batch);params={'action':'query','format':'json','formatversion':'2','prop':'revisions','rvprop':'ids|content','rvslots':'main','redirects':'1','titles':titles}
 url='https://en.wiktionary.org/w/api.php?'+urllib.parse.urlencode(params);path=cache/(hashlib.sha256(titles.encode()).hexdigest()[:16]+'.json')
 try:
  if not path.exists():
   subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','40','--user-agent','MollyChampionsLocalPrototype/0.1 (personal educational word-study import)','--output',str(path),url],check=True)
   time.sleep(6)
  data=json.loads(path.read_text());q=data.get('query',{});rename={a['from']:a['to'] for a in q.get('normalized',[])+q.get('redirects',[])};pages={p['title']:p for p in q.get('pages',[])}
  for w in batch:
   title=w['word']
   for _ in range(5):
    if title in rename:title=rename[title]
    else:break
   page=pages.get(title,{});rev=page.get('revisions',[{}])[0];text=rev.get('slots',{}).get('main',{}).get('content','');g=glosses(text,w)
   if g:out[w['id']]={'glosses':g,'title':title,'revision':rev.get('revid'),'source':'https://en.wiktionary.org/w/index.php?'+urllib.parse.urlencode({'title':title,'oldid':rev.get('revid')}),'credit':'Wiktionary contributors','license':'CC BY-SA 4.0'}
   else:missing.append(w['id'])
 except Exception as e:
  print('Import paused after a network or rate-limit response; no more requests will be sent in this run.',flush=True);missing.extend(w['id'] for w in words[i:]);break
 if i%500==0 or i+50>=len(words):print(f'Dictionary: {min(i+50,len(words))}/{len(words)} checked; {len(out)} with usable English glosses',flush=True)
 (R/'data/dictionary.json').write_text(json.dumps(out,ensure_ascii=False))
(R/'research/dictionary-audit.json').write_text(json.dumps({'enriched':len(out),'missing':missing,'note':'Automatically cleaned English dictionary glosses; not independently checked against the bee-specific sense.'},indent=2))
print('Finished',len(out),'dictionary cards;',len(missing),'source-study-only cards',flush=True)
