#!/usr/bin/env python3
"""Reuse only source-attributed, English usage examples for the chosen sense; skip quotations."""
import json,re,unicodedata
from pathlib import Path
from dictionary_source import extract,plain,args_of
R=Path(__file__).resolve().parents[1];words=json.loads((R/'data/words.json').read_text());dictionary=json.loads((R/'data/dictionary.json').read_text());pages={};aliases={}
for p in (R/'research/dictionary').glob('*.json'):
 d=json.loads(p.read_text()).get('query',{});pages.update({x['title']:x for x in d.get('pages',[])});aliases.update({x['from']:x['to'] for x in d.get('normalized',[])+d.get('redirects',[])})
def norm(text):return unicodedata.normalize('NFKD',text).casefold().replace('’',"'")
def template_sentence(line):
 m=re.search(r'\{\{(?:ux|usex|uxi|eg)\|en\|',line)
 if not m:return ''
 i=m.end();depth=1;brackets=0;part=''
 while i<len(line):
  pair=line[i:i+2]
  if pair=='{{':depth+=1;part+=pair;i+=2;continue
  if pair=='}}':
   depth-=1
   if depth==0:return plain(part)
   part+=pair;i+=2;continue
  if pair=='[[':brackets+=1;part+=pair;i+=2;continue
  if pair==']]':brackets=max(0,brackets-1);part+=pair;i+=2;continue
  if line[i]=='|' and depth==1 and brackets==0:return plain(part)
  part+=line[i];i+=1
 return ''
selected={}
for w in words:
 d=dictionary[w['id']]
 if d.get('sourceType')=='study-note':continue
 title=d['title'];p=pages.get(title,{});text=p.get('revisions',[{}])[0].get('slots',{}).get('main',{}).get('content','');en=re.search(r'^==English==\s*$(.*?)(?=^==[^=\n].*?==\s*$|\Z)',text,re.M|re.S)
 if not en:continue
 sense='';candidates=[]
 for line in en[1].splitlines():
  if re.match(r'^#+(?![:*#])\s*',line):sense=plain(re.sub(r'^#+\s*','',line));continue
  if not re.match(r'^#+:',line) or not sense:continue
  if not any(g['text'].startswith(sense) for g in d['glosses']):continue
  sentence=template_sentence(line)
  if not sentence and "'''" in line and '{{' not in line:sentence=plain(re.sub(r'^#+:\s*','',line))
  if not sentence or not 6<=len(sentence.split())<=32 or len(sentence)>230 or not sentence.endswith(('.','!','?')):continue
  if norm(w['word']) not in norm(sentence):continue
  if re.search(r'\b(fuck\w*|shit\w*|sex\w*|porn\w*|rape\w*|suicid\w*|kill\w*|murder\w*|nazi\w*|hitler|prostitut\w*|genital\w*|penis|vagina)\b',sentence,re.I):continue
  if '<!--' in sentence or '-->' in sentence or '{{' in sentence or 'http' in sentence:continue
  candidates.append(sentence)
 if candidates:selected[w['id']]={'text':min(candidates,key=len),'source':d['source'],'credit':'Wiktionary contributors','license':'CC BY-SA 4.0','type':'dictionary-usage'}
(R/'data/example-batches').mkdir(exist_ok=True)
(R/'data/example-batches/wiktionary.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
queue=[{'id':w['id'],'word':w['word'],'level':w['level'],'new2027':w['new2027'],'meaning':dictionary[w['id']]['glosses'][0]['text']} for w in words if w['id'] not in selected]
(R/'research/example-queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
print('Licensed usage examples:',len(selected),'Original examples still needed:',len(queue))
