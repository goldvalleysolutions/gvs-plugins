# gvs-plugins

The Gold Valley Solutions plugin marketplace: single-job "office worker" plugins for small offices, built to be installed by name on personal Claude accounts and other plugin-capable tools.

Plugins are plain files: instructions (skills), starter notes and fixtures. There is no server, nothing is sent anywhere by the plugins themselves, and what a plugin learns about your office is saved as text files in your own working folder.

**Status: early.** This repository is the marketplace skeleton. It lists no plugins yet. The planned order is Coordinator, then Inbox, Librarian and Bookkeeper. When a plugin is released it appears in the marketplace list below and installs as `<name>@goldvalleysolutions`, for example `coordinator@goldvalleysolutions`.

## Plugins

| Plugin | What it does | Status |
| --- | --- | --- |
| _none yet_ | | Coordinator is next |

## Install

### 1. Add the marketplace once, then install by name (recommended)

In Claude Code, from a terminal:

```bash
claude plugin marketplace add goldvalleysolutions/gvs-plugins
claude plugin install coordinator@goldvalleysolutions   # once Coordinator is listed
```

Or inside a Claude Code session:

```text
/plugin marketplace add goldvalleysolutions/gvs-plugins
/plugin install coordinator@goldvalleysolutions
```

The install id is the plugin name, an `@`, and the marketplace name (`goldvalleysolutions`). A plugin's skills then run as `/<plugin>:<skill>`, for example `/coordinator:setup`.

On claude.ai or the Claude desktop app: open **Customize > Plugins**, choose **Add > Add marketplace**, and enter `goldvalleysolutions/gvs-plugins`. Then pick a plugin from the list and select **Add**.

### 2. Install one plugin from a folder

Each plugin folder is self-contained, so you can use one without the marketplace.

- Claude Code, for one session: `claude --plugin-dir ./plugins/<name>`
- Cursor: copy the folder to `~/.cursor/plugins/local/<name>`, then restart Cursor or run **Developer: Reload Window**.

### 3. Upload a zip

On claude.ai or the Claude desktop app: zip a plugin folder (either the folder itself or its contents), then use **Customize > Plugins > Add > Upload plugin** and choose the `.zip` (or `.plugin`) file. The archive must hold exactly one `.claude-plugin/plugin.json`.

## What works on which Claude plan

Facts checked against Anthropic's documentation in November 2026. These limits are Anthropic's and can change.

- **Free:** plugins work for Gold Valley on a Claude Free account, where Customize > Plugins and plugin upload are available. Anthropic's help article "Use plugins in Claude" currently says plugins are available on paid plans, and its directory is a paid-plan surface, so check **Customize > Plugins** on your own account. We distribute through this marketplace and zip upload for that reason, not through Anthropic's directory.
- **Free limits that matter:** one custom connector, and no scheduled tasks. These plugins keep their notes in local files and do not need a custom connector.
- **Scheduled tasks** (for example a morning "needs you" list) need Pro or higher. On Free you ask by hand.
- **Claude Code** works with a plugin from this marketplace as shown above.
- Plugins that only contain skills and notes, like the ones planned here, load in chat. Hooks and sub-agents run in Cowork and Claude Code, not in chat.

## Other tools

Each plugin keeps one source tree and thin manifests for each tool. Formats are still moving, so treat the lines below as what the docs say today, not as a promise.

| Tool | Manifest in this repo | Docs |
| --- | --- | --- |
| Claude Code and claude.ai | `.claude-plugin/marketplace.json`, `<plugin>/.claude-plugin/plugin.json` | https://code.claude.com/docs/en/plugins/marketplace-reference, https://code.claude.com/docs/en/plugins/manifest-reference |
| Cursor | `.cursor-plugin/marketplace.json`, `<plugin>/.cursor-plugin/plugin.json` | https://cursor.com/docs/plugins, https://cursor.com/docs/reference/plugins |
| Agent Plugins (portable; ChatGPT and Codex) | `<plugin>/plugin.json` | https://agent-plugins.org/plugin-authors/manifest, https://developers.openai.com/plugins/build/plugins |

Known gaps, so nobody is surprised:

- **Cursor marketplace:** Cursor documents `.cursor-plugin/marketplace.json` for multi-plugin repositories, but installing from a third-party GitHub marketplace in Cursor may need a team plan or a listing in the Cursor Marketplace. We have not tested it and have not submitted anything. Installing one plugin from a local folder is documented and is the safe path.
- **Codex and ChatGPT:** the root `plugin.json` is the portable Agent Plugins manifest and should load there. OpenAI also describes its own marketplace catalog file at `.agents/plugins/marketplace.json`. This repo does not ship one yet. Untested.
- Only the Claude Code flow is exercised end to end today (see below).

## Check your work

```bash
python3 scripts/validate.py                  # our checks, plus `claude plugin validate` if the CLI is installed
python3 scripts/validate.py --require-cli    # fail instead of skip when the claude CLI is missing
python3 -m unittest discover -s tests -v     # tests for the validator
```

The validator checks both marketplace files, then every folder in `plugins/` and `templates/plugin`: the three manifests agree on name, version and description, every referenced path exists, and every skill has frontmatter. It exits nonzero on any problem and prints a `SKIPPED` line, never a silent pass, when the `claude` CLI is not available. Install the CLI with `npm install -g @anthropic-ai/claude-code` (no login is needed to validate).

## Repository layout

```
.claude-plugin/marketplace.json   Claude Code marketplace catalog
.cursor-plugin/marketplace.json   Cursor marketplace catalog
plugins/<name>/                   one folder per plugin, installable on its own
templates/plugin/                 starter for a new plugin
scripts/validate.py               validator
tests/                            validator tests and fixtures
```

See [CONTRIBUTING.md](CONTRIBUTING.md) to add or change a plugin. Licensed under the [MIT License](LICENSE).
