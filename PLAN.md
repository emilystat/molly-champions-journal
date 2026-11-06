# Molly’s Words of the Champions — local-first plan

Prepared November 6, 2026. This is a new project. The school-word site at
https://emilystat.github.io/molly-spelling-bee/ is a read-only reference and will not be edited or redeployed.

## 1. Start with an honest word bank

The supplied Hoover page is the **2027 season** page. Scripps describes the official annual guide as **4,000 words**, rather than “more than 4,000.” Accepted variants and an older-source practice collection can produce a larger count.

The Hoover page separates new 2027 words from repeated lists, and explicitly says the repeated lists have not been updated. Import the publicly linked **study** slideshows, record the title/year/set/level and individual slide for every word, deduplicate spellings, and report gaps. Do not claim that this mixed collection is an exact, verified 2027 list. Clearly distinguish current-season additions from carryover practice. Leave a path to reconcile against the school’s official 2027 guide later.

Store only word spellings and factual metadata from the decks. Link back to the original slide for its definitions, examples, pictures and recordings. Reuse Molly’s own existing word explanations and properly credited recordings only when the spelling matches. Do not invent definitions, origins or pronunciations to fill gaps.

## 2. Make 4,000 words feel manageable

The home page should answer: “What should I do today?” It should show a short daily mix, reviews due, new words left today, and overall coverage. It should not open with thousands of rows.

Molly’s bee is in **late January 2027**. Use **January 25 only as an adjustable planning estimate**, not a confirmed event date. There are roughly 80 days from November 6: full coverage of 4,115 words would need about 52 new spellings per day before reviews, which is a substantial workload.

Default to the **505 explicitly new 2027 words first**, with 10 new words plus up to 20 due reviews. A first pass takes about 51 days, leaving several weeks for return visits. Review due words from any category even if the new-word path is narrower. Then expand to the 2027-titled repeat sets or the whole collection based on Molly’s familiarity and the teacher’s guidance. Keep all 4,115 spellings available in custom practice.

Keep **One Bee (1,126), Two Bee (1,988), and Three Bee (1,001)** visible as separate categories on the home page, practice selector, library, word cards, daily learning ceiling and progress. The explicitly new 2027 subset contains 127 / 252 / 126 in those categories. These are counts from the linked mixed-year collection, not official annual category totals.

 Make the new-word budget and session length adjustable. A target bee date can show a **first-pass** workload estimate; it is not a guarantee of long-term mastery. At 10 new words/day, 4,000 words take about 400 days before allowing for reviews. Larger goals must make that tradeoff visible.

## 3. Separate learning from recall

- **Daily practice:** a balanced, reproducible set of due reviews and unseen words; save and resume it.
- **Learn a small batch:** reveal a word card, listen, notice a tricky part, then hide it and spell it. Seeing an answer does not earn an independent-recall success.
- **Listen and spell:** keep the answer, spelling-revealing labels and external dictionary links hidden until checking or explicitly revealing the answer. Use spellcheck/autocorrect off.
- **My tricky words:** automatically collect misses; optionally star words Molly wants to revisit.
- **Choose a set:** filter by level, source set or current-season additions. Offer 5, 10, 20 or 50 words.
- **Bee rehearsal:** a fixed set with feedback held until the end; show the actual results without punishing one miss by ending the session.
- **Browse:** search the entire bank, open a word card, view source, and start a focused session.

## 4. Review individual words over time

Track each word separately: encounters, independent correct recalls, misses, last practice day, next due day, review stage, star and a small optional personal note. Use review intervals of 1, 3, 7, 14 and 30 days after successive independent recall days. A mistake returns the word to early review. A correct response on the same day cannot repeatedly promote it. A revealed answer is assisted practice. Keep “seen,” “learning,” “review due,” and “secure recall” distinct. A word is secure only after several successful recalls on different days, never after one lucky answer or reading a card.

Do not require every overdue word to be completed before starting. Cap the daily queue and explain that the rest will appear in future sessions. Use local calendar days consistently across daylight-saving changes.

## 5. Treat pronunciation as a learning requirement

Prefer an exact-match recording with its source/license when available; otherwise clearly label the device’s computer voice. Give a slower replay, a voice selector, and a direct link to the word’s Hoover study slide for checking pronunciation. Never substitute a recording of a similarly spelled word. Avoid automatic bulk lookups for 4,000 words. If audio fails, explain it and provide a parent/pronouncer or source-study route; never grade silence as a spelling mistake.

November 6 completion: all 4,115 explanations and contextual sentences are present. Independent review covers meaning, example usage and grammar labels. Independently verified recorded pronunciation for every rare word remains outside this local version’s completed content scope.

## 6. Protect months of work

This version is for Molly on one device, with no accounts, Supabase, email service or paid API. GitHub Pages hosts the static website; progress remains on the device. Use a unique storage namespace unrelated to the school spelling site or AMC sites. Persist after meaningful actions, not every timer tick. Save the active session, queue order, answers and progress. Provide a dated JSON backup and validated merge restore; reject malformed files before changing data. Show storage failures visibly and allow a backup. Opening the same project in two tabs must not silently replace newer progress.

Local/browser progress does not follow Molly to a different device automatically. Backups are the supported transfer path for this version.

## 7. Visual and interaction direction

A calm personal word journal: warm paper, deep ink, muted lavender and honey accents, clear typography, a small illustrated bee and generous spacing. Use a compact navigation: Today, Practice, Word library, My progress, Settings. Keep the daily action prominent. Provide keyboard operation, visible focus, clear feedback, minimum touch targets and a narrow-screen layout. Avoid competitive leaderboards, public profiles and pressure-based streak penalties.

## 8. Local implementation and checks

Use a small static site with ES modules, no framework dependency or backend. Bundle the word bank, source manifest and audited reuse of Molly’s own metadata. Keep the importer, data-validation report and tests with the project. Keep downloaded source HTML out of the deliverable/git history.

Test meaningful behavior: filtering/deduplication and stable IDs; accent/variant and punctuation answer checking; one result per question; assisted/same-day review scheduling; session resume; safe backup restore; multiple-tab conflict handling; empty queues; corrupt storage; responsive layout; keyboard use; audio failure/fallback. Verify an actual local browser learning session, a recall test, the source links, progress after reload, backup/restore and phone layout.

Deliver a separate persistent local folder, a local preview, an import audit and clear instructions. Publication was requested after local completion: use the separate molly-champions-journal repository.

## Sources

- User’s source index: https://hoover206.wixsite.com/spelling/copy-of-2025-words-1
- Scripps description: https://www.spellingbee.com/faq/what-words-champions
- Existing personal site: https://emilystat.github.io/molly-spelling-bee/
