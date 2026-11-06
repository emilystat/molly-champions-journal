#!/usr/bin/env python3
"""Apply explicitly reviewed wording; keep source records and stable word IDs."""
from pathlib import Path
import json,re,collections
R=Path(__file__).resolve().parents[1];words=json.loads((R/'data/words.json').read_text());byid={w['id']:w for w in words};byword={w['word']:w for w in words};manifest=json.loads((R/'data/manifest.json').read_text());sources={s['key']:s for s in manifest['sources']};dictionary=json.loads((R/'data/dictionary.json').read_text());notes=json.loads((R/'data/study-notes.json').read_text());audit={}
# These short explanations were independently compared with the original study sense.
review_paths=[R/f'research/example-part-{n}-issues.json' for n in [1,2,3]]+[R/f'research/cross-review-part-{n}-issues.json' for n in [1,2,3]]+sorted((R/'research').glob('cross-review-part-*-closure-issues.json'))+sorted((R/'research').glob('cross-review-part-*-pos-issues.json'))+[R/'research/cross-review-part-3-tail-issues.json',R/'research/licensed-pos-issues.json',R/'research/independent-wiktionary-content-issues.json',R/'research/tricenary-example-closure-issue.json']
reviewed_pos={}
example_fixes={byword['prespinous']['id']:{'text':"The anatomy diagram marked the prespinous area above the shoulder blade's bony ridge.",'type':'original','credit':'Original example for Molly','license':'Original example wording'}}
for path in review_paths:
 if not path.exists():continue
 data=json.loads(path.read_text());records=data.items() if isinstance(data,dict) else [(r['id'],r) for r in data]
 for id,r in records:
  text=next((r[k] for k in ['proposedExplanation','proposedGloss','proposedSense','proposedDefinition'] if r.get(k)),None)
  if text:audit[id]={'word':r['word'],'text':text,'reviewer':path.stem,'reason':r.get('reason','Source-sense selection corrected.')}
  if r.get('proposedPos'):reviewed_pos[id]=r['proposedPos']
  example=r.get('replacementExample') or r.get('proposedExample')
  if example and path.name!='independent-wiktionary-content-issues.json':example_fixes[id]=example if isinstance(example,dict) else {'text':example,'type':'original','credit':'Original example for Molly','license':'Original example wording'}
extra={
'enterprising':'Showing initiative, resourcefulness, and readiness to try new projects.',
'gnome':'In folklore, a small earth-dwelling being often said to guard treasure.',
'protein':'A large biological molecule made from amino acids and essential to living things.',
'supercargo':'An officer on a merchant ship who supervises cargo and commercial business.',
'ad ignorantiam':'Arguing that a claim is true merely because it has not been disproved.',
'ammonite':'A nitrogen-rich fertilizer made from animal remains; also, a coiled fossil shell.',
'arrieros':'Mexican fiesta dances associated with muleteers and their camps.',
'capitalist':'A person who invests capital in businesses, or who supports capitalism.',
'copperhead':'A venomous snake with a copper-colored head.',
'calyx':'The group of sepals that surrounds and protects a flower bud.',
'channelopathy':'A disorder involving abnormal function of the ion channels in cells.',
'crinoid':'A marine animal in the sea-lily and feather-star group, known both living and as fossils.',
'ctetology':'A historical theory concerning the origin or inheritance of acquired characteristics.',
'frater':'An old term for the shared dining hall of a monastery.',
'impluvium':'A sunken basin that collected rainwater in the courtyard of an ancient Roman house.',
'Juglar':'The name associated with a recurring cycle of business expansion and contraction.',
'parietal':'Relating to a body-cavity wall; in the skull, associated with its upper sides.',
'weazen':'To shrink or wither, sometimes used figuratively for cowering.',
'Alzheimer':'The surname used in the name of Alzheimer disease, which affects memory and thinking.',
'tricenary':'Lasting thirty days, or based on the number thirty.',
'prespinous':'Relating to the area of the shoulder blade above its bony ridge.',
'terminator':'A DNA sequence that signals the end of transcription, when an RNA copy is made.',
'pierrot':'A comic character in traditional French pantomime, usually with a white-painted face and loose white clothes.',
'musings':'Thoughts or reflections on a subject that interests someone.',
'frijolillo':'A name used for several plants in the legume family, including herbs and trees.',
'aretalogy':'A story recounting extraordinary or miraculous deeds of a deity or hero.',
'ailette':'A small piece of historical armor worn at the shoulder over a coat of mail.',
'colloque':'In French, a conference or meeting for specialists to discuss a subject.',
'matelote':'A fish dish cooked in a seasoned sauce containing wine and onions.',
'hellebore':'A poisonous plant whose roots were historically used as medicine or insecticide.',
'oxyacetylene':'Using oxygen and acetylene to produce a hot metalworking flame.',
'selah':'An uncertain biblical term, perhaps a musical instruction or a call to pause.',
'coulisse':'A side scene or backstage space at the edge of a theater stage.',
'bahr':'A sea, lake, or river, especially in Arabic geographical names.',
'accordatura':'The tuning of a stringed instrument.',
'Mandelbrot set':'Complex numbers c for which iterating z → z² + c from zero stays bounded; the boundary forms a fractal.',
'nidicolous':"Living in another animal's nest, or remaining in one's own after hatching.",
'Oort cloud':'A hypothetical distant cloud of icy bodies surrounding the Solar System.',
'pneumatocyst':'A gas-filled bladder, especially in floating algae.',
'Terre Haute':'A city in western Indiana on the Wabash River.',
'Carrickmacross':'Irish lace often decorated with flower or leaf designs.',
'ni-Vanuatu':'A person from Vanuatu; also, relating to that country.',
'sclaff':'To strike the ground before the ball with a golf club.',
'anabathmoi':'Psalms 120–134, the Songs of Ascents, in Orthodox worship.',
'prêt-à-porter':'Ready-to-wear clothing made in advance in standard sizes.',
'Patripassianism':'A historical theological view that God the Father suffered in the passion of Christ.'
}
for word,text in extra.items():
 if word in byword:audit[byword[word]['id']]={'word':word,'text':text,'reviewer':'root-source-check','reason':'Source clarification, grammar, or independent reference check.'}
pos={'enterprising':'adjective','carnassial':'adjective','Mesopotamian':'adjective','Miranda':'adjective','paraplegic':'adjective','planetesimal':'noun','obeisant':'adjective','biloculine':'adjective','toponymic':'adjective','surrealist':'noun','Doppler':'adjective','Alzheimer':'proper noun','Juglar':'proper noun','parietal':'adjective','prespinous':'adjective','tricenary':'adjective'}
supports={
'ammonite':[('Collins dictionary','https://www.collinsdictionary.com/dictionary/english/ammonite')],
'frater':[('Collins dictionary','https://www.collinsdictionary.com/us/dictionary/english/frater')],
'ad ignorantiam':[('Philosophy reference','https://iep.utm.edu/fallacy/')],
'tricenary':[('Merriam-Webster dictionary','https://www.merriam-webster.com/dictionary/tricenary')],
'prespinous':[('Merriam-Webster dictionary','https://www.merriam-webster.com/dictionary/prescapular')]
}
for word in ['frijolillo','aretalogy','ailette','souari nut']:
 supports[word]=[('Merriam-Webster dictionary','https://www.merriam-webster.com/dictionary/'+word.replace(' ','%20'))]
supports['emphysema']=[('NHLBI lung-health reference','https://www.nhlbi.nih.gov/health/copd')]
supports['Deseret']=[('Utah State Archives','https://archives.utah.gov/research/entities/5548/')]
supports['colloque']=[('Académie française dictionary','https://www.dictionnaire-academie.fr/article/A9C2964')]
supports['matelote']=[('Merriam-Webster dictionary','https://www.merriam-webster.com/dictionary/matelote')]
for word,text in {'souari nut':'The edible souari nut could be pressed to obtain cooking oil.','ailette':"An ailette was worn at the shoulder above the knight's coat of mail.",'colloque':'Researchers attended a French colloque to discuss their new findings.','matelote':'The cook served matelote, with tender fish simmered in a seasoned wine sauce.'}.items():
 example_fixes[byword[word]['id']]={'text':text,'type':'original','credit':'Original example for Molly','license':'Original example wording'}
for id,r in audit.items():
 w=byid[id];ref=sorted(w['refs'],key=lambda x:(sources[x['source']]['year'],sources[x['source']]['category']=='new-2027'),reverse=True)[0];text=r['text'].strip();text=text[:1].upper()+text[1:];text=text if text.endswith(('.','!','?')) else text+'.'
 notes[id]={'glosses':[{'pos':pos.get(w['word'],(w['pos'] or ['word study'])[0]),'text':text,'clue':text}],'title':w['word'],'source':sources[ref['source']]['url']+'#slide=id.'+ref['slide'],'sourceType':'study-note','credit':'Original study wording for Molly, checked against the study context and linked references','license':'Original study wording','editorialStatus':'reviewed_study_note'}
 if w['word'] in supports:notes[id]['supportingSources']=[{'label':a,'url':b} for a,b in supports[w['word']]]
 dictionary[id]=notes[id]
# Remove inherited wiki anchor fragments and label-only pseudo-definitions.
for word in ['stamina','chapiter','ravioli','gaiters']:
 dictionary[byword[word]['id']]['glosses']=dictionary[byword[word]['id']]['glosses'][:1]
for d in dictionary.values():
 clean=[]
 for g in d['glosses']:
  for field in ['text','clue']:
   if field in g:g[field]=re.sub(r'#(?:Noun|Verb|Adjective|Adverb|English|Proper_noun)\b','',g[field]);g[field]=re.sub(r'\s+\(\s*\)','',g[field]);g[field]=re.sub(r'\s+([,.;:])',r'\1',g[field])
  if not re.fullmatch(r'(?:\([^)]*\)\s*)+',g['text']):clean.append(g)
 if clean:d['glosses']=clean
for id,part in reviewed_pos.items():
 for collection in [notes,dictionary]:
  if id in collection:
   for gloss in collection[id]['glosses']:gloss['pos']=part
(R/'data/study-notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n');(R/'data/dictionary.json').write_text(json.dumps(dictionary,ensure_ascii=False,indent=2)+'\n');(R/'research/content-corrections-applied.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
(R/'data/example-batches/review-fixes.json').write_text(json.dumps(example_fixes,ensure_ascii=False,indent=2)+'\n')
counts=collections.Counter()
for id,d in notes.items():
 w=byid[id];ref=next((r for r in w['refs'] if sources[r['source']]['url'] in d['source']),w['refs'][0]);counts[ref['source']]+=sum(len(g['text'].split()) for g in d['glosses'])
print('Applied',len(audit),'reviewed corrections;',len(notes),'total original notes. Max note words for one source deck:',max(counts.values()))
assert max(counts.values())<=200,'Shorten source-based notes for the over-limit deck before delivery.'
