"""Small, conservative Wiktionary gloss reader. Source revisions stay attached."""
import re,html
POS={'Noun','Verb','Adjective','Adverb','Proper noun','Interjection','Preposition','Conjunction','Pronoun','Numeral','Phrase','Determiner','Particle','Prepositional phrase'}
LANG=re.compile(r'^[a-z]{2,3}(?:-[a-z0-9]+)?$')
FORM_NAMES={'plural of','en-plural of','alternative spelling of','alternative form of','alt form','alt sp','alt form of','alternative case form of','obsolete spelling of','archaic spelling of','obsolete form of','archaic form of','synonym of','syn of','abbreviation of','initialism of','acronym of','clipping of','ellipsis of','inflection of','infl of','en-past of','en-third-person singular of','en-ing form of','present participle of','past participle of','simple past of','comparative of','superlative of','feminine of','masculine of','diminutive of','standard spelling of','chiefly','en-superlative of','en-comparative of','en-irregular plural of','en-verb form of','alternative typography of','alt case','aphetic form of','short for','apocopic form of','altsp','alt spelling of','obs form','stand sp','standard form of','dated spelling of','sylabbr of'}
REMOVABLE={'senseid','sid','sense','defdate','rfdef','rfe','attention','senseid-safe','senseno','rfex','rfv-sense','rfquote-sense','defdt','defdate','topics','topic','c','C','categorize','catlangname','catlangcode','pedia','wikipedia box'}
def args_of(text):
 parts=[];part='';depth=0;i=0
 while i<len(text):
  pair=text[i:i+2]
  if pair=='[[':depth+=1;part+=pair;i+=2;continue
  if pair==']]':depth=max(0,depth-1);part+=pair;i+=2;continue
  if text[i]=='|' and depth==0:parts.append(part);part=''
  else:part+=text[i]
  i+=1
 parts.append(part)
 return parts[0].strip().lower(),[a.strip() for a in parts[1:] if not re.match(r'^[A-Za-z0-9_-]+=',a.strip())]
def target_of(text):
 name,args=args_of(text)
 if name in FORM_NAMES:
  if args and LANG.fullmatch(args[0]):args=args[1:]
  return args[0] if args else ''
 return ''
def plain(s):
 s=re.sub(r'<!--.*?-->','',s,flags=re.S)
 s=re.sub(r'<ref\b[^>]*(?:/>|>.*?</ref>)','',s,flags=re.S|re.I);s=re.sub(r'<[^>]+>','',s)
 for _ in range(20):
  def temp(m):
   name,args=args_of(m[1])
   if name in REMOVABLE or name.startswith(('r:','cite','quote')):return ''
   if name in ['lb','label','lbl','tlb','context']:
    labels=args[1:] if args and LANG.fullmatch(args[0]) else args
    labels=[x for x in labels if x not in ['transitive','intransitive','countable','uncountable','usually','chiefly','often','not comparable','comparable','attributive','and','or','_','!']]
    return '('+', '.join(labels)+') ' if labels else ''
   if name in ['qualifier','qual','q','i','a','accent']:return '('+', '.join(args)+') ' if args else ''
   if name in ['gloss','gl','non-gloss definition','ngd','ng','n-g','non-gloss']:return args[-1] if args else ''
   if name in ['l','m','link','mention','term','ll']:
    if args and LANG.fullmatch(args[0]):args=args[1:]
    return args[1] if len(args)>1 else args[0] if args else ''
   if name in ['w','wikipedia']:return args[1] if len(args)>1 else args[0] if args else ''
   if name in FORM_NAMES:
    target=target_of(m[1]);label={'infl of':'Form of','inflection of':'Form of','alt form':'Alternative form of','alt sp':'Alternative spelling of','en-plural of':'Plural of','en-superlative of':'Superlative of','en-comparative of':'Comparative of','syn of':'Synonym of'}.get(name,name.capitalize())
    return label+' '+target if target else ''
   if name in ['given name','surname']:return 'A given name' if name=='given name' else 'A surname'
   if name in ['taxlink','vern','taxfmt','taxon']:return args[0] if args else ''
   if name in ['smallcaps','smallcap','sc','nowrap','nobr','sic','nuclide','ipa char','ipachar','cap','u','1','lang','nobr','frac','unsupported','langname','vern','lena','lre']:
    return args[-1] if args else ''
   if name in ['sup','sub']:
    tr=str.maketrans('0123456789-','⁰¹²³⁴⁵⁶⁷⁸⁹⁻' if name=='sup' else '₀₁₂₃₄₅₆₇₈₉₋');return args[0].translate(tr) if args else ''
   if name in ['chemf']:return ''.join(args)
   if name in ['b.c.e.','c.e.']:return name.upper()
   if name=='place':
    vals=args[1:] if args and LANG.fullmatch(args[0]) else args
    def location(value):
     value=re.sub(r'<<([^<>]+)>>',lambda m:m[1].split('/',1)[-1],value)
     return value.split('/',1)[-1] if '/' in value else value
    if not vals:return ''
    if '<<' in vals[0]:return location(vals[0])
    if any(v in [';',';and the','in the'] for v in vals):return m[0]
    kind={'caplc':'capital city','adr':'administrative region','cc':'country','city':'city'}.get(vals[0],vals[0])
    if '/' in kind:return m[0]
    places=[location(v) for v in vals[1:] if '/' in v]
    if not places:return m[0]
    return ('An ' if kind[:1].lower() in 'aeiou' else 'A ')+kind+' in '+', '.join(places)
   if name in ['demonym-adj','demonym-noun']:
    vals=args[1:] if args and LANG.fullmatch(args[0]) else args
    place=', '.join(vals);place=re.sub(r'<<([^<>]+)>>',lambda m:m[1].split('/',1)[-1],place)
    return ('Relating to ' if name=='demonym-adj' else 'A person from ')+place
   if name=='si-unit' and len(args)>=4 and args[1]=='milli':return 'One thousandth of a '+args[2]+', a unit of '+args[3]
   if name in [',',';']:return name+' '
   if name in ['century']:return (args[0]+'th century') if args else ''
   if name in ['+obj']:return ''
   return m[0]
  v=re.sub(r'\{\{([^{}]*)\}\}',temp,s)
  if v==s:break
  s=v
 if '{{' in s or '}}' in s:return ''
 s=re.sub(r'\[\[([^]]+)\]\]',lambda m:m[1].split('|')[-1].split('#',1)[0],s);s=re.sub(r'\[https?://[^ ]+ ([^]]+)\]',r'\1',s)
 s=s.replace("'''",'').replace("''",'');s=html.unescape(s);s=re.sub(r'\s+',' ',s).strip(' ;')
 return s if 8<=len(s)<=450 and len(s.split())<=70 and not re.search(r'https?://|\||\[\[|\]\]',s) else ''
def extract(text,w):
 m=re.search(r'^==\s*English\s*==\s*$(.*?)(?=^==[^=\n].*?==\s*$|\Z)',text,re.M|re.S)
 if not m:return []
 pos='';entries=[]
 for line in m[1].splitlines():
  h=re.match(r'^={3,6}([^=]+)={3,6}\s*$',line)
  if h:pos=h[1].strip();continue
  if pos not in POS or not re.match(r'^#+(?![:*#])\s*',line):continue
  if re.search(r'\{\{(?:lb|label)\|[^}]*\b(?:offensive|vulgar|slur)\b',line,re.I):continue
  raw=re.sub(r'^#+\s*','',line);p=plain(raw)
  if p.startswith(('Senses relating to','Senses concerning','Senses related to')):continue
  if p and not any(e['text']==p for e in entries):
   target=next((target_of(t) for t in re.findall(r'\{\{([^{}]*)\}\}',raw) if target_of(t)),None)
   entries.append({'pos':pos.lower(),'text':p,**({'lemma':target} if target else {})})
 preferred=[e for e in entries if e['pos'] in w.get('pos',[]) or e['pos']=='proper noun' and 'noun' in w.get('pos',[])]
 # Modern explanatory senses beat historical senses and bare form references.
 def tokens(text):
  stop={'the','and','that','with','which','from','this','used','having','such','into','relating','being','also','something','someone','person','especially','often','very','more','most','other','another','one','ones','own','each','either','whose','there','than','same','both','some','any','all','its','their','them','about','upon','into','between','form','word','words','noun','verb','adjective'}
  found=set()
  for t in re.findall(r'[^\W\d_]+',text.lower()):
   if len(t)<3 or t in stop:continue
   if t.endswith('ies') and len(t)>5:t=t[:-3]+'y'
   elif t.endswith('s') and not t.endswith(('ss','us','is')) and len(t)>4:t=t[:-1]
   found.add(t)
  return found
 context=tokens(w.get('_context',''))-tokens(w.get('word',''))
 def rank(e):
  overlap=context & tokens(e['text']);score=sum(min(8,len(t)) for t in overlap)
  outdated=bool(re.search(r'^\([^)]*(?:obsolete|archaic|historical|very rare)',e['text']))
  vague=bool(re.match(r'^(?:Something|Anything) resembling|^Other places named|^A given name',e['text']))
  return (outdated,vague,-score,bool(e.get('lemma')))
 return sorted(preferred or entries,key=rank)[:2]
