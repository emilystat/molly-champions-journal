import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULT_SETTINGS,blankProgress,applyRecall,wordStatus,checkAnswer,dayKey,addDays,dailyQueue,learningPool,selectWords,createSession,sessionStep,validateBackup,maskSpelling} from '../lib/core.js';
const word=(id,level=1)=>({id,word:id,variants:[],level,refs:[{source:'set-a'}],new2027:level===1});
const day='2026-11-06';
test('answer checking preserves meaningful punctuation and accepts only listed variants',()=>{
 const w={word:'piñata',variants:['pinata']};assert(checkAnswer(w,' PIÑATA '));assert(!checkAnswer(w,'pinada'));
 assert(checkAnswer({word:'co-operate',variants:['cooperate']},'cooperate'));
 assert(!checkAnswer({word:'cul-de-sac',variants:[]},'cul de sac'));
 assert(checkAnswer({word:"point d’appui",variants:[]},"point d'appui"));
 assert(!checkAnswer({word:'café',variants:[]},'cafe',{...DEFAULT_SETTINGS,accentsOptional:false}));
});
test('independent recall advances once per calendar day, not with rapid repetitions',()=>{
 let p=applyRecall(blankProgress('a',day),{correct:true},day,1);assert.equal(p.stage,1);assert.equal(p.dueDay,'2026-11-07');
 p=applyRecall(p,{correct:true},day,2);assert.equal(p.stage,1);assert.equal(p.correctDays,1);
 p=applyRecall(p,{correct:true},'2026-11-07',3);assert.equal(p.stage,2);assert.equal(p.dueDay,'2026-11-10');
 p=applyRecall(p,{correct:true},'2026-11-10',4);assert.equal(p.stage,3);assert.equal(wordStatus(p,'2026-11-10'),'secure');
});
test('assisted spelling and skipped words cannot create secure recall',()=>{
 let p=applyRecall(blankProgress('a',day),{correct:true,assisted:true},day,1);assert.equal(p.stage,0);assert.equal(p.assisted,1);assert.equal(p.correctDays,0);
 p=applyRecall(p,{correct:false,skipped:true},day,2);assert.equal(p.misses,0);assert.equal(p.skips,1);
});
test('a miss returns a previously secure word to early review',()=>{
 const p=applyRecall({...blankProgress('a',day),stage:5,correctDays:5,attempts:5,correct:5},{correct:false},day,2);assert.equal(p.stage,0);assert.equal(p.dueDay,'2026-11-07');assert.equal(wordStatus(p,day),'learning');
});
test('calendar-day intervals do not depend on daylight-saving hour lengths',()=>{assert.equal(addDays('2026-11-01',1),'2026-11-02');assert.equal(addDays('2026-03-07',2),'2026-03-09');});
test('daily queue caps reviews and new words without duplicates',()=>{
 const words=Array.from({length:30},(_,i)=>word('w'+i)),progress={};for(const w of words.slice(0,12))progress[w.id]={...blankProgress(w.id,'2026-10-01'),attempts:1,correct:1,dueDay:'2026-11-05'};
 const q=dailyQueue(words,progress,{...DEFAULT_SETTINGS,dailyNew:4,reviewCap:5},day);assert.equal(q.length,9);assert.equal(new Set(q.map(w=>w.id)).size,9);assert.equal(q.filter(w=>!progress[w.id]).length,4);
});
test('subject-free filters combine level, source, focus, and current-season additions',()=>{
 const words=[word('a'),word('b',2),{...word('c'),refs:[{source:'set-b'}]}];assert.deepEqual(selectWords(words,{}, {level:1,source:'set-a',new2027:true,size:10,mode:'learn'},day).map(w=>w.id),['a']);assert.equal(selectWords(words,{}, {focus:'tricky',size:5,mode:'practice'},day).length,0);
});
test('backup validation accepts intact progress and rejects unknown words or corrupt counts',()=>{
 const p=applyRecall(blankProgress('a',day),{correct:true},day,2),b={kind:'molly-champions-backup',version:1,settings:DEFAULT_SETTINGS,progress:[p],sessions:[]};assert.equal(validateBackup(b,new Set(['a'])).progress.length,1);assert.throws(()=>validateBackup(b,new Set(['b'])));assert.throws(()=>validateBackup({...b,progress:[{...p,correct:9}]},new Set(['a'])));assert.throws(()=>validateBackup({...b,progress:[{...p,dueDay:'2026-02-31'}]},new Set(['a'])));
});
test('backup validation rejects damaged sessions before any storage mutation',()=>{
 const b={kind:'molly-champions-backup',version:1,settings:DEFAULT_SETTINGS,progress:[],sessions:[{id:'s',ids:['unknown'],index:0,mode:'quiz',status:'active',responses:[],elapsedMs:0,updatedAt:1,startedAt:1}]};assert.throws(()=>validateBackup(b,new Set(['a'])));
});

test('a January plan can focus on new-season words without excluding older words from due review',()=>{
 const words=[word('fresh'),{...word('older'),new2027:false},word('stretch',3)],progress={older:{...blankProgress('older','2026-10-01'),attempts:1,correct:1,dueDay:day}};
 assert.deepEqual(learningPool(words,DEFAULT_SETTINGS).map(w=>w.id),['fresh']);
 assert.deepEqual(dailyQueue(words,progress,{...DEFAULT_SETTINGS,dailyNew:2},day).map(w=>w.id),['older','fresh']);
 assert.equal(learningPool(words,{...DEFAULT_SETTINGS,newScope:'all'}).length,3);
});

test('daily sessions introduce unseen words with a study card while due reviews stay independent',()=>{
 const s=createSession(['fresh','review','fresh2'],'daily','Daily',1,['fresh','fresh2']);
 assert.equal(s.phase,'study');assert.equal(s.assisted,true);
 assert.deepEqual(sessionStep(s,1),{phase:'answer',assisted:false});
 assert.deepEqual(sessionStep(s,2),{phase:'study',assisted:true});
 assert.equal(createSession(['a'],'quiz','Quiz',1).phase,'answer');
});

test('recall clues mask accent variants, origin spellings, phrases and inflections',()=>{
 assert.equal(maskSpelling('From Latin princeps.',{word:'princeps'}),'From Latin ____.');
 assert.equal(maskSpelling('Italian da capo means again.',{word:'da capo'}),'Italian ____ means again.');
 assert.equal(maskSpelling('A danzón from Gruyères.',{word:'danzon'}),'A ____ from Gruyères.');
 assert.equal(maskSpelling('A cheese from Gruyères.',{word:'Gruyere'}),'A cheese from ____.');
 assert.equal(maskSpelling('Two braced arms.',{word:'brace'}),'Two ____ arms.');
 assert.equal(maskSpelling('CAFE\u0301 café',{word:'café'}),'____ ____');
});
