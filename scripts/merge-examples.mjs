import fs from'node:fs';
const root=new URL('../',import.meta.url),load=p=>JSON.parse(fs.readFileSync(new URL(p,root))),words=load('data/words.json'),byId=new Map(words.map(w=>[w.id,w]));
const normalize=s=>s.normalize('NFC').toLocaleLowerCase('en').replace(/[’‘]/g,"'");
const targetPresent=(text,word)=>{const escaped=normalize(word).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');return new RegExp('(?<![\\p{L}\\p{M}\\p{N}])'+escaped+'(?![\\p{L}\\p{M}\\p{N}])','u').test(normalize(text));};
const priority=f=>f==='wiktionary.json'?0:f==='review-fixes.json'?2:f==='editorial.json'?3:1;
let all={};const files=fs.readdirSync(new URL('data/example-batches/',root)).filter(f=>f.endsWith('.json')).sort((a,b)=>priority(a)-priority(b)||a.localeCompare(b));
for(const file of files){let data;try{data=load('data/example-batches/'+file);}catch{throw Error('Example batch is not complete JSON: '+file);}for(const[id,e]of Object.entries(data)){
 if(!byId.has(id))throw Error('Unknown example word '+id);
 if(!e||typeof e.text!=='string')throw Error('Invalid example object: '+file);
 if(all[id]&&!['editorial.json','review-fixes.json'].includes(file))throw Error('Conflicting example batches for '+byId.get(id).word);
 if(/\{\{|\}\}|\[\[|\]\]|<script|#(?:Noun|Verb|English)\b/i.test(e.text))throw Error('Unclean example '+byId.get(id).word);
 all[id]=e;
}}
const seen=new Set();for(const[id,e]of Object.entries(all)){const word=byId.get(id).word;if(e.text.length<12||e.text.length>350||!targetPresent(e.text,word))throw Error('Example is missing its exact word or has invalid text: '+word);const key=normalize(e.text);if(seen.has(key))throw Error('Duplicate example: '+word);seen.add(key);}
fs.writeFileSync(new URL('data/examples.json',root),JSON.stringify(all,null,2)+'\n');
const report={total:words.length,examples:Object.keys(all).length,remaining:words.length-Object.keys(all).length,byLevel:Object.fromEntries([1,2,3].map(l=>[l,{total:words.filter(w=>w.level===l).length,examples:words.filter(w=>w.level===l&&all[w.id]).length}]))};
fs.writeFileSync(new URL('research/example-coverage.json',root),JSON.stringify(report,null,2)+'\n');console.log(report);
