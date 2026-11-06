# Local website verification

November 6, 2026. The new Words of the Champions journal is separate from Molly’s published school-word site and all AMC8 projects. The original local review preceded publication. The separate molly-champions-journal repository is used for the GitHub Pages release; existing projects remain unchanged.

## App stability — passed

An independent agent reviewed the application code and reproduced defects before and after fixes. The final checks cover audio fallback firing once, stalled source audio, stale playback callbacks, safe restored IDs, stale-tab actions, interrupted rehearsal recovery, and timer checkpoints that do not count hours away.

- **23 Node tests passed**: spelling variants/accents/punctuation, same-day recall limits, assisted/skipped attempts, review scheduling, dates/DST, category/source filters, daily queue caps, mixed learning/recall, clue concealment, two-client writes, backup validation and merge, stale actions, and refresh/timer recovery.
- **Five Python parser tests passed.**
- Data validation checks **4,115 distinct stable IDs, 4,115 explanations, 4,115 contextual examples**, attribution, clean text, exact standalone target forms, unique sentences, 92 source sets, and category counts 1,126 / 1,988 / 1,001. The manifest explicitly keeps `officialListVerified: false`.
- App and self-contained module syntax checked; the self-contained build includes all four data bundles and has no external JavaScript package dependency.

## Molly-style study review — passed

Root executed the actual Chrome UI at **http://127.0.0.1:5184/**, an isolated QA origin. A different agent reviewed the saved visible UI evidence and independently validated the downloaded backup with the app’s actual validator. This is a simulated Molly workflow, not a claim that Molly herself completed the test.

- Daily unseen words show spelling, explanation and sentence before the first assisted attempt. Hiding the card removes the answer; recall inputs disable spellcheck/autocorrect.
- Complete five-word study, five-word Two Bee spelling and five-word Three Bee rehearsal sessions passed. Correct, wrong, revealed, skipped and unanswered attempts are distinguished. Rehearsal answers and feedback stay hidden until results.
- A known-word independent correct attempt earned one independent recall and no premature secure status.
- Pause hides the answer form and freezes the clock. Reload/resume retains the exact typed draft. Multi-tab practice continues the existing queue; progress updates without duplicate credit.
- One/Two/Three Bee home entries, library totals and practice selection passed. Empty search gives a safe disabled practice action.
- Notes containing literal angle brackets and stars persist after reload. A newer note survives restoring an older backup.
- The actual downloaded backup contained 18 distinct word records, five completed sessions and 19 responses/attempts. An independent validator confirmed all counts and metadata. Browser restore rejected malformed and wrong-kind JSON, merged the valid downloaded text without doubling counts, and kept newer records. The pasted-text path and file picker share the same restore function.
- Meaning, origin and sentence clues conceal target spellings, including danzon/danzón, Gruyere/Gruyères, da capo and princeps. An independent full-bank scan found zero remaining canonical/accepted spellings in masked example, meaning and origin fields.
- Hear and Slow replay produced the labelled computer-voice fallback when source audio failed. Missing audio has a study/skip route and is not automatically graded wrong.
- Keyboard skip navigation focuses the main content; dialogs have a dynamic accessible name. Home, practice, library, progress, settings and sources have no horizontal document overflow at 320 and 768 CSS pixels; the 375-pixel phone view and normal desktop view were visually inspected. This is not a physical-device certification.
- The standalone HTML rendered over HTTP with all 4,115 words. Final saved-folder preview on port5182 opened with zero QA attempts, confirming separate browser storage. No app console errors were observed in the inspected packaged-app view.

## Explanation and example review — passed

The 4,115 pairs are partitioned without overlap: 603 retained-dictionary candidates, 1,171 original part1, 1,171 original part2, and 1,170 original part3. Each was read by an agent who did not author that example, alongside the displayed explanation and available study context. Part3 was independently split600/570. A further grammar-label pass covered all partitions. Another agent independently checked all 292 newly written editorial replacements for meaning, facts, grammar and suitability; that review passed with no findings. See the final completion state in `WORK_TRACKER.md`.

Corrections address wrong default senses, circular form descriptions, scientific-notation corruption, inappropriate imported examples, target inflections, unclear sentences and mismatched parts of speech. Focused primary-source checks resolved unusual senses and source errors; examples include minnelied as a song, myocommata as partitions, frijolillo’s broader plant meaning, and the distinct DNA-transcription meaning of terminator. Source discrepancies are recorded rather than silently copied. Retained Wiktionary text has revision-level credits; original short explanations and sentences are labelled.

Local evidence is saved in the ignored `research/` folder: independent stability report, Molly acceptance/evidence review, downloaded-backup validation, licensed content/POS reviews, original-example cross-reviews, keyed corrections and closure reports. `WORD_CHECKLIST.csv` and `PROGRESS_LOG.jsonl` provide per-word coverage and durable checkpoints.

## Remaining source and platform limits

- The supplied source combines 2025/2026/2027 decks. These **4,115 linked spellings are not a reconciled official 4,000-word 2027 guide**. Current-season additions and carryovers remain labelled.
- 4,100 recording filenames match the spelling, but not every source recording is playable or independently pronunciation-checked. Browser source playback failed for tested Google files; the labelled computer voice worked. Use the source study or a parent/pronouncer for unclear rare words. Original recordings are not bundled.
- The browser file picker requires a local-file extension permission that was not changed. Full restore was exercised through the pasted contents of the actual downloaded backup, using the shared restore function.
- Direct `file://` preview was blocked by browser policy; local-file storage is not verified. Use **Start Word Journal.command** and the tested fixed address **http://127.0.0.1:5182/**.
- Progress is local to a browser profile and origin, with no cloud account. Download backups before changing browser/device/address. Keep using port5182 for Molly; QA progress on port5184 is separate.
