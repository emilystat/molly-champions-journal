import test from 'node:test';import assert from 'node:assert/strict';import{IDBFactory}from'fake-indexeddb';import{StudyDB}from'../lib/db.js';import{createSession,validateBackup,DEFAULT_SETTINGS}from'../lib/core.js';
function origin(){globalThis.indexedDB=new IDBFactory();}
test('simultaneous answers in two clients commit exactly one result',async()=>{origin();const a=await new StudyDB().open(),b=await new StudyDB().open();try{const s=await a.start(createSession(['a'],'practice'));const results=await Promise.allSettled([a.answer(s.id,0,{answer:'a',correct:true,assisted:false,skipped:false}),b.answer(s.id,0,{answer:'a',correct:true,assisted:false,skipped:false})]);assert.equal(results.filter(r=>r.status==='fulfilled').length,1);const snap=await a.snapshot();assert.equal(snap.progress.a.attempts,1);assert.equal(snap.sessions[0].responses.length,1);}finally{a.close();b.close();}});
test('backup round trip keeps answers, notes and stars and rejects corruption before changing records',async()=>{origin();const a=await new StudyDB().open();let backup;try{const s=await a.start(createSession(['a'],'practice'));await a.answer(s.id,0,{answer:'a',correct:true,assisted:false,skipped:false});await a.advance(s.id,0);await a.wordNote('a',{note:'A memory clue.',star:true});backup=await a.backup();}finally{a.close();}origin();const b=await new StudyDB().open();try{await b.restore(backup,new Set(['a']));let snap=await b.snapshot();assert.equal(snap.progress.a.attempts,1);assert.equal(snap.progress.a.star,true);assert.equal(snap.progress.a.note,'A memory clue.');assert.equal(snap.sessions[0].status,'complete');await assert.rejects(()=>b.restore({...backup,progress:[{...backup.progress[0],correct:99}]},new Set(['a'])));assert.equal((await b.snapshot()).progress.a.correct,1);await b.restore(backup,new Set(['a']));assert.equal((await b.snapshot()).progress.a.attempts,1);}finally{b.close();}});
test('reopening a committed quiz answer advances once and parks the next question',async()=>{origin();const a=await new StudyDB().open();try{const s=await a.start(createSession(['a','b'],'quiz'));await a.answer(s.id,0,{answer:'a',correct:true,assisted:false,skipped:false});await a.recoverOnOpen();const snap=await a.snapshot(),next=snap.sessions[0];assert.equal(next.index,1);assert.equal(next.phase,'answer');assert.equal(next.responses.length,1);assert.equal(next.paused,true);assert.equal(next.resumedAt,null);await a.recoverOnOpen();assert.equal((await a.snapshot()).progress.a.attempts,1);}finally{a.close();}});
test('settings can create a 200-word daily session and its own backup remains valid',async()=>{const ids=Array.from({length:200},(_,i)=>'w'+i),s=createSession(ids,'daily','Maximum daily plan',1,ids.slice(100)),backup={kind:'molly-champions-backup',version:1,settings:{...DEFAULT_SETTINGS,dailyNew:100,reviewCap:100},progress:[],sessions:[s]};assert.equal(validateBackup(backup,new Set(ids)).sessions[0].ids.length,200);assert.throws(()=>validateBackup({...backup,sessions:[{...s,phase:'feedback'}]},new Set(ids)));assert.throws(()=>validateBackup({...backup,sessions:[s,{...s,id:'other'}]},new Set(ids)));});

test('a stale study action cannot mutate a completed session or corrupt its backup',async()=>{origin();const a=await new StudyDB().open(),b=await new StudyDB().open();try{const s=await a.start(createSession(['a'],'learn'));await b.finish(s.id);await assert.rejects(()=>a.transitionPhase(s.id,0,'study','answer'));const backup=await a.backup();assert.equal(validateBackup(backup,new Set(['a'])).sessions[0].phase,'study');}finally{a.close();b.close();}});
test('restored session IDs reject HTML attribute payloads before persistence',()=>{const s=createSession(['a']);assert.throws(()=>validateBackup({kind:'molly-champions-backup',version:1,settings:DEFAULT_SETTINGS,progress:[],sessions:[{...s,id:'quote"inside'}]},new Set(['a'])));});

test('timer checkpoints preserve elapsed work without counting an hour away after reopening',async()=>{origin();const a=await new StudyDB().open();try{const before=Date.now(),s=createSession(['a'],'practice','Timer',before-35000);await a.start(s);await a.checkpoint(s.id,0);let saved=(await a.snapshot()).sessions[0];assert(saved.elapsedMs>=35000);await a.updateSession(s.id,x=>({...x,updatedAt:before-3600000,resumedAt:before-3600000}));/* updateSession stamps writes; simulate an old durable record in the test fixture */const tx=a.db.transaction('sessions','readwrite');saved={...saved,updatedAt:before-3600000,resumedAt:before-3600000};tx.objectStore('sessions').put(saved);await new Promise((resolve,reject)=>{tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});await a.recoverOnOpen();const reopened=(await a.snapshot()).sessions[0];assert.equal(reopened.paused,true);assert(reopened.elapsedMs<40000);}finally{a.close();}});

test('quiz recovery freezes the durable clock before advancing final or non-final feedback',async()=>{
 const realNow=Date.now;let clock=1800000000000;Date.now=()=>clock;
 try{
  for(const ids of [['a','b'],['a']]){
   origin();const a=await new StudyDB().open();
   try{
    const s=await a.start(createSession(ids,'quiz','Interrupted quiz',clock));
    clock+=5000;await a.answer(s.id,0,{answer:'a',correct:true,assisted:false,skipped:false});
    assert.equal((await a.session(s.id)).elapsedMs,5000);
    // Simulate the browser stopping after the answer transaction, before UI advance.
    clock+=3600000;await a.recoverOnOpen();let saved=await a.session(s.id);
    assert.equal(saved.elapsedMs,5000,'closed-browser time must not enter the quiz total');
    assert.equal(saved.index,ids.length===1?0:1);
    assert.equal(saved.status,ids.length===1?'complete':'active');
    assert.equal(saved.paused,true);assert.equal(saved.resumedAt,null);
    assert.equal(saved.responses.length,1);
    clock+=3600000;await a.recoverOnOpen();saved=await a.session(s.id);
    assert.equal(saved.elapsedMs,5000,'repeated recovery must remain idempotent');
    assert.equal((await a.snapshot()).progress.a.attempts,1);
    assert.equal(validateBackup(await a.backup(),new Set(ids)).sessions[0].elapsedMs,5000);
   }finally{a.close();}
  }
 }finally{Date.now=realNow;}
});
