# Molly’s Word Journal — Words of the Champions

A separate practice website for Molly’s late-January 2027 bee. Her existing school spelling site, older Words of Champions repository, and AMC8 projects are unchanged. No account service or online progress database is connected.

## Open the website

**[Molly’s Word Journal](https://emilystat.github.io/molly-champions-journal/)**

Progress saves in the browser on the current device. Use Settings → Download backup to keep a copy or move progress between browsers/devices. Local-preview progress can be transferred to the published website using a backup.

The site is published from this repository through GitHub Pages; the local launcher below remains available.

## Open the local site

Double-click **Start Word Journal.command**, then open **http://127.0.0.1:5182/** in Chrome. Keep the Terminal window open while practising. Press Control-C there to stop it. The launcher needs Python 3 (already available on this Mac).

**Molly-Word-Journal.html** is an additional self-contained build with the app and word library in one file. Its rendering has been checked over HTTP; opening `file://` directly was blocked by the automation browser’s URL policy, so local-file persistence has not been verified. The local server is the recommended, tested route.

Use **Settings → Download backup** regularly. Source recordings and original study slides need internet access. Keep using the same browser and local address for progress.

For development, use Python 3 from this folder:

```sh
python3 -m http.server 5182 --bind 127.0.0.1
```

Then open http://127.0.0.1:5182/ in Chrome. Stop the server with Control-C. This server is bound to your computer only. **The server address and the standalone file have separate browser storage**; use a backup to transfer work rather than expecting it to appear automatically.

## The learning plan

- **One Bee, Two Bee and Three Bee** have their own home-page entry, practice filter, word-library filter and progress totals.
- Start with the **505 explicitly new 2027 words**, at **10 new words/day plus up to 20 due reviews**. A first pass takes about 51 days. All due reviews remain eligible even when the new-word path is narrower.
- January 25 is an **adjustable estimate for “late January,” not the confirmed bee date**. Settings lets you change it and choose the full collection or 2027-titled decks. The progress page shows the workload for the chosen path and for the entire bank.
- New daily words first show a study card; due reviews ask for independent recall. Also choose study, then spell; listen and spell with immediate feedback; or a bee rehearsal with results at the end. Choose 5, 10, 20 or 50 words, source set, category, tricky/starred words, or new 2027 additions.
- Word-level review intervals are 1, 3, 7, 14 and 30 days. Assisted attempts do not count as independent recall. A word becomes “secure” only after at least three independent recall days; quick repeats cannot simulate retention.
- Progress, unfinished sessions, notes and stars save locally in a separate IndexedDB database. Backup restore validates and merges records instead of clearing the journal.

See **PLAN.md** for the full design and learning decisions.

## What is in the bank

| Category | Distinct spellings | Explicitly new 2027 |
| --- | ---: | ---: |
| One Bee | 1,126 | 127 |
| Two Bee | 1,988 | 252 |
| Three Bee | 1,001 | 126 |
| Total | **4,115** | **505** |

The supplied [Hoover 206 page](https://hoover206.wixsite.com/spelling/copy-of-2025-words-1) links 92 Words of the Champions study decks with 2025, 2026 and 2027 titles. Its nine school-word decks are excluded. The page says repeated lists have not all been updated. Consequently, **4,115 is the deduplicated linked collection, not a verified official 2027 list**. The official Scripps guide has 4,000 words. See **SOURCE_AUDIT.md** and **data/manifest.json** for provenance.

Every word now has an explanation and a contextual example sentence: **4,115 of each**. Dictionary entries retain Wiktionary revision links and attribution. Short original study notes clarify rare words, forms, and meanings that did not fit the default dictionary sense. Original sentences were written for this journal; retained dictionary examples carry their own credit. Independent reviewers checked every word/example pair against the available study context, with focused reference checks for disputed facts. See **WORK_TRACKER.md**, **WORD_CHECKLIST.csv**, and **QA.md** for completion and review evidence.

**4,100** words have a recording reference whose filename matches the spelling. Recordings stream on request from their original public Google Drive source. This is not a claim that all recordings are playable or independently pronunciation-checked. The browser QA encountered unavailable source playback and verified the labelled computer-voice fallback. Use the original study card or a parent/pronouncer for unclear rare words. No audio library or study-slide illustrations are bundled. Short original explanations paraphrase factual meanings; the original slide prose and sentences are not copied.

## Content and credits

Made with 🐝 and 🩷 for Molly. Original site content © 2026 Emily, licensed under **CC BY-NC-SA 4.0**, with third-party exceptions described in [LICENSE](LICENSE). The website uses a warm honey-yellow palette.

- Source words/metadata: Hoover 206 study decks linked in the manifest. Each word retains its set and slide reference.
- Dictionary text: Wiktionary contributors, **CC BY-SA 4.0**. See **data/DICTIONARY_LICENSE.md** and per-entry source URLs; text is shortened and cleaned.
- Public recording references credit the original study recordings. Original media remains hosted by its source.
- The importer can inspect Molly’s existing school-site checkout as a read-only source of her own notes; the current new bank has no spelling overlap, so no old school-site explanations or recordings are bundled.

## Development and verification

The website has no runtime package dependencies. Development database tests use the pinned `fake-indexeddb` package; install development dependencies once with `npm install`. With Node 20+:

```sh
node --test tests/*.test.mjs
node scripts/validate-bank.mjs
node scripts/build-standalone.mjs
python3 -m unittest discover -s tests -p 'test_*.py'
```

The source import and dictionary import scripts are included for auditability. Their downloaded research caches and independent review evidence remain locally in the ignored `research/` folder and are excluded from publication. No further network import is needed to complete this bank. The raw example batches and research inputs remain only in the original local working folder; the public repository includes the final reviewed runtime data. In that maintained local folder, after any deliberate reimport, run `python3 scripts/apply-content-review.py`, `node scripts/merge-examples.mjs`, and the data checks to restore curated selections. `python3 scripts/update-progress.py` updates the tracker without changing study wording. Respect source rate limits and preserve provenance. Reconcile with the school’s official 2027 guide before claiming an exact current-season collection as the exact official current-season list.

See **QA.md** for checks completed and remaining limitations.
