import fs from 'node:fs';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
const root = new URL('../', import.meta.url);
const require = createRequire(import.meta.url);
const reference = process.argv[2];
if (!reference) throw new Error('Pass the read-only spelling reference checkout path.');
const ownWords = [...require(`${reference}/words-2026-27.js`), ...require(`${reference}/words-2026-27-onebee.js`)];
const helpers = require(`${reference}/audio.js`);
const audioText = fs.readFileSync(`${reference}/audio-map.js`, 'utf8');
const audioMap = JSON.parse(audioText.slice(audioText.indexOf('{'), audioText.lastIndexOf('}') + 1));
const audit = JSON.parse(fs.readFileSync(new URL('research/deck-audit.json', root)));
const decks = audit.decks.filter(d => d.kind === 'champions');
const key = s => s.normalize('NFC').replace(/’/g, "'").replace(/\s+/g, ' ').trim().toLocaleLowerCase('en');
const own = new Map(ownWords.map(w => [key(w.word), w]));
const index = new Map();
for (const d of decks) for (const [i, item] of d.words.entries()) {
  if (item.confidence === 'needs-review') continue;
  const k = key(item.display);
  let w = index.get(k);
  if (!w) {
    w = { id: `w-${crypto.createHash('sha256').update(k).digest('hex').slice(0, 14)}`, word: item.display, level: d.level, refs: [], origins: [], pos: [], variants: [], current: false, new2027: false };
    index.set(k, w);
  }
  w.level = Math.min(w.level, d.level);
  w.current ||= d.year === 2027;
  w.new2027 ||= d.year === 2027 && d.set.endsWith('N');
  w.refs.push({ source: d.key, slide: item.slide, position: i + 1 });
  if (item.audio && !w.sourceAudio) w.sourceAudio = { fileId: item.audio.id, source: d.key, url: `https://drive.usercontent.google.com/download?id=${item.audio.id}&export=download`, credit: 'Hoover 206 study recording' };
  if (item.origin && !w.origins.includes(item.origin)) w.origins.push(item.origin);
  if (item.pos && !w.pos.includes(item.pos)) w.pos.push(item.pos);
}
let enriched = 0, recorded = 0;
const words = [...index.values()];
for (const w of words) {
  const old = own.get(key(w.word));
  if (old) {
    w.details = Object.fromEntries(['definition', 'sentence', 'sounds', 'parts', 'tip', 'flag', 'confuse', 'say'].filter(k => old[k]).map(k => [k, old[k]]));
    w.variants = old.alts || [];
    enriched++;
  }
  const rec = audioMap[helpers.normalizeWordKey(w.word)];
  if (rec && rec.page && rec.author && rec.license && helpers.rankRecordingFile(rec.file, w.word, { alts: w.variants, pos: w.pos.join(' ') }) >= 5) {
    w.recording = rec;
    recorded++;
  }
}
words.sort((a,b) => a.level - b.level || Number(b.new2027) - Number(a.new2027) || Number(b.current) - Number(a.current) || a.word.localeCompare(b.word));
const sources = decks.map(({ words, kind, ...d }) => ({ ...d, count: words.length, category: d.year === 2027 ? d.set.endsWith('N') ? 'new-2027' : 'repeat-2027' : 'carryover' }));
const manifest = { version: 1, season: 2027, checkedOn: '2026-11-06', officialListVerified: false,
  title: 'Hoover Words of the Champions practice collection', sourceIndex: 'https://hoover206.wixsite.com/spelling/copy-of-2025-words-1',
  wordCount: words.length, sourceCount: sources.length, new2027Count: words.filter(w => w.new2027).length,
  currentSourceCount: words.filter(w => w.current).length, enrichedCount: enriched, recordingCount: words.filter(w=>w.sourceAudio||w.recording).length,
  levels: Object.fromEntries([1,2,3].map(l => [l, words.filter(w => w.level === l).length])),
  sourceYears: [...new Set(sources.map(s => s.year))].sort(),
  caveat: 'The linked page includes older carryover sets. This collection is not yet reconciled against the official 4,000-word 2027 guide.',
  metadataCredit: 'Selected word explanations were written for Emily’s school spelling site and reused unchanged. Original source slides provide the remaining study explanations.',
  audioCredit: 'Selected exact-match recordings from Wikimedia Commons; speaker and license are credited on the word card. Other words use a clearly identified computer voice.',
  sources };
fs.writeFileSync(new URL('data/words.json', root), JSON.stringify(words));
fs.writeFileSync(new URL('data/manifest.json', root), JSON.stringify(manifest));
fs.writeFileSync(new URL('SOURCE_AUDIT.md', root), `# Word-bank audit\n\nChecked November 6, 2026.\n\n- ${audit.decks.length} linked study decks read; ${audit.errors.length} unavailable.\n- ${decks.length} Words of the Champions decks included; 9 school decks kept out of this separate bank.\n- ${decks.reduce((n,d)=>n+d.words.length,0)} word occurrences; **${words.length} distinct spellings** after merging repeated spellings.\n- Levels: ${JSON.stringify(manifest.levels)}.\n- ${manifest.new2027Count} words in explicitly new 2027 decks; ${manifest.currentSourceCount} words appear in a deck titled for 2027.\n- Source title years: ${manifest.sourceYears.join(', ')}. Older entries remain labelled as carryover.\n- ${enriched} words reuse Emily’s own detailed school-site notes; ${manifest.recordingCount} have matching source recording links (playback availability can vary). Every word has a source-study link.\n- 15 labels needed text-based checking because their recording filename was absent or misspelled. Source text, not the audio filename, determines spelling.\n\n## Current limitation\n\n${manifest.caveat} Do not advertise this as an exact official 2027 list. Do not add filler words to reach a target count. The source audit and stable spelling IDs allow reconciliation later without losing progress.\n\nDefinitions, example sentences, illustrations and audio from the Hoover slides are linked, not republished. Publicly downloaded source pages remain in the ignored research folder.\n`);
console.log(JSON.stringify({words:words.length,sources:sources.length,levels:manifest.levels,new2027:manifest.new2027Count,currentSources:manifest.currentSourceCount,enriched,recorded}));
