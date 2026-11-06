# GitHub Pages deployment

Repository: https://github.com/emilystat/molly-champions-journal
Website: https://emilystat.github.io/molly-champions-journal/

This is a static site served from the repository root. `.nojekyll` preserves the plain HTML, CSS, ES modules and JSON files without Jekyll conversion. Hash navigation and relative asset paths work under the repository subdirectory. No deployment secrets, account service or server database are required.

The production source is the default `codex/publish-champions-journal` branch, root folder. Push a reviewed update there to trigger the built-in GitHub Pages build.

Learner answers, notes, stars and unfinished practice stay in browser storage and are never part of Git commits or Pages builds. Source research caches, raw example batches, test progress, and development dependencies are ignored by Git. Final reviewed explanations and examples are included in `data/`.

The older spelling and Words of Champions repositories are separate and unchanged.
