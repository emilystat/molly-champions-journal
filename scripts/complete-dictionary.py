#!/usr/bin/env python3
"""Resumable, serial public-dictionary import; cached batches and coverage log survive interruptions."""
import argparse,json,time,re,subprocess,hashlib,urllib.parse,datetime,csv,io
from pathlib import Path
from dictionary_source import extract
P=argparse.ArgumentParser();P.add_argument('--fetch',action='store_true');P.add_argument('--scope',choices=['all','new2027'],default='all');P.add_argument('--max-batches',type=int,default=100);P.add_argument('--delay',type=float,default=6);P.add_argument('--lemmas',action='store_true');P.add_argument('--case-fallback',action='store_true');P.add_argument('--extras',type=Path);P.add_argument('--mirror',type=Path);A=P.parse_args()
R=Path(__file__).resolve().parents[1];CACHE=R/'research/dictionary';CACHE.mkdir(parents=True,exist_ok=True)
words=json.loads((R/'data/words.json').read_text());context_path=R/'research/source-context.json';source_context=json.loads(context_path.read_text()) if context_path.exists() else {};
for w in words:w['_context']=source_context.get(w['id'],{}).get('context','')
lookup_alias_path=R/'data/lookup-aliases.json';lookup_aliases=json.loads(lookup_alias_path.read_text()) if lookup_alias_path.exists() else {};by_id={w['id']:w for w in words};pages={};aliases={};checked=set();errors=[]
def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)
def load_response(data):
 q=data.get('query',{});aliases.update({a['from']:a['to'] for a in q.get('normalized',[])+q.get('redirects',[])})
 for p in q.get('pages',[]):
  pages[p['title']]=p;checked.add(p['title'])
 checked.update(a['from'] for a in q.get('normalized',[])+q.get('redirects',[]))
for p in CACHE.glob('*.json'):
 try:load_response(json.loads(p.read_text()))
 except (ValueError,KeyError):pass

def lookup(title):
 for _ in range(10):
  if title in aliases:title=aliases[title]
  else:break
 return pages.get(title),title

def rebuild(state='running'):
 out={};pending=[];lemma_targets=set();needs_lemma=set()
 for w in words:
  p,title=lookup(w['word']);rev=(p or {}).get('revisions',[{}])[0];raw=rev.get('slots',{}).get('main',{}).get('content','');g=extract(raw,w)
  if not g:
   candidates=[w['word'][:1].upper()+w['word'][1:],w['word'].title(),w['word'].lower()]+lookup_aliases.get(w['word'],[])
   for candidate in candidates:
    cp,ct=lookup(candidate);cr=(cp or {}).get('revisions',[{}])[0];cg=extract(cr.get('slots',{}).get('main',{}).get('content',''),w)
    if cg:p,title,rev,g=cp,ct,cr,cg;break
  refs=[]
  def explain(target,trail=()):
   if target in trail or len(trail)>4:return None,[]
   lp,lt=lookup(target);lr=(lp or {}).get('revisions',[{}])[0]
   if target not in checked:lemma_targets.add(target)
   lg=extract(lr.get('slots',{}).get('main',{}).get('content',''),w)
   ref={'title':lt,'revision':lr.get('revid'),'url':'https://en.wiktionary.org/w/index.php?'+urllib.parse.urlencode({'title':lt,'oldid':lr.get('revid')})}
   direct=next((x for x in lg if not x.get('lemma')),None)
   if direct:return direct['text'],[ref]
   for child in lg:
    if child.get('lemma'):
     meaning,chain=explain(child['lemma'],trail+(target,))
     if meaning:return meaning,[ref]+chain
   return None,[]
  for e in g:
   target=e.pop('lemma',None)
   if target and target!=title:
    meaning,chain=explain(target)
    if meaning:
     e['text']=e['text'].rstrip('. ')+'. '+meaning;e['clue']=meaning
     e['text']=e['text'] if len(e['text'])<=450 else e['text'][:448].rsplit(' ',1)[0]+'…';refs.extend(chain)
    else:needs_lemma.add(w['id'])

  if g:
   out[w['id']]={'glosses':g,'title':title,'revision':rev.get('revid'),'source':'https://en.wiktionary.org/w/index.php?'+urllib.parse.urlencode({'title':title,'oldid':rev.get('revid')}),'credit':'Wiktionary contributors','license':'CC BY-SA 4.0',**({'additionalSources':refs} if refs else {})}
  else:pending.append({'id':w['id'],'word':w['word'],'level':w['level'],'new2027':w['new2027'],'reason':'not-fetched' if w['word'] not in checked else 'missing-entry-or-unsupported-definition'})
 # Do not erase usable cards while a newer parser/source is incomplete.
 existing=json.loads((R/'data/dictionary.json').read_text())
 for id,d in existing.items():
  if id not in out:out[id]=d
 notes_path=R/'data/study-notes.json'
 if notes_path.exists():
  for id,d in json.loads(notes_path.read_text()).items():
   if id not in by_id:raise ValueError('A study note has an unknown word ID.')
   out[id]=d;needs_lemma.discard(id)
 pending=[p for p in pending if p['id'] not in out]
 if len(out)==len(words) and not needs_lemma:state='explanations-complete'
 if not needs_lemma:lemma_targets.clear()
 coverage={'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'total':len(words),'cards':len(out),'dictionaryCards':sum(d.get('sourceType')!='study-note' for d in out.values()),'studyNotes':sum(d.get('sourceType')=='study-note' for d in out.values()),'remaining':len(words)-len(out),'new2027':{'total':sum(w['new2027'] for w in words),'cards':sum(w['new2027'] and w['id'] in out for w in words)},'categories':{str(l):{'total':sum(w['level']==l for w in words),'cards':sum(w['level']==l and w['id'] in out for w in words)} for l in [1,2,3]},'sourcePagesCached':len(pages),'pendingLemmaPages':len(lemma_targets),'errors':errors,'editorialStatus':'Dictionary entries are source-attributed; matching the exact bee sense still needs editorial review.'}
 coverage['needsLemmaExplanation']=len(needs_lemma);
 checklist=io.StringIO();writer=csv.writer(checklist);writer.writerow(['word','category','new_2027','card_status','dictionary_source'])
 for w in words:
  status='original_study_note' if out.get(w['id'],{}).get('sourceType')=='study-note' else 'needs_lemma_explanation' if w['id'] in needs_lemma else 'dictionary_available' if w['id'] in out else 'source_checked_no_usable_definition' if w['word'] in checked else 'not_fetched'
  writer.writerow([w['word'],['','One Bee','Two Bee','Three Bee'][w['level']],'yes' if w['new2027'] else 'no',status,out.get(w['id'],{}).get('source','')])
 (R/'WORD_CHECKLIST.csv').write_text(checklist.getvalue())
 atomic(R/'data/dictionary.json',out);atomic(R/'data/coverage.json',coverage);atomic(R/'research/dictionary-pending.json',pending)
 log=f'''# Word-card completion tracker\n\nLast checkpoint: {coverage['updatedAt']}\n\nState: **{state}**. Every successful batch is saved. This file is generated from the actual word records, not estimated progress.\n\n| Category | Explanations | Total | Remaining |\n| --- | ---: | ---: | ---: |\n'''
 for l,label in [(1,'One Bee'),(2,'Two Bee'),(3,'Three Bee')]:
  c=coverage['categories'][str(l)];log+=f"| {label} | {c['cards']} | {c['total']} | {c['total']-c['cards']} |\n"
 c=coverage['new2027'];log+=f"\n**All explanations: {len(out)} / {len(words)}.** Explicitly new 2027 words: **{c['cards']} / {c['total']}**.\n\n- Complete definitions and form/lemma explanations before claiming all study cards are finished.\n- Preserve per-entry Wiktionary revisions and CC BY-SA 4.0 attribution.\n- Keep original One / Two / Three Bee categories and stable word IDs; saved progress is unaffected.\n- Rare words, dictionary sense matching and pronunciation still need content review.\n- Official 2027 list reconciliation is separate from definition coverage.\n- Current source fetches are serial, cached and spaced by at least {A.delay:g} seconds. A network error or rate limit stops the run instead of skipping words or repeatedly retrying.\n"
 if errors:log+='\n## Last source issue\n\n'+errors[-1]+'\n'
 log+='\n## Resume\n\nRun `python3 scripts/complete-dictionary.py --fetch --scope new2027` for current-season additions, or `--scope all` for remaining words. Cached pages are reused. Run without `--fetch` to rebuild cards from cache only. Keep the ignored `research/dictionary` cache with the working checkout between parts.\n'
 (R/'WORK_TRACKER.md').write_text(log)
 history=R/'PROGRESS_LOG.jsonl';event={k:coverage[k] for k in ['updatedAt','state','cards','remaining','new2027','needsLemmaExplanation','errors']}
 with history.open('a') as stream:stream.write(json.dumps(event,ensure_ascii=False)+'\n')
 if A.mirror:
  for relative in ['data/dictionary.json','data/coverage.json','WORK_TRACKER.md','WORD_CHECKLIST.csv','PROGRESS_LOG.jsonl']:
   target=A.mirror/relative;target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_suffix(target.suffix+'.tmp');temp.write_bytes((R/relative).read_bytes());temp.replace(target)
 return out,lemma_targets

def fetch(titles):
 key=hashlib.sha256('|'.join(titles).encode()).hexdigest()[:16];path=CACHE/(key+'.json');header=CACHE/(key+'.headers');temp=CACHE/(key+'.download')
 params={'action':'query','format':'json','formatversion':'2','prop':'revisions','rvprop':'ids|content','rvslots':'main','redirects':'1','maxlag':'5','titles':'|'.join(titles)}
 url='https://en.wiktionary.org/w/api.php?'+urllib.parse.urlencode(params)
 r=subprocess.run(['/usr/bin/curl','--compressed','--silent','--show-error','--location','--max-time','35','--user-agent','MollyWordJournal/0.2 (personal educational study; https://emilystat.github.io/molly-spelling-bee/)','--dump-header',str(header),'--output',str(temp),'--write-out','%{http_code}',url],capture_output=True,text=True)
 status=r.stdout.strip()
 if r.returncode or status!='200':
  wait=next((line.strip() for line in header.read_text().splitlines() if line.lower().startswith('retry-after:')),'') if header.exists() else ''
  raise RuntimeError(f"Public dictionary request stopped: HTTP {status or 'unavailable'}; {wait or r.stderr.strip() or 'retry later'}. No later batches were requested.")
 data=json.loads(temp.read_text())
 if data.get('error'):raise RuntimeError('Dictionary API returned '+json.dumps(data['error']))
 if not isinstance(data.get('query',{}).get('pages'),list):raise RuntimeError('Dictionary response had no pages; kept existing work.')
 temp.replace(path);load_response(data);
 if A.mirror:
  target=A.mirror/'research/dictionary'/path.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
 return len(titles)

out,lemmas=rebuild('preparing');scope=[w for w in words if A.scope=='all' or w['new2027']];scope.sort(key=lambda w:(not w['new2027'],w['level'],w['word']))
pending=[w['word'] for w in scope if w['word'] not in checked]
if A.case_fallback:
 for w in scope:
  p,title=lookup(w['word']);raw=(p or {}).get('revisions',[{}])[0].get('slots',{}).get('main',{}).get('content','')
  if not extract(raw,w):pending.extend(t for t in [w['word'][:1].upper()+w['word'][1:],w['word'].title(),w['word'].lower()]+lookup_aliases.get(w['word'],[]) if t not in checked)
if A.extras:pending.extend(t for t in json.loads(A.extras.read_text()) if t not in checked)
if A.lemmas:pending.extend(t for t in sorted(lemmas) if t not in checked)
pending=list(dict.fromkeys(pending));count=0
print(f"Starting {A.scope}: {len(out)}/{len(words)} cards; {len(pending)} uncached requested words",flush=True)
if A.fetch:
 while count<A.max_batches:
  titles=pending[:50]
  if not titles:break
  try:fetch(titles)
  except Exception as e:errors.append(str(e));rebuild('paused-source-issue');print(str(e),flush=True);raise SystemExit(2)
  pending=pending[50:];count+=1;out,lemmas=rebuild('importing')
  print(f"Batch {count}: {len(out)}/{len(words)} cards; {sum(w['new2027'] and w['id'] in out for w in words)}/505 new 2027",flush=True);time.sleep(max(6,A.delay))
 out,lemmas=rebuild('batch-saved' if pending else 'source-pass-complete')
print(f"Saved {len(out)}/{len(words)} cards. {len(lemmas)} lemma sources still needed.",flush=True)
