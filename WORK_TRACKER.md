# Molly’s Word Journal — work tracker

Last checkpoint: 2026-11-06T14:57:40.987787+00:00

State: **complete-reviewed**. Counts below come from the saved records.

| Category | Explanations | Examples | Words |
| --- | ---: | ---: | ---: |
| One Bee | 1126 | 1126 | 1126 |
| Two Bee | 1988 | 1988 | 1988 |
| Three Bee | 1001 | 1001 | 1001 |

All **4,115 explanations** and **4,115 example sentences** are saved. All **505 explicitly new 2027 words** are included. Stable IDs preserve existing progress.

## Review checkpoints

- **Stability: passed**. Independent code review closed audio retries, quiz recovery, timer recovery, backup validation, clue masking and stale-tab issues. 23 Node tests and 5 parser tests pass.
- **Molly: passed**. Actual Chrome study, spelling, rehearsal, daily cards, resume, notes/stars, categories, progress and backup flows reviewed independently from saved UI evidence and the downloaded backup.
- **Content: passed**. All 4,115 word/example pairs independently checked across complete partitions; grammar-label passes and a second semantic check of all292 replacement sentences passed. All findings are resolved.

## Files and safe continuation

- `WORD_CHECKLIST.csv`: one row per spelling, with source and completion status.
- `PROGRESS_LOG.jsonl`: durable import and review checkpoints.
- `data/study-notes.json` and `data/example-batches`: curated wording, with stable word IDs.
- `research/*review*.md` and keyed issue JSONs: independent review evidence and resolutions (local, ignored by Git).
- `scripts/apply-content-review.py`: reapplies saved corrections; `scripts/merge-examples.mjs`: merges and validates sentences; `scripts/update-progress.py`: recounts without rewriting content.
- Cached dictionary source batches remain in ignored `research/dictionary`. No new network import is needed. After any deliberate reimport, rerun the correction/merge scripts and data checks; the raw importer alone does not preserve all editorial choices.

## Scope and remaining source limitations

Published version: https://emilystat.github.io/molly-champions-journal/ . Molly’s existing websites are unchanged. This is the 4,115-word mixed-year linked collection, not a reconciled official 4,000-word 2027 list. Computer-voice fallback is labelled; referenced Google recordings and rare-word pronunciations have not all been independently verified. These source limitations are separate from completed explanation/example coverage.
