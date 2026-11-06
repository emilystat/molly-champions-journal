export const INTERVALS = [1, 1, 3, 7, 14, 30];
export const DEFAULT_SETTINGS = { name: 'Molly', dailyNew: 10, reviewCap: 20, newLevel: 3, newScope: 'new2027', targetDate: '2027-01-25', accentsOptional: true, voice: '', rate: .85, preferRecordings: true };
export function dayKey(now = new Date()) {
  return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
}
export function addDays(day,n) {
  const [y,m,d] = day.split('-').map(Number); return new Date(Date.UTC(y,m-1,d+n,12)).toISOString().slice(0,10);
}
export function daysBetween(a,b) { return Math.round((Date.parse(`${b}T12:00:00Z`)-Date.parse(`${a}T12:00:00Z`))/86400000); }
export function normalizeAnswer(text, accentsOptional = true) {
  let s = String(text || '').normalize('NFC').trim().replace(/[’‘]/g,"'").replace(/\s+/g,' ').toLocaleLowerCase('en');
  if (accentsOptional) s = s.normalize('NFD').replace(/\p{M}/gu,'');
  return s;
}
export function checkAnswer(word, answer, settings = DEFAULT_SETTINGS) {
  const a = normalizeAnswer(answer,settings.accentsOptional);
  return a.length > 0 && [word.word,...(word.variants||[])].some(w => normalizeAnswer(w,settings.accentsOptional) === a);
}
export function blankProgress(id,day=dayKey()) { return { id, seenDay: day, attempts: 0, correct: 0, misses: 0, skips: 0, assisted: 0, stage: 0, correctDays: 0, lastCreditDay: '', lastDay: '', dueDay: day, star: false, note: '', updatedAt: 0 }; }
export function applyRecall(previous, result, day = dayKey(), now = Date.now()) {
  const p = { ...previous };
  p.attempts++; p.lastDay = day; p.updatedAt = now;
  if (result.skipped) { p.skips++; p.dueDay=addDays(day,1); return p; }
  if (!result.correct) { p.misses++; p.stage=0; p.dueDay=addDays(day,1); return p; }
  p.correct++;
  if (result.assisted) { p.assisted++; p.dueDay=p.stage ? p.dueDay : addDays(day,1); return p; }
  // One credit per local calendar day; a rapid retry cannot simulate retention.
  if (p.lastCreditDay !== day) {
    p.stage = Math.min(5,p.stage+1); p.correctDays++; p.lastCreditDay=day;
    p.dueDay = addDays(day,INTERVALS[p.stage]);
  }
  return p;
}
export function wordStatus(p,day=dayKey()) {
  if (!p || !p.attempts) return 'new';
  if (p.dueDay <= day) return 'due';
  if (p.stage>=3 && p.correctDays>=3) return 'secure';
  return 'learning';
}
export function totals(words,progress,day=dayKey()) {
  const result={new:0,due:0,learning:0,secure:0,starred:0,tricky:0,todayNew:0};
  for (const w of words) { const p=progress[w.id];result[wordStatus(p,day)]++;if(p?.star)result.starred++;if(p && p.misses>0 && p.stage<3)result.tricky++;if(p?.attempts && p.seenDay===day)result.todayNew++; }
  return result;
}
function seededOrder(items,seed) { const hash=s=>{let n=2166136261;for(const c of s){n^=c.charCodeAt(0);n=Math.imul(n,16777619);}return n>>>0;};return [...items].sort((a,b)=>hash(seed+a.id)-hash(seed+b.id)); }
export function selectWords(words,progress,config,day=dayKey()) {
  let pool=words.filter(w => (!config.level || w.level===Number(config.level)) && (!config.source || w.refs.some(r=>r.source===config.source)) && (!config.new2027 || w.new2027));
  if (config.focus==='tricky') pool=pool.filter(w=>progress[w.id]?.misses>0 && progress[w.id].stage<3 || progress[w.id]?.star);
  if (config.focus==='starred') pool=pool.filter(w=>progress[w.id]?.star);
  if (config.focus==='due') pool=pool.filter(w=>wordStatus(progress[w.id],day)==='due');
  const sorted=seededOrder(pool,config.seed||`${day}:${config.mode}`);
  if (config.focus==='new') return sorted.filter(w=>!progress[w.id]?.attempts).slice(0,config.size);
  return sorted.sort((a,b)=>{
    const rank=w=>{const p=progress[w.id];return p?.dueDay<=day&&p.attempts?0:!p?.attempts?1:2;};return rank(a)-rank(b);
  }).slice(0,config.size);
}
export function learningPool(words,settings) {
  return words.filter(w=>w.level<=settings.newLevel && (settings.newScope==='new2027'?w.new2027:settings.newScope==='current'?w.current:true));
}
export function dailyQueue(words,progress,settings,day=dayKey()) {
  const stats=totals(words,progress,day);
  const due=words.filter(w=>progress[w.id]?.attempts&&progress[w.id].dueDay<=day).sort((a,b)=>progress[a.id].dueDay.localeCompare(progress[b.id].dueDay)||progress[b.id].misses-progress[a.id].misses).slice(0,settings.reviewCap);
  const fresh=learningPool(words,settings).filter(w=>!progress[w.id]?.attempts).slice(0,Math.max(0,settings.dailyNew-stats.todayNew));
  const queue=[];while(due.length||fresh.length){if(due.length)queue.push(due.shift());if(due.length)queue.push(due.shift());if(fresh.length)queue.push(fresh.shift());}
  return queue;
}
export function sessionStep(s,index) { const assisted=s.mode==='learn'||s.mode==='daily'&&(s.studyIds||[]).includes(s.ids[index]);return {phase:assisted?'study':'answer',assisted}; }
export function createSession(ids,mode='practice',label='A little word practice',now=Date.now(),studyIds=[]) {
  return {id:crypto.randomUUID(),ids:[...ids],mode,label,index:0,studyIds:[...studyIds],...sessionStep({ids,mode,studyIds},0),responses:[],draft:'',status:'active',paused:false,startedAt:now,updatedAt:now,elapsedMs:0,resumedAt:now};
}
export function elapsed(s,now=Date.now()) {return s.elapsedMs+(s.status==='active'&&!s.paused&&s.resumedAt?Math.max(0,now-s.resumedAt):0);}
export function timeText(ms){const s=Math.floor(ms/1000);return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;}
const validDay=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\d$/.test(s)&&!Number.isNaN(Date.parse(`${s}T12:00:00Z`))&&new Date(`${s}T12:00:00Z`).toISOString().slice(0,10)===s;
export function validateBackup(value,knownIds) {
  if (!value || value.kind!=='molly-champions-backup' || value.version!==1 || !Array.isArray(value.progress) || !Array.isArray(value.sessions)) throw Error('This is not a Words of the Champions backup.');
  if(value.progress.length>knownIds.size || value.sessions.length>2000)throw Error('This backup is too large.');
  const seen=new Set();
  for(const p of value.progress){
    if(!p || !knownIds.has(p.id)||seen.has(p.id))throw Error('The backup contains unknown or repeated word records.');seen.add(p.id);
    for(const k of ['attempts','correct','misses','skips','assisted','stage','correctDays'])if(!Number.isSafeInteger(p[k])||p[k]<0)throw Error('The backup contains invalid practice counts.');
    if(p.stage>5||p.correct>p.attempts||p.assisted>p.correct||p.correct+p.misses+p.skips!==p.attempts||p.correctDays>p.correct||typeof p.star!=='boolean'||typeof p.note!=='string'||p.note.length>2000||!Number.isSafeInteger(p.updatedAt)||p.updatedAt<0||!validDay(p.seenDay)||!validDay(p.dueDay)||p.lastDay&&!validDay(p.lastDay)||p.lastCreditDay&&!validDay(p.lastCreditDay))throw Error('The backup contains invalid word progress.');
  }
  const sessions=new Set();let active=0;
  for(const s of value.sessions){
    if(!s||typeof s.id!=='string'||! /^[A-Za-z0-9_-]{1,100}$/.test(s.id)||sessions.has(s.id)||!Array.isArray(s.ids)||s.ids.length>200||!s.ids.length||new Set(s.ids).size!==s.ids.length||s.ids.some(id=>!knownIds.has(id))||!['learn','practice','quiz','daily'].includes(s.mode)||!['active','complete'].includes(s.status)||!Number.isSafeInteger(s.index)||s.index<0||s.index>=s.ids.length||!Array.isArray(s.responses)||!Number.isFinite(s.elapsedMs)||s.elapsedMs<0||!Number.isFinite(s.updatedAt)||!Number.isFinite(s.startedAt)||typeof s.label!=='string'||s.label.length>200||!['study','answer','feedback'].includes(s.phase)||typeof s.paused!=='boolean'||typeof s.assisted!=='boolean'||typeof s.draft!=='string'||s.draft.length>200||!(s.resumedAt===null||Number.isFinite(s.resumedAt)))throw Error('The backup contains an invalid practice session.');
    if(s.studyIds!==undefined&&(!Array.isArray(s.studyIds)||s.studyIds.some(id=>!s.ids.includes(id))||new Set(s.studyIds).size!==s.studyIds.length))throw Error('The backup contains an invalid study queue.');
    const expected=s.index+(s.phase==='feedback'?1:0);
    if(s.responses.length!==expected||s.responses.some((r,i)=>r.wordId!==s.ids[i]||typeof r.answer!=='string'||r.answer.length>200||typeof r.correct!=='boolean'||typeof r.assisted!=='boolean'||typeof r.skipped!=='boolean'||r.correct&&r.skipped||!Number.isFinite(r.at)))throw Error('The backup contains inconsistent saved answers.');
    if(s.status==='active'&&++active>1)throw Error('A backup may contain only one unfinished practice.');
    sessions.add(s.id);
  }
  const settings={...DEFAULT_SETTINGS,...value.settings};
  if(!Number.isInteger(settings.dailyNew)||settings.dailyNew<1||settings.dailyNew>100||!Number.isInteger(settings.reviewCap)||settings.reviewCap<1||settings.reviewCap>100||!['new2027','current','all'].includes(settings.newScope)||![1,2,3].includes(settings.newLevel)||typeof settings.name!=='string'||settings.name.length>40||settings.targetDate&&!validDay(settings.targetDate)||typeof settings.accentsOptional!=='boolean'||typeof settings.preferRecordings!=='boolean'||typeof settings.voice!=='string'||settings.voice.length>300||!Number.isFinite(settings.rate)||settings.rate<.5||settings.rate>1.3)throw Error('The backup contains invalid settings.');
  return {...value,settings};
}

// Match answer spellings without exposing accent/case variants in recall clues.
export function maskSpelling(text,word){
  text=String(text||'');let folded='',map=[];
  const fold=s=>s.normalize('NFD').replace(/\p{M}/gu,'').toLocaleLowerCase('en').replace(/[’‘]/g,"'").replace(/[‐‑‒–—]/g,'-');
  for(const m of text.matchAll(/\P{M}\p{M}*|\p{M}+/gu)){
    let part=fold(m[0]);if(/\s/u.test(part))part=' ';
    if(part===' '&&folded.endsWith(' ')){map[map.length-1].end=m.index+m[0].length;continue;}
    for(let i=0;i<part.length;i++)map.push({start:m.index,end:m.index+m[0].length});folded+=part;
  }
  const ranges=[];
  for(const spelling of [word.word,...(word.variants||[])]){
    const target=fold(spelling).replace(/\s+/g,' ').trim();if(!target)continue;
    for(let i=folded.indexOf(target);i>=0;i=folded.indexOf(target,i+1)){
      let start=map[i].start,end=map[i+target.length-1].end;
      // Do not leave inflection letters attached to a masked answer.
      while(start>0&&/[\p{L}\p{M}]/u.test(text[start-1]))start--;
      while(end<text.length&&/[\p{L}\p{M}]/u.test(text[end]))end++;
      ranges.push([start,end]);
    }
  }
  const merged=[];for(const r of ranges.sort((a,b)=>a[0]-b[0])){const last=merged.at(-1);if(last&&r[0]<=last[1])last[1]=Math.max(last[1],r[1]);else merged.push([...r]);}
  let out='',cursor=0;for(const[start,end]of merged){out+=text.slice(cursor,start)+'____';cursor=end;}return out+text.slice(cursor);
}
