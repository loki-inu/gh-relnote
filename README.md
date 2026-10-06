# gh-relnote

A [GitHub CLI](https://cli.github.com/) extension that turns your conventional commits into a GitHub Release body, from local git history. No API calls to build the notes, no config file.

```bash
gh extension install loki-inu/gh-relnote
gh relnote
```

```markdown
## What's changed

### Features

- **cli:** add sync (`b22b22b`) — Ada Lovelace

### Fixes

- handle commas in tags (`d44d44d`) — Ada Lovelace

---

Range: `v1.0.0` → `HEAD`.
```

(Synthetic example.)

## Create a release with the notes

```bash
gh relnote create v1.3.0 --draft
gh relnote create v1.3.0 --title "v1.3.0" -- --no-bots --max 50
```

`create` runs relnote for latest tag → `HEAD`, then calls `gh release create TAG ... --notes-file <notes>`. Everything before `--` goes to `gh release create` (`--draft`, `--prerelease`, `--title`, `--target`, asset files). Everything after `--` goes to relnote.

## Print notes only

```bash
gh relnote                          # latest tag → HEAD
gh relnote --since v1.2.0 --no-bots
gh relnote --output notes.md --quiet
gh relnote --help                   # every flag
```

Grouping follows Conventional Commits: `feat` → Features, `fix` → Fixes, `type!` or `BREAKING CHANGE` → Breaking, everything else → Other. Merge commits are skipped by default, `--no-bots` drops dependabot and renovate, and subjects that look like tokens or keys are never printed.

## vs `gh release create --generate-notes`

`--generate-notes` builds notes from merged pull requests on GitHub. `gh relnote` builds them from commit messages in your clone, grouped by commit type, so it works for direct-to-main repos, offline, and before you push.

## Requirements

`gh`, `git`, and Python 3.11+ on `PATH` (stdlib only). Set `PYTHON=/path/to/python3` to pick an interpreter.

## How it works

This extension bundles [relnote](https://github.com/loki-inu/relnote) (v0.1.5), a zero-dependency Python CLI that's also available as a GitHub Action. Use relnote directly if you don't use `gh`.

## License

MIT
