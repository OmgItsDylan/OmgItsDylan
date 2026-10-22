# OmgItsDylan profile README

## One commit only

This repo always has exactly one commit on `main`. Never add a second one.

To publish a change (a card refresh, a code change, anything), fold it into the existing commit and force-push:

```bash
git add -A
git commit --amend --no-edit
git push --force-with-lease origin main
```

The commit message stays `Profile README with generated cards`.
