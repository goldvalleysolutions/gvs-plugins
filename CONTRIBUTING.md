# Contributing

Thanks for helping. This repository is a plugin marketplace; every change goes through a pull request.

## Branches

- `main` is the released marketplace. Only the maintainers merge to `main`.
- `test` is where work lands first. Open pull requests against `test`.
- Make your change on a short-lived branch, open a pull request into `test`, and delete the branch after it merges.

## Add a plugin

1. Copy `templates/plugin/` to `plugins/<name>`. Names are lowercase kebab-case, for example `coordinator`.
2. Keep one source tree. Write skills once under `skills/<skill-name>/SKILL.md`. The three manifests (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, root `plugin.json`) stay thin and must agree on `name`, `version` and `description`.
3. Every `SKILL.md` starts with frontmatter containing `name` (equal to its folder name) and `description` (what it does and when to use it, up to 1024 characters).
4. Add the plugin to **both** `.claude-plugin/marketplace.json` (`"source": "./plugins/<name>"`) and `.cursor-plugin/marketplace.json` (`"source": "plugins/<name>"`). The entry name must equal the plugin's manifest name.
5. Give the plugin a README (install, setup, what it does, what it will not do) and a CHANGELOG. Use semantic versions.
6. Run the checks below.

## Check before you push

```bash
python3 scripts/validate.py --require-cli
python3 -m unittest discover -s tests -v
```

`--require-cli` needs the `claude` CLI (`npm install -g @anthropic-ai/claude-code`; no login needed). Without it the validator still runs its own checks and prints a SKIPPED line for the CLI step. The same checks run on every pull request.

## Ground rules

- Plugins are plain files. No paid services, no secrets, no real client or office data. Memory templates and eval fixtures hold invented examples only.
- Anything that sends, posts or pays must wait for an explicit yes from the user in chat. Plugins draft; people approve.
- Plugin files are read-only at runtime. A plugin saves what it learns in the user's own working folder, never inside the plugin folder.
- Do not claim more than the docs say. Plugin formats on each tool are still moving: cite the doc URL for any manifest field you rely on, and say so in the pull request when something is a gap.
- Do not add a plugin to a marketplace listing outside this repository, or publish one anywhere, without the maintainers' approval.

To report a security issue, see [SECURITY.md](SECURITY.md). Do not open a public issue for it.

## License

By contributing you agree your contribution is licensed under the [MIT License](LICENSE).
