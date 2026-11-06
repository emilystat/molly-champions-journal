import {DEFAULT_SETTINGS,blankProgress,applyRecall,dayKey,elapsed,sessionStep,validateBackup} from './core.js';
const NAME='molly-champions-2027-v1';
const request=r=>new Promise((resolve,reject)=>{r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
const complete=t=>new Promise((resolve,reject)=>{t.oncomplete=resolve;t.onerror=()=>reject(t.error);t.onabort=()=>reject(t.error||Error('The save was interrupted.'));});
export class StudyDB {
  constructor(){this.channel=typeof BroadcastChannel!=='undefined'?new BroadcastChannel(NAME):null;this.onChange=()=>{};if(this.channel)this.channel.onmessage=()=>this.onChange();}
  async open(){this.db=await new Promise((resolve,reject)=>{const r=indexedDB.open(NAME,1);r.onupgradeneeded=()=>{for(const name of ['progress','sessions','settings'])r.result.createObjectStore(name,{keyPath:'id'});};r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.onblocked=()=>reject(Error('Close other copies of this site, then reload.'));});this.db.onversionchange=()=>this.db.close();return this;}
  close(){this.channel?.close();this.db?.close();}
  async recoverOnOpen(){
    const snap=await this.snapshot();let active=snap.sessions.find(s=>s.status==='active');
    // Freeze from the durable timestamps before advancing interrupted quiz feedback.
    // Advancing first would count time away or replace the old checkpoint timestamp.
    if(active?.status==='active'&&!active.paused)active=await this.updateSession(active.id,s=>s.status==='active'?{...s,elapsedMs:Date.now()-s.updatedAt<=30000?elapsed(s):s.elapsedMs,paused:true,resumedAt:null}:s);
    if(active?.mode==='quiz'&&active.phase==='feedback')await this.advance(active.id,active.index);
  }
  async snapshot(){const t=this.db.transaction(['progress','sessions','settings'],'readonly'),done=complete(t);const [p,s,c]=await Promise.all(['progress','sessions','settings'].map(n=>request(t.objectStore(n).getAll())));await done;return {progress:Object.fromEntries(p.map(x=>[x.id,x])),sessions:s.sort((a,b)=>b.startedAt-a.startedAt),settings:{...DEFAULT_SETTINGS,...c.find(x=>x.id==='preferences')?.value}};}
  async session(id){return request(this.db.transaction('sessions','readonly').objectStore('sessions').get(id));}
  async start(s){const t=this.db.transaction('sessions','readwrite'),done=complete(t),st=t.objectStore('sessions');const all=await request(st.getAll());if(all.some(x=>x.status==='active')){t.abort();await done.catch(()=>{});throw Error('A practice session is already open. Continue or finish it before starting another.');}st.put(s);await done;this.notify();return s;}
  async updateSession(id,change){const t=this.db.transaction('sessions','readwrite'),done=complete(t),st=t.objectStore('sessions');const s=await request(st.get(id));if(!s){t.abort();await done.catch(()=>{});throw Error('That session is no longer available.');}const next=change(s);next.updatedAt=Date.now();st.put(next);await done;this.notify();return next;}
  async transitionPhase(id,index,from,to){return this.updateSession(id,s=>{if(s.status!=='active'||s.paused||s.index!==index||s.phase!==from||s.responses.some(r=>r.wordId===s.ids[index]))throw Error('This question changed in another tab. Reload its saved state.');return {...s,phase:to,assisted:true};});}
  async answer(id,expectedIndex,result){const t=this.db.transaction(['progress','sessions'],'readwrite'),done=complete(t),ss=t.objectStore('sessions'),ps=t.objectStore('progress');const s=await request(ss.get(id));
    if(!s||s.status!=='active'||s.paused||s.index!==expectedIndex||s.responses.some(r=>r.wordId===s.ids[expectedIndex])){t.abort();await done.catch(()=>{});throw Error('This question has changed in another tab. Reload the saved session before answering.');}
    const wordId=s.ids[expectedIndex],old=await request(ps.get(wordId));const p=applyRecall(old||blankProgress(wordId),{...result,assisted:s.assisted||result.assisted},dayKey());if(!old?.attempts)p.seenDay=dayKey();ps.put(p);
    s.responses.push({...result,assisted:s.assisted||result.assisted,wordId,at:Date.now()});s.phase='feedback';s.draft='';s.elapsedMs=elapsed(s);s.resumedAt=Date.now();s.updatedAt=Date.now();ss.put(s);await done;this.notify();return s;}
  async advance(id,index){return this.updateSession(id,s=>{if(s.index!==index||!s.responses.some(r=>r.wordId===s.ids[index]))throw Error('This session changed. Reload its latest saved state.');if(s.index===s.ids.length-1){s.elapsedMs=elapsed(s);s.status='complete';s.resumedAt=null;s.endedAt=Date.now();}else{s.index++;Object.assign(s,sessionStep(s,s.index));s.draft='';}return s;});}
  async finish(id){return this.updateSession(id,s=>({...s,elapsedMs:elapsed(s),status:'complete',endedAt:Date.now(),resumedAt:null}));}
  async checkpoint(id,index){return this.updateSession(id,s=>s.status==='active'&&!s.paused&&s.index===index?{...s,elapsedMs:elapsed(s),resumedAt:Date.now()}:s);}
  async pause(id,paused){return this.updateSession(id,s=>{if(s.status!=='active')return s;return {...s,elapsedMs:elapsed(s),paused,resumedAt:paused?null:Date.now()};});}
  async wordNote(id,patch){const t=this.db.transaction('progress','readwrite'),done=complete(t),st=t.objectStore('progress');const p=await request(st.get(id))||blankProgress(id);st.put({...p,...patch,updatedAt:Date.now()});await done;this.notify();}
  async preferences(value){const t=this.db.transaction('settings','readwrite'),done=complete(t);t.objectStore('settings').put({id:'preferences',value});await done;this.notify();}
  async backup(){const snap=await this.snapshot();return {kind:'molly-champions-backup',version:1,exportedAt:new Date().toISOString(),settings:snap.settings,progress:Object.values(snap.progress),sessions:snap.sessions};}
  async restore(raw,ids){const backup=validateBackup(raw,ids);const t=this.db.transaction(['progress','sessions','settings'],'readwrite'),done=complete(t);for(const name of ['progress','sessions']){const st=t.objectStore(name);const current=await request(st.getAll());const lookup=new Map(current.map(x=>[x.id,x]));const hasActive=current.some(s=>s.status==='active');for(const item of backup[name]){const old=lookup.get(item.id);if(name==='sessions'&&item.status==='active'&&(hasActive||current.length))continue;if(!old||item.updatedAt>old.updatedAt){st.put(name==='sessions'&&item.status==='active'?{...item,paused:true,resumedAt:null}:item);}}}
    const prefs=t.objectStore('settings');if(!await request(prefs.get('preferences')))prefs.put({id:'preferences',value:backup.settings});await done;this.notify();return backup.progress.length;}
  notify(){this.channel?.postMessage('saved');}
}
